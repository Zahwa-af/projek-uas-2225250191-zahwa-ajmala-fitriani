"""Route chatbot Pembimbing AI untuk beranda dan misi."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta

from flask import Blueprint, current_app, jsonify

from asisten.anonim import kode_anonim, samarkan
from asisten.klien import GalatLLM, HasilLLM, KlienLLM
from asisten.konfigurasi import KonfigurasiAsisten
from asisten.pengaman import larangan, menyuruh_siswa_menghitung, periksa_balasan
from asisten.prompt import StatusSiswa, susun_pesan, susun_pesan_beranda, tingkat_bantuan
from segitiga import bank_soal, rmt
from segitiga.penilai import periksa_langkah

from .umum import GalatApi, ambil_main, data_json, koneksi, sekarang, teks_wajib

bp = Blueprint("asisten", __name__, url_prefix="/api/asisten")

KUNCI_KLIEN = "segipintar_asisten_klien"

# Galat dari penyedia yang tidak akan hilang dengan mencoba ulang (permintaan salah, key
# ditolak, saldo habis, akses ditolak, model tidak ada, parameter salah).
GALAT_TETAP = {400, 401, 402, 403, 404, 422}

# Riwayat chatbot beranda yang ikut dikirim ke model hanya dari percakapan terkini.
RIWAYAT_BERANDA_MENIT = 60

# Dikirim (hanya ke model, tidak disimpan) bila balasan pertama menyuruh siswa menghitung.
PERMINTAAN_JAWAB_LANGSUNG = (
    "Aku tidak tahu caranya. Tolong langsung selesaikan sampai hasil akhir dengan susunan "
    "Diketahui, Rumus, Penyelesaian, dan Jadi. Jangan menyuruhku menghitung sendiri dan "
    "jangan mengakhiri dengan pertanyaan."
)


def _buang_contoh_tanya_balik(riwayat: list[dict[str, str]]) -> list[dict[str, str]]:
    """Buang pasangan (pertanyaan siswa + balasan) yang balasannya menyuruh siswa menghitung.

    Balasan seperti itu (dari instruksi lama atau model yang lemah) ditiru gayanya oleh
    model jika ikut dikirim sebagai riwayat. Khusus beranda; riwayat misi tidak disaring.
    """
    terakhir = max((i for i, p in enumerate(riwayat) if p["role"] == "assistant"), default=-1)
    hasil: list[dict[str, str]] = []
    for i, pesan in enumerate(riwayat):
        if pesan["role"] == "assistant" and menyuruh_siswa_menghitung(pesan["content"]):
            # Balasan terakhir: soalnya DIPERTAHANKAN, karena siswa mungkin sedang meminta
            # "coba kamu hitung" untuk soal itu. Pasangan yang lebih lama dibuang seluruhnya
            # agar soal lama tidak dijawab ulang.
            if i != terakhir and hasil and hasil[-1]["role"] == "user":
                hasil.pop()
            continue
        hasil.append(pesan)
    return hasil


def _konfig() -> KonfigurasiAsisten:
    return current_app.config["ASISTEN"]


def _klien() -> KlienLLM | None:
    return current_app.extensions.get(KUNCI_KLIEN)


def _status_siswa(main_id: str, langkah: dict) -> StatusSiswa:
    conn = koneksi()
    no = langkah["no"]

    benar = conn.execute(
        "SELECT 1 FROM jawaban_langkah " "WHERE main_id = ? AND langkah = ? AND benar = 1",
        (main_id, no),
    ).fetchone()

    salah = conn.execute(
        "SELECT COUNT(*) AS n FROM jawaban_langkah "
        "WHERE main_id = ? AND langkah = ? AND benar = 0",
        (main_id, no),
    ).fetchone()["n"]

    tingkat = conn.execute(
        "SELECT MAX(tingkat) AS t FROM petunjuk_dibuka " "WHERE main_id = ? AND langkah = ?",
        (main_id, no),
    ).fetchone()["t"]

    terakhir = conn.execute(
        "SELECT jawaban, kode_diagnosis FROM jawaban_langkah "
        "WHERE main_id = ? AND langkah = ? ORDER BY id DESC LIMIT 1",
        (main_id, no),
    ).fetchone()

    umpan = None

    if terakhir and terakhir["kode_diagnosis"]:
        try:
            umpan = periksa_langkah(langkah, json.loads(terakhir["jawaban"])).umpan_balik
        except (ValueError, TypeError):
            umpan = None

    return StatusSiswa(
        sudah_benar=bool(benar),
        percobaan_salah=int(salah),
        tingkat_petunjuk=int(tingkat or 0),
        kode_terakhir=terakhir["kode_diagnosis"] if terakhir else None,
        umpan_terakhir=umpan,
    )


def _pasangan_terjawab(rows: list) -> list[dict[str, str]]:
    """Ubah baris log (urut waktu) menjadi riwayat untuk model, hanya pasangan yang lengkap.

    Pertanyaan siswa yang gagal dijawab (diikuti baris 'galat' atau pertanyaan lain) TIDAK
    ikut dikirim. Jika ikut, model menganggapnya pertanyaan yang belum dijawab dan
    menjawabnya ulang bersama pertanyaan baru.
    """
    riwayat: list[dict[str, str]] = []
    for i, r in enumerate(rows):
        if r["peran"] == "siswa":
            berikut = rows[i + 1] if i + 1 < len(rows) else None
            terjawab = (
                berikut is not None
                and berikut["peran"] == "asisten"
                and berikut["sumber"] != "galat"
            )
            if terjawab:
                riwayat.append({"role": "user", "content": r["teks"]})
        elif r["sumber"] != "galat":
            riwayat.append({"role": "assistant", "content": r["teks"]})
    return riwayat


def _riwayat(main_id: str, no: str) -> list[dict[str, str]]:
    rows = (
        koneksi()
        .execute(
            "SELECT peran, teks, sumber FROM percakapan_asisten "
            "WHERE main_id = ? AND langkah = ? ORDER BY id",
            (main_id, no),
        )
        .fetchall()
    )
    return _pasangan_terjawab(rows)


def _panggil_model(klien: KlienLLM, pesan: list, asal: str) -> tuple[HasilLLM | None, str]:
    """Panggil model. Kembalikan (hasil, "") atau (None, alasan galat yang aman dicatat).

    Galat yang dikenal (GalatLLM) dicatat ringkas. Galat tak terduga dicatat lengkap dengan
    traceback agar penyebab aslinya terlihat di log server, lalu tetap dibalas JSON 503
    (bukan halaman 500 HTML). Traceback Python tidak memuat nilai variabel, jadi API key
    tidak ikut tercetak; alasan yang disimpan juga dibersihkan dari API key.
    """
    try:
        return klien.balas(pesan), ""
    except GalatLLM as e:
        current_app.logger.warning("Asisten %s gagal: %s", asal, e.pesan)
        if e.status in GALAT_TETAP:
            return None, e.pesan
        # Galat sementara (balasan kosong karena model "berpikir" kehabisan token, batas
        # permintaan, server penyedia bermasalah, koneksi putus): coba sekali lagi.
        # openrouter/free biasanya memilih model lain pada percobaan kedua.
        try:
            return klien.balas(pesan), ""
        except GalatLLM as e2:
            current_app.logger.warning("Asisten %s gagal lagi: %s", asal, e2.pesan)
            return None, f"{e.pesan} | Percobaan ulang: {e2.pesan}"[:600]
        except Exception:  # noqa: BLE001 - dicatat lalu dilaporkan sebagai galat pertama
            current_app.logger.exception("Asisten %s galat tak terduga saat mengulang", asal)
            return None, e.pesan
    except Exception as e:  # noqa: BLE001 - jaring pengaman, penyebab dicatat di log
        current_app.logger.exception("Asisten %s galat tak terduga", asal)
        alasan = f"Galat tak terduga: {type(e).__name__}: {e}"
        api_key = _konfig().api_key
        if api_key:
            alasan = alasan.replace(api_key, "[KEY]")
        return None, alasan[:300]


def _simpan(umum: dict, **isian: object) -> None:
    baris = {**umum, **isian, "waktu": sekarang()}
    nilai = [baris.get(k) for k in _KOLOM]

    for i, kolom in enumerate(_KOLOM):
        if kolom in {"disamarkan", "disaring"} and nilai[i] is None:
            nilai[i] = 0

    koneksi().execute(
        f"INSERT INTO percakapan_asisten ({', '.join(_KOLOM)}) "
        f"VALUES ({', '.join('?' for _ in _KOLOM)})",
        nilai,
    )


_KOLOM = (
    "main_id",
    "kode_anonim",
    "misi_id",
    "langkah",
    "peran",
    "teks",
    "teks_asli",
    "disamarkan",
    "disaring",
    "alasan_saring",
    "langkah_benar",
    "percobaan_salah",
    "tingkat_petunjuk",
    "kode_diagnosis",
    "tingkat_bantuan",
    "tahap_rmt",
    "fase_kognitif",
    "sumber",
    "model",
    "token_masuk",
    "token_keluar",
    "durasi_ms",
    "waktu",
)


@bp.get("/status")
def status():
    k = _konfig()

    return jsonify(
        {
            "aktif": _klien() is not None,
            "maks_pesan_per_misi": k.maks_pesan_per_misi,
            "maks_panjang_pesan": k.maks_panjang_pesan,
        }
    )


@bp.post("/pesan")
def kirim_pesan():
    klien = _klien()

    if klien is None:
        raise GalatApi("Pembimbing AI belum diaktifkan di server ini.", 503)

    k = _konfig()
    data = data_json()
    main = ambil_main(data.get("main_id"))

    if main["selesai"]:
        raise GalatApi("Misi ini sudah selesai.")

    misi = bank_soal.ambil_misi(main["misi_id"])
    no = str(data.get("langkah") or "")
    langkah = bank_soal.cari_langkah(misi, no) if misi else None

    if langkah is None:
        raise GalatApi("Langkah tidak ditemukan.", 404)

    teks = teks_wajib(data, "teks", "Pertanyaan", k.maks_panjang_pesan)
    conn = koneksi()

    terpakai = conn.execute(
        "SELECT COUNT(*) AS n FROM percakapan_asisten " "WHERE main_id = ? AND peran = 'siswa'",
        (main["id"],),
    ).fetchone()["n"]

    if terpakai >= k.maks_pesan_per_misi:
        raise GalatApi(
            "Batas pertanyaan untuk misi ini sudah tercapai. " "Kamu masih bisa memakai petunjuk.",
            429,
        )

    sesi = conn.execute(
        "SELECT nama_panggilan FROM sesi WHERE id = ?",
        (main["sesi_id"],),
    ).fetchone()

    teks_aman, disamarkan = samarkan(teks, sesi["nama_panggilan"] if sesi else None)

    status_siswa = _status_siswa(main["id"], langkah)
    tahap = rmt.tahap_langkah(main["misi_id"], no)
    fase = rmt.fase_kesalahan(status_siswa.kode_terakhir, main["misi_id"], no)

    pesan = susun_pesan(
        misi,
        langkah,
        status_siswa,
        _riwayat(main["id"], no),
        teks_aman,
        tahap=tahap,
        fase=fase,
    )

    umum = {
        "main_id": main["id"],
        "kode_anonim": kode_anonim(main["sesi_id"], k.rahasia_anonim),
        "misi_id": main["misi_id"],
        "langkah": no,
        "langkah_benar": int(status_siswa.sudah_benar),
        "percobaan_salah": status_siswa.percobaan_salah,
        "tingkat_petunjuk": status_siswa.tingkat_petunjuk,
        "kode_diagnosis": status_siswa.kode_terakhir,
        # Label RMT (Tahap 1); sejak Tahap 2F juga dipakai untuk mediasi di instruksi model.
        "tahap_rmt": tahap,
        "fase_kognitif": fase,
        "tingkat_bantuan": tingkat_bantuan(status_siswa),
    }

    _simpan(
        umum,
        peran="siswa",
        teks=teks_aman,
        disamarkan=int(disamarkan),
        sumber=klien.sumber,
    )

    mulai = time.monotonic()

    hasil, alasan_galat = _panggil_model(klien, pesan, "misi")
    durasi = int((time.monotonic() - mulai) * 1000)

    if hasil is None:
        _simpan(umum, peran="asisten", teks=alasan_galat, sumber="galat", durasi_ms=durasi)
        conn.commit()
        raise GalatApi(
            "Pembimbing sedang tidak bisa dihubungi. Coba lagi sebentar, atau buka petunjuk.",
            503,
        )

    if status_siswa.sudah_benar:
        cek_teks, disaring, alasan = hasil.teks, False, None
    else:
        angka, kalimat = larangan(misi, langkah)
        cek = periksa_balasan(hasil.teks, angka, kalimat)
        cek_teks = cek.teks
        disaring = cek.disaring
        alasan = cek.alasan

    _simpan(
        umum,
        peran="asisten",
        teks=cek_teks,
        teks_asli=hasil.teks if disaring else None,
        disaring=int(disaring),
        alasan_saring=alasan,
        sumber=klien.sumber,
        model=hasil.model,
        token_masuk=hasil.token_masuk,
        token_keluar=hasil.token_keluar,
        durasi_ms=durasi,
    )

    conn.commit()

    return jsonify(
        {
            "balasan": cek_teks,
            "sisa_pertanyaan": max(0, k.maks_pesan_per_misi - terpakai - 1),
        }
    )


# ------------------------------------------------------------
# Chat Pembimbing AI di beranda
# ------------------------------------------------------------


@bp.post("/beranda")
def kirim_pesan_beranda():
    klien = _klien()

    if klien is None:
        raise GalatApi("Pembimbing AI belum diaktifkan di server ini.", 503)

    k = _konfig()
    data = data_json()

    sesi_id = str(data.get("sesi_id") or "")
    conn = koneksi()

    sesi = conn.execute(
        "SELECT id, nama_panggilan FROM sesi WHERE id = ?",
        (sesi_id,),
    ).fetchone()

    if sesi is None:
        raise GalatApi("Sesi tidak ditemukan. Masukkan namamu lagi.", 404)

    teks = teks_wajib(data, "teks", "Pertanyaan", k.maks_panjang_pesan)

    terpakai = conn.execute(
        "SELECT COUNT(*) AS n FROM percakapan_beranda " "WHERE sesi_id = ? AND peran = 'siswa'",
        (sesi_id,),
    ).fetchone()["n"]

    if terpakai >= k.maks_pesan_per_misi:
        raise GalatApi(
            "Batas pertanyaan Pembimbing AI sudah tercapai.",
            429,
        )

    teks_aman, disamarkan = samarkan(teks, sesi["nama_panggilan"])

    # Ambil lebih banyak baris (termasuk galat) lalu saring: susun_pesan_beranda tetap
    # membatasi ke 8 pesan terakhir.
    # Hanya percakapan yang masih berlangsung (RIWAYAT_BERANDA_MENIT terakhir). Balasan lama
    # (misalnya dari instruksi versi sebelumnya) tidak ikut, agar gayanya tidak ditiru model.
    batas_waktu = (datetime.now(UTC) - timedelta(minutes=RIWAYAT_BERANDA_MENIT)).isoformat(
        timespec="seconds"
    )
    riwayat_rows = conn.execute(
        "SELECT peran, teks, sumber FROM percakapan_beranda "
        "WHERE sesi_id = ? AND waktu >= ? ORDER BY id DESC LIMIT 24",
        (sesi_id, batas_waktu),
    ).fetchall()
    riwayat = _buang_contoh_tanya_balik(_pasangan_terjawab(list(reversed(riwayat_rows))))

    # Instruksi sistem ada di asisten/prompt.py (INSTRUKSI_BERANDA).
    pesan = susun_pesan_beranda(riwayat, teks_aman)

    kode = kode_anonim(sesi_id, k.rahasia_anonim)

    conn.execute(
        """
        INSERT INTO percakapan_beranda
        (sesi_id, kode_anonim, peran, teks, disamarkan, sumber, waktu)
        VALUES (?, ?, 'siswa', ?, ?, ?, ?)
        """,
        (
            sesi_id,
            kode,
            teks_aman,
            int(disamarkan),
            klien.sumber,
            sekarang(),
        ),
    )

    mulai = time.monotonic()

    hasil, alasan_galat = _panggil_model(klien, pesan, "beranda")

    if hasil is not None and menyuruh_siswa_menghitung(hasil.teks):
        # Model (dipilih acak oleh openrouter/free) tetap menahan jawaban. Minta sekali lagi
        # agar langsung menyelesaikan; jika permintaan ulang gagal, pakai balasan pertama.
        current_app.logger.warning("Asisten beranda menahan jawaban; meminta ulang sekali.")
        ulang, _ = _panggil_model(
            klien,
            [
                *pesan,
                {"role": "assistant", "content": hasil.teks},
                {"role": "user", "content": PERMINTAAN_JAWAB_LANGSUNG},
            ],
            "beranda (ulang)",
        )
        if ulang is not None:
            hasil = ulang

    durasi = int((time.monotonic() - mulai) * 1000)

    if hasil is None:
        # Catat alasan kegagalan (aman, tanpa API key) agar bisa diperiksa peneliti.
        conn.execute(
            """
            INSERT INTO percakapan_beranda
            (sesi_id, kode_anonim, peran, teks, sumber, durasi_ms, waktu)
            VALUES (?, ?, 'asisten', ?, 'galat', ?, ?)
            """,
            (sesi_id, kode, alasan_galat, durasi, sekarang()),
        )
        conn.commit()
        raise GalatApi(
            "Pembimbing sedang tidak bisa dihubungi. Coba lagi sebentar.",
            503,
        )

    # Samarkan informasi pribadi jika muncul kembali dalam balasan AI.
    balasan, _ = samarkan(hasil.teks, nomor_panjang=False)

    conn.execute(
        """
        INSERT INTO percakapan_beranda
        (sesi_id, kode_anonim, peran, teks, sumber,
         model, token_masuk, token_keluar, durasi_ms, waktu)
        VALUES (?, ?, 'asisten', ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sesi_id,
            kode,
            balasan,
            klien.sumber,
            hasil.model,
            hasil.token_masuk,
            hasil.token_keluar,
            durasi,
            sekarang(),
        ),
    )

    conn.commit()

    return jsonify(
        {
            "balasan": balasan,
            "sisa_pertanyaan": max(0, k.maks_pesan_per_misi - terpakai - 1),
        }
    )
