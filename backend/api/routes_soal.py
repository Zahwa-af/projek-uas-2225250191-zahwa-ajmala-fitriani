"""Route: daftar misi, isi misi, memulai misi, dan latihan."""

from __future__ import annotations

import random
import uuid

from flask import Blueprint, current_app, jsonify, request

from segitiga import bank_soal, fading, generator_soal
from segitiga.penilai import periksa_langkah

from .umum import GalatApi, data_json, koneksi, sekarang

bp = Blueprint("soal", __name__, url_prefix="/api")


def _skor_terbaik(sesi_id: str) -> dict[int, dict]:
    rows = koneksi().execute(
        "SELECT misi_id, MAX(skor_rubrik) AS skor, MAX(bintang) AS bintang "
        "FROM main_misi WHERE sesi_id = ? AND selesai IS NOT NULL GROUP BY misi_id",
        (sesi_id,),
    )

    return {
        r["misi_id"]: {
            "skor": r["skor"],
            "bintang": r["bintang"],
        }
        for r in rows
    }


def daftar_misi_dengan_status(sesi_id: str | None) -> list[dict]:
    terbaik = _skor_terbaik(sesi_id) if sesi_id else {}
    bebas = current_app.config.get("MISI_BEBAS", False)

    hasil = []
    sebelumnya_selesai = True

    for m in bank_soal.semua_misi():
        st = terbaik.get(m["id"])

        hasil.append(
            {
                "id": m["id"],
                "judul": m["judul"],
                "indikator": m["indikator"],
                "indikator_singkat": m["indikator_singkat"],
                "lencana": m["lencana"],
                "selesai": st is not None,
                "skor": st["skor"] if st else None,
                "bintang": st["bintang"] if st else 0,
                "maks": 6,
                "terbuka": bebas or sebelumnya_selesai,
            }
        )

        sebelumnya_selesai = st is not None

    return hasil


@bp.get("/misi")
def daftar_misi():
    return jsonify(daftar_misi_dengan_status(request.args.get("sesi_id")))


@bp.get("/misi/<int:misi_id>")
def isi_misi(misi_id: int):
    misi = bank_soal.ambil_misi(misi_id)

    if misi is None:
        raise GalatApi("Misi tidak ditemukan.", 404)

    return jsonify(bank_soal.misi_publik(misi))


@bp.post("/misi/<int:misi_id>/mulai")
def mulai_misi(misi_id: int):
    data = data_json()
    sesi_id = str(data.get("sesi_id") or "")
    conn = koneksi()

    if (
        conn.execute(
            "SELECT 1 FROM sesi WHERE id = ?",
            (sesi_id,),
        ).fetchone()
        is None
    ):
        raise GalatApi("Sesi tidak ditemukan. Masukkan namamu lagi.", 404)

    status = next(
        (m for m in daftar_misi_dengan_status(sesi_id) if m["id"] == misi_id),
        None,
    )

    if status is None:
        raise GalatApi("Misi tidak ditemukan.", 404)

    if not status["terbuka"]:
        raise GalatApi("Selesaikan misi sebelumnya dulu.", 403)

    main_id = uuid.uuid4().hex[:16]

    conn.execute(
        "INSERT INTO main_misi (id, sesi_id, misi_id, mulai) " "VALUES (?, ?, ?, ?)",
        (main_id, sesi_id, misi_id, sekarang()),
    )

    conn.commit()

    return jsonify({"main_id": main_id})


# ------------------------------------------------------------------
# LATIHAN PILAH
# ------------------------------------------------------------------


@bp.get("/latihan/pilah")
def latihan_pilah():
    return jsonify([bank_soal.saring_rahasia(s) for s in bank_soal.latihan()["pilah"]])


@bp.post("/latihan/pilah/periksa")
def periksa_latihan_pilah():
    data = data_json()

    soal = next(
        (s for s in bank_soal.latihan()["pilah"] if s["id"] == data.get("soal_id")),
        None,
    )

    if soal is None:
        raise GalatApi("Soal latihan tidak ditemukan.", 404)

    hasil = periksa_langkah(
        soal,
        {"penempatan": data.get("penempatan") or {}},
    )

    return jsonify(
        {
            "benar": hasil.benar,
            "kode": hasil.kode,
            "umpan_balik": hasil.umpan_balik,
        }
    )


# ------------------------------------------------------------------
# LATIHAN TINGGI SEGITIGA
# ------------------------------------------------------------------


@bp.get("/latihan/tinggi")
def latihan_tinggi():
    seed = request.args.get("seed", type=int)

    if seed is None:
        seed = random.randint(1, 1_000_000)

    soal = generator_soal.buat_soal_tinggi(seed)

    return jsonify(generator_soal.soal_tinggi_publik(soal))


@bp.post("/latihan/tinggi/periksa")
def periksa_latihan_tinggi():
    data = data_json()

    try:
        seed = int(data.get("seed"))
    except (TypeError, ValueError) as e:
        raise GalatApi("Soal tidak valid.") from e

    return jsonify(
        generator_soal.periksa_soal_tinggi(
            seed,
            str(data.get("pilihan") or ""),
        )
    )


# ------------------------------------------------------------------
# LATIHAN SOAL CERITA BERTAHAP (fading, tanpa skor) — Tahap 2C
# ------------------------------------------------------------------


def _seed_tingkat(data: dict) -> tuple[int, int]:
    try:
        seed = int(data.get("seed"))
    except (TypeError, ValueError) as e:
        raise GalatApi("Soal tidak valid.") from e
    return seed, fading.normalkan_tingkat(data.get("tingkat"))


@bp.get("/latihan/bertahap")
def latihan_bertahap():
    seed = request.args.get("seed", type=int)
    if seed is None:
        seed = random.randint(1, 1_000_000)
    return jsonify(fading.soal_publik(seed, request.args.get("tingkat")))


@bp.post("/latihan/bertahap/periksa")
def periksa_latihan_bertahap():
    data = data_json()
    seed, tingkat = _seed_tingkat(data)
    jawaban = data.get("jawaban")
    if not isinstance(jawaban, dict):
        raise GalatApi("Jawaban tidak valid.")
    try:
        hasil = fading.periksa(seed, tingkat, str(data.get("isian") or ""), jawaban)
    except ValueError as e:
        raise GalatApi(str(e)) from e
    return jsonify({"benar": hasil.benar, "kode": hasil.kode, "umpan_balik": hasil.umpan_balik})


@bp.post("/latihan/bertahap/petunjuk")
def petunjuk_latihan_bertahap():
    data = data_json()
    seed, tingkat = _seed_tingkat(data)
    try:
        return jsonify(fading.petunjuk(seed, tingkat, str(data.get("isian") or ""), data.get("ke")))
    except ValueError as e:
        raise GalatApi(str(e)) from e


@bp.post("/latihan/bertahap/selesai")
def selesai_latihan_bertahap():
    """Keputusan fading untuk soal berikutnya + pertanyaan penjelasan diri. Tidak disimpan."""
    data = data_json()
    seed, tingkat = _seed_tingkat(data)
    try:
        salah = int(data.get("salah") or 0)
        petunjuk = int(data.get("petunjuk") or 0)
    except (TypeError, ValueError) as e:
        raise GalatApi("Data latihan tidak valid.") from e
    k = fading.tingkat_berikut(tingkat, salah, petunjuk)
    return jsonify(
        {
            "tingkat_berikut": k.tingkat,
            "arah": k.arah,
            "pesan": k.pesan,
            "refleksi": fading.refleksi(seed, tingkat),
        }
    )
