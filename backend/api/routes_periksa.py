"""Route: memeriksa langkah, membuka petunjuk, menyelesaikan misi, refleksi."""

from __future__ import annotations

import json

from flask import Blueprint, jsonify

from segitiga import bank_soal
from segitiga.penilai import (
    BATAS_PERCOBAAN,
    TINGKAT_PETUNJUK_MAKS,
    hitung_skor_misi,
    periksa_langkah,
)

from .umum import GalatApi, ambil_main, data_json, koneksi, sekarang, status_langkah

bp = Blueprint("periksa", __name__, url_prefix="/api")


def _misi_dan_langkah(main_row, no: str) -> tuple[dict, dict]:
    misi = bank_soal.ambil_misi(main_row["misi_id"])
    if misi is None:
        raise GalatApi("Misi tidak ditemukan.", 404)
    langkah = bank_soal.cari_langkah(misi, no)
    if langkah is None:
        raise GalatApi("Langkah tidak ditemukan.", 404)
    return misi, langkah


def _tingkat_sekarang(main_id: str, no: str) -> int:
    row = (
        koneksi()
        .execute(
            "SELECT MAX(tingkat) AS t FROM petunjuk_dibuka WHERE main_id = ? AND langkah = ?",
            (main_id, no),
        )
        .fetchone()
    )
    return int(row["t"] or 0)


def _buka_petunjuk(main_id: str, langkah: dict, sampai: int, otomatis: bool) -> list[dict]:
    """Catat petunjuk yang dibuka sampai tingkat tertentu; kembalikan yang baru dibuka."""
    conn = koneksi()
    dari = _tingkat_sekarang(main_id, langkah["no"]) + 1
    baru = []
    for t in range(dari, sampai + 1):
        conn.execute(
            "INSERT OR IGNORE INTO petunjuk_dibuka (main_id, langkah, tingkat, otomatis, waktu) "
            "VALUES (?, ?, ?, ?, ?)",
            (main_id, langkah["no"], t, int(otomatis), sekarang()),
        )
        baru.append({"tingkat": t, "teks": langkah["petunjuk"][t - 1]})
    return baru


@bp.post("/periksa")
def periksa():
    data = data_json()
    main = ambil_main(data.get("main_id"))
    if main["selesai"]:
        raise GalatApi("Misi ini sudah selesai. Mulai lagi untuk mengulang.")
    no = str(data.get("langkah") or "")
    _, langkah = _misi_dan_langkah(main, no)
    conn = koneksi()

    sudah_benar = conn.execute(
        "SELECT 1 FROM jawaban_langkah WHERE main_id = ? AND langkah = ? AND benar = 1",
        (main["id"], no),
    ).fetchone()
    if sudah_benar:
        return jsonify(
            {
                "benar": True,
                "kode_diagnosis": None,
                "umpan_balik": langkah["penjelasan_benar"],
                "boleh_lanjut": True,
                "tingkat_petunjuk": _tingkat_sekarang(main["id"], no),
                "petunjuk_baru": [],
            }
        )

    jawaban = data.get("jawaban")
    hasil = periksa_langkah(langkah, jawaban if isinstance(jawaban, dict) else {})

    # Jawaban kosong / format salah tidak dihitung sebagai percobaan.
    dihitung = hasil.kode not in {"KOSONG", "FORMAT_ANGKA"}
    percobaan_salah = conn.execute(
        "SELECT COUNT(*) AS n FROM jawaban_langkah WHERE main_id = ? AND langkah = ? AND benar = 0",
        (main["id"], no),
    ).fetchone()["n"]
    if dihitung:
        conn.execute(
            "INSERT INTO jawaban_langkah "
            "(main_id, langkah, percobaan_ke, jawaban, benar, kode_diagnosis, waktu) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                main["id"],
                no,
                percobaan_salah + 1,
                json.dumps(jawaban, ensure_ascii=False)[:2000],
                int(hasil.benar),
                hasil.kode,
                sekarang(),
            ),
        )
        if not hasil.benar:
            percobaan_salah += 1

    umpan_balik = hasil.umpan_balik
    petunjuk_baru: list[dict] = []
    if not hasil.benar and percobaan_salah >= BATAS_PERCOBAAN:
        petunjuk_baru = _buka_petunjuk(main["id"], langkah, TINGKAT_PETUNJUK_MAKS, otomatis=True)
        if petunjuk_baru:
            umpan_balik += " Kamu sudah mencoba 3 kali. Yuk, lihat cara lengkapnya di petunjuk."
    conn.commit()

    tingkat = _tingkat_sekarang(main["id"], no)
    return jsonify(
        {
            "benar": hasil.benar,
            "kode_diagnosis": hasil.kode,
            "umpan_balik": umpan_balik,
            "boleh_lanjut": hasil.benar or tingkat >= TINGKAT_PETUNJUK_MAKS,
            "tingkat_petunjuk": tingkat,
            "petunjuk_baru": petunjuk_baru,
        }
    )


@bp.post("/petunjuk")
def petunjuk():
    data = data_json()
    main = ambil_main(data.get("main_id"))
    if main["selesai"]:
        raise GalatApi("Misi ini sudah selesai.")
    no = str(data.get("langkah") or "")
    _, langkah = _misi_dan_langkah(main, no)
    st = status_langkah(main["id"]).get(no)
    if st and st.benar:
        raise GalatApi("Langkah ini sudah benar.")
    tingkat = _tingkat_sekarang(main["id"], no)
    if tingkat >= TINGKAT_PETUNJUK_MAKS:
        raise GalatApi("Semua petunjuk sudah dibuka.")
    baru = _buka_petunjuk(main["id"], langkah, tingkat + 1, otomatis=False)
    koneksi().commit()
    return jsonify(
        {
            "petunjuk_baru": baru,
            "tingkat_petunjuk": tingkat + 1,
            "boleh_lanjut": tingkat + 1 >= TINGKAT_PETUNJUK_MAKS,
        }
    )


@bp.post("/misi/selesai")
def selesai():
    data = data_json()
    main = ambil_main(data.get("main_id"))
    misi = bank_soal.ambil_misi(main["misi_id"])
    assert misi is not None
    status = status_langkah(main["id"])

    belum = [
        lk["no"]
        for lk in misi["langkah"]
        if not (
            status.get(lk["no"])
            and (status[lk["no"]].benar or status[lk["no"]].tingkat_petunjuk >= 3)
        )
    ]
    if belum:
        raise GalatApi(f"Masih ada langkah yang belum selesai: {', '.join(belum)}.")

    skor = hitung_skor_misi(misi, status)
    conn = koneksi()
    if not main["selesai"]:
        conn.execute(
            "UPDATE main_misi SET selesai = ?, skor_rubrik = ?, rincian = ?, bintang = ?, "
            "total_petunjuk = ? WHERE id = ?",
            (
                sekarang(),
                skor.skor,
                json.dumps(skor.rincian),
                skor.bintang,
                skor.total_petunjuk,
                main["id"],
            ),
        )
        conn.commit()

    ringkasan = [
        {
            "no": lk["no"],
            "judul": lk.get("judul", ""),
            "instruksi": lk["instruksi"],
            "penjelasan": lk["penjelasan_benar"],
            "dapat_skor": bool(status[lk["no"]].benar and status[lk["no"]].tingkat_petunjuk < 3),
        }
        for lk in misi["langkah"]
    ]
    return jsonify(
        {
            "skor": skor.skor,
            "maks": skor.maks,
            "rincian": skor.rincian,
            "bintang": skor.bintang,
            "total_petunjuk": skor.total_petunjuk,
            "lencana": misi["lencana"] if skor.skor >= 4 else None,
            "ringkasan": ringkasan,
        }
    )


@bp.post("/refleksi")
def refleksi():
    data = data_json()
    main = ambil_main(data.get("main_id"))
    teks = str(data.get("teks") or "").strip()[:1000]
    if teks:
        koneksi().execute(
            "INSERT INTO refleksi (main_id, teks, waktu) VALUES (?, ?, ?)",
            (main["id"], teks, sekarang()),
        )
        koneksi().commit()
    return jsonify({"tersimpan": bool(teks)})
