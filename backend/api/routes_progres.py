"""Route: sesi siswa, progres, dan rekap guru."""

from __future__ import annotations

import hmac
import uuid
from collections import Counter

from flask import Blueprint, current_app, jsonify

from segitiga import bank_soal, rmt
from segitiga.penilai import kategori_literasi

from .keamanan import catat_pin_salah, pin_terkunci
from .routes_soal import daftar_misi_dengan_status
from .umum import GalatApi, data_json, koneksi, sekarang, teks_wajib

bp = Blueprint("progres", __name__, url_prefix="/api")


@bp.post("/sesi")
def buat_sesi():
    data = data_json()
    nama = teks_wajib(data, "nama_panggilan", "Nama panggilan", 30)
    kelas = teks_wajib(data, "kode_kelas", "Kode kelas", 20).upper()
    sesi_id = uuid.uuid4().hex[:12]
    conn = koneksi()
    conn.execute(
        "INSERT INTO sesi (id, nama_panggilan, kode_kelas, dibuat) VALUES (?, ?, ?, ?)",
        (sesi_id, nama, kelas, sekarang()),
    )
    conn.commit()
    return jsonify({"sesi_id": sesi_id, "nama_panggilan": nama, "kode_kelas": kelas})


@bp.get("/sesi/<sesi_id>")
def cek_sesi(sesi_id: str):
    row = koneksi().execute("SELECT * FROM sesi WHERE id = ?", (sesi_id,)).fetchone()
    if row is None:
        raise GalatApi("Sesi tidak ditemukan.", 404)
    return jsonify(
        {
            "sesi_id": row["id"],
            "nama_panggilan": row["nama_panggilan"],
            "kode_kelas": row["kode_kelas"],
        }
    )


@bp.get("/progres/<sesi_id>")
def progres(sesi_id: str):
    misi = daftar_misi_dengan_status(sesi_id)
    total = sum(m["skor"] or 0 for m in misi)
    return jsonify(
        {
            "misi": misi,
            "total": total,
            "maks": 6 * len(misi),
            "kategori": kategori_literasi(total) if any(m["selesai"] for m in misi) else None,
            "lencana": [m["lencana"] for m in misi if (m["skor"] or 0) >= 4],
        }
    )


@bp.post("/guru")
def rekap_guru():
    data = data_json()
    pin_benar = current_app.config.get("PIN_GURU")
    if not pin_benar:
        raise GalatApi("Halaman guru belum diaktifkan. Atur SEGIPINTAR_PIN_GURU di server.", 403)
    if pin_terkunci():
        raise GalatApi("Terlalu banyak PIN salah. Tunggu 15 menit, lalu coba lagi.", 429)
    if not hmac.compare_digest(str(data.get("pin") or ""), pin_benar):
        catat_pin_salah()
        raise GalatApi("PIN guru salah.", 403)
    kelas = teks_wajib(data, "kode_kelas", "Kode kelas", 20).upper()
    conn = koneksi()
    siswa = []
    for s in conn.execute(
        "SELECT * FROM sesi WHERE kode_kelas = ? ORDER BY nama_panggilan", (kelas,)
    ):
        misi = daftar_misi_dengan_status(s["id"])
        if not any(m["selesai"] for m in misi):
            continue
        total = sum(m["skor"] or 0 for m in misi)
        salah = conn.execute(
            "SELECT j.kode_diagnosis, j.langkah, m.misi_id FROM jawaban_langkah j "
            "JOIN main_misi m ON m.id = j.main_id "
            "WHERE m.sesi_id = ? AND j.benar = 0 AND j.kode_diagnosis IS NOT NULL",
            (s["id"],),
        ).fetchall()
        kode = Counter(r["kode_diagnosis"] for r in salah)
        # RMT Tahap 1: fase kognitif yang paling sering bermasalah (dihitung dari data lama).
        fase = Counter(
            f
            for r in salah
            if (f := rmt.fase_kesalahan(r["kode_diagnosis"], r["misi_id"], r["langkah"]))
        )
        petunjuk = conn.execute(
            "SELECT COUNT(*) AS n FROM petunjuk_dibuka p JOIN main_misi m ON m.id = p.main_id "
            "WHERE m.sesi_id = ?",
            (s["id"],),
        ).fetchone()["n"]
        refleksi = [
            r["teks"]
            for r in conn.execute(
                "SELECT r.teks FROM refleksi r JOIN main_misi m ON m.id = r.main_id "
                "WHERE m.sesi_id = ? ORDER BY r.waktu",
                (s["id"],),
            )
        ]
        siswa.append(
            {
                "nama_panggilan": s["nama_panggilan"],
                "skor_misi": [m["skor"] for m in misi],
                "total": total,
                "kategori": kategori_literasi(total),
                "petunjuk_dibuka": petunjuk,
                "kesalahan_terbanyak": [k for k, _ in kode.most_common(3)],
                "fase_kesulitan": {f: fase.get(f, 0) for f in rmt.SEMUA_FASE},
                "refleksi": refleksi,
            }
        )
    judul = [m["judul"] for m in bank_soal.semua_misi()]
    return jsonify({"kode_kelas": kelas, "judul_misi": judul, "siswa": siswa})
