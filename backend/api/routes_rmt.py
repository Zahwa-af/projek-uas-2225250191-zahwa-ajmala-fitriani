"""Route aktivitas pendamping RMT (Tahap 2A).

- GET  /api/rmt/misi/<id> : konten aktivitas tanpa kunci jawaban.
- POST /api/rmt/respons   : simpan respons siswa (atau "dilewati") dan beri umpan balik.

Tidak menulis ke tabel jawaban_langkah, petunjuk_dibuka, atau main_misi, sehingga skor
rubrik misi tidak berubah. Data disimpan dengan kode anonim; teks bebas disamarkan.
"""

from __future__ import annotations

import json

from flask import Blueprint, current_app, jsonify

from asisten.anonim import kode_anonim, samarkan
from segitiga import aktivitas_rmt

from .umum import GalatApi, ambil_main, data_json, koneksi, sekarang

bp = Blueprint("rmt", __name__, url_prefix="/api/rmt")

# Batas percobaan per aktivitas dalam satu main misi: mencegah penumpukan baris di database.
# Jauh di atas kebutuhan siswa (umumnya 1–5 kali).
MAKS_PERCOBAAN = 50


@bp.get("/misi/<int:misi_id>")
def konten_misi(misi_id: int):
    konten = aktivitas_rmt.ambil(misi_id)
    if konten is None:
        raise GalatApi("Aktivitas misi tidak ditemukan.", 404)
    return jsonify(aktivitas_rmt.publik(konten))


@bp.post("/respons")
def simpan_respons():
    data = data_json()
    main = ambil_main(data.get("main_id"))
    konten = aktivitas_rmt.ambil(main["misi_id"])
    aktivitas = (
        aktivitas_rmt.cari_aktivitas(konten, str(data.get("aktivitas") or "")) if konten else None
    )
    if aktivitas is None:
        raise GalatApi("Aktivitas tidak ditemukan.", 404)

    dilewati = data.get("dilewati") is True
    if dilewati:
        hasil = None
        jawaban_simpan = None
    else:
        try:
            hasil = aktivitas_rmt.periksa(aktivitas, data.get("jawaban"))
        except ValueError as e:
            raise GalatApi(str(e)) from None
        jawaban_simpan = dict(hasil.jawaban)
        if "teks" in jawaban_simpan:
            sesi = (
                koneksi()
                .execute("SELECT nama_panggilan FROM sesi WHERE id = ?", (main["sesi_id"],))
                .fetchone()
            )
            jawaban_simpan["teks"], _ = samarkan(
                jawaban_simpan["teks"], sesi["nama_panggilan"] if sesi else None
            )

    conn = koneksi()
    percobaan = conn.execute(
        "SELECT COUNT(*) AS n FROM aktivitas_rmt WHERE main_id = ? AND aktivitas = ?",
        (main["id"], aktivitas["id"]),
    ).fetchone()["n"]
    if percobaan >= MAKS_PERCOBAAN:
        raise GalatApi("Percobaan untuk aktivitas ini sudah terlalu banyak. Lanjutkan saja.", 429)
    conn.execute(
        "INSERT INTO aktivitas_rmt (main_id, kode_anonim, misi_id, aktivitas, tahap_rmt, "
        "percobaan_ke, jawaban, dilewati, benar, waktu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            main["id"],
            kode_anonim(main["sesi_id"], current_app.config["ASISTEN"].rahasia_anonim),
            main["misi_id"],
            aktivitas["id"],
            aktivitas["tahap"],
            percobaan + 1,
            json.dumps(jawaban_simpan, ensure_ascii=False) if jawaban_simpan else None,
            int(dilewati),
            None if hasil is None or hasil.benar is None else int(hasil.benar),
            sekarang(),
        ),
    )
    conn.commit()

    if hasil is None:
        return jsonify({"tercatat": True, "dilewati": True})
    return jsonify(
        {
            "tercatat": True,
            "dilewati": False,
            "benar": hasil.benar,
            "umpan_balik": hasil.umpan_balik,
            "penjelasan": hasil.penjelasan,
        }
    )
