"""Aktivitas pendamping RMT per misi (Tahap 2A) — memuat, memvalidasi, menyaring, memeriksa.

Aktivitas ini TERPISAH dari sistem penilaian: tidak menambah atau mengurangi skor rubrik,
dan tidak mengubah misi.json, penilai.py, atau diagnosis.py. Pilihan ganda diperiksa dengan
memakai ulang `penilai.periksa_langkah` (tanpa mengubahnya).

Rujukan RMT (lihat docs/13): Input [hal. 9], Perencanaan & Refleksi [hal. 8],
Representasi & Validasi [hal. 14], Transendensi [hal. 9], Intensionalitas & Makna [hal. 9].
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .penilai import periksa_langkah

FILE_KONTEN = Path(__file__).resolve().parent.parent / "data" / "soal" / "rmt_misi.json"

INPUT = "input"
PERENCANAAN = "perencanaan"
REPRESENTASI = "representasi"
VALIDASI = "validasi"
REFLEKSI = "refleksi"
TRANSENDENSI = "transendensi"
TAHAP_WAJIB = (INPUT, PERENCANAAN, REPRESENTASI, VALIDASI, REFLEKSI, TRANSENDENSI)

JENIS = {"prediksi", "urutan", "pilihan", "pilihan_banyak", "teks"}

# Tidak boleh dikirim ke browser sebelum siswa menjawab.
FIELD_RAHASIA = {"kunci", "jawaban_sebenarnya", "penjelasan", "umpan_balik_opsi", "umpan_balik"}

PANJANG_TEKS_MAKS = 1000
PANJANG_TUJUAN_MAKS = 200  # aturan desain: teks pendek


@dataclass(frozen=True)
class HasilAktivitas:
    benar: bool | None  # None = aktivitas tanpa jawaban benar (prediksi, teks)
    umpan_balik: str
    penjelasan: str | None
    jawaban: dict[str, Any]  # yang disimpan ke database


# ------------------------------------------------------------------ validasi konten
def _galat(lokasi: str, pesan: str) -> ValueError:
    return ValueError(f"rmt_misi.json {lokasi}: {pesan}")


def _validasi_aktivitas(a: dict[str, Any], lokasi: str) -> None:
    for f in ("id", "jenis", "tahap"):
        if not a.get(f):
            raise _galat(lokasi, f"field '{f}' kosong")
    if a["jenis"] not in JENIS:
        raise _galat(lokasi, f"jenis '{a['jenis']}' tidak dikenal")
    if a["tahap"] not in TAHAP_WAJIB:
        raise _galat(lokasi, f"tahap '{a['tahap']}' tidak dikenal")

    jenis = a["jenis"]
    if jenis in {"prediksi", "pilihan", "pilihan_banyak"}:
        ids = [o["id"] for o in a.get("opsi", [])]
        if len(ids) < 2 or len(set(ids)) != len(ids):
            raise _galat(lokasi, "opsi minimal 2 dan id harus unik")
        if not a.get("pertanyaan"):
            raise _galat(lokasi, "pertanyaan kosong")
    if jenis == "prediksi":
        if a.get("jawaban_sebenarnya") not in ids:
            raise _galat(lokasi, "jawaban_sebenarnya tidak ada di opsi")
    elif jenis == "pilihan":
        if a.get("kunci") not in ids:
            raise _galat(lokasi, "kunci tidak ada di opsi")
    elif jenis == "pilihan_banyak":
        kunci = a.get("kunci")
        if not isinstance(kunci, list) or len(kunci) < 2 or not set(kunci) <= set(ids):
            raise _galat(lokasi, "kunci pilihan_banyak harus daftar minimal 2 id opsi")
    elif jenis == "urutan":
        kartu = [k["id"] for k in a.get("kartu", [])]
        if len(kartu) < 3 or len(set(kartu)) != len(kartu):
            raise _galat(lokasi, "kartu minimal 3 dan id harus unik")
        kunci = a.get("kunci")
        if not isinstance(kunci, list) or not kunci:
            raise _galat(lokasi, "kunci urutan harus daftar urutan yang diterima")
        for urutan in kunci:
            if sorted(urutan) != sorted(kartu):
                raise _galat(lokasi, "setiap kunci urutan harus memuat semua kartu tepat sekali")
        if sorted(kartu) in kunci:
            raise _galat(lokasi, "urutan tampil (alfabet id) sama dengan kunci: kunci bocor")
    elif jenis == "teks":
        if not a.get("kalimat_pembuka"):
            raise _galat(lokasi, "kalimat_pembuka kosong")
    if jenis in {"pilihan", "pilihan_banyak", "urutan"} and not a.get("penjelasan"):
        raise _galat(lokasi, "penjelasan kosong")


def validasi(daftar: list[dict[str, Any]], misi_ids: set[int]) -> None:
    ada = {k.get("misi_id") for k in daftar}
    if ada != misi_ids or len(daftar) != len(misi_ids):
        raise ValueError(f"rmt_misi.json harus memuat tepat misi {sorted(misi_ids)}, ada {ada}")
    for k in daftar:
        lokasi = f"misi {k['misi_id']}"
        for f in ("tujuan", "makna"):
            teks = k.get(f) or ""
            if not teks or len(teks) > PANJANG_TUJUAN_MAKS:
                raise _galat(lokasi, f"'{f}' harus diisi dan maksimal {PANJANG_TUJUAN_MAKS} huruf")
        ids = [a.get("id") for a in k.get("aktivitas", [])]
        if len(set(ids)) != len(ids):
            raise _galat(lokasi, "id aktivitas ganda")
        for a in k["aktivitas"]:
            _validasi_aktivitas(a, f"{lokasi} aktivitas {a.get('id')}")
        tahap = {a["tahap"] for a in k["aktivitas"]}
        kurang = set(TAHAP_WAJIB) - tahap
        if kurang:
            raise _galat(lokasi, f"tahap belum ada: {sorted(kurang)}")


@lru_cache(maxsize=1)
def semua_konten() -> tuple[dict[str, Any], ...]:
    from . import bank_soal  # impor lokal agar modul ini tetap ringan

    with open(FILE_KONTEN, encoding="utf-8") as f:
        daftar = json.load(f)
    validasi(daftar, {m["id"] for m in bank_soal.semua_misi()})
    return tuple(daftar)


def ambil(misi_id: int) -> dict[str, Any] | None:
    return next((k for k in semua_konten() if k["misi_id"] == int(misi_id)), None)


def cari_aktivitas(konten: dict[str, Any], aktivitas_id: str) -> dict[str, Any] | None:
    return next((a for a in konten["aktivitas"] if a["id"] == aktivitas_id), None)


# ------------------------------------------------------------------ untuk browser
def publik(konten: dict[str, Any]) -> dict[str, Any]:
    """Salinan tanpa kunci/penjelasan/umpan balik. Kartu urutan diurutkan menurut id
    (alfabet), yang dijamin validasi BERBEDA dari urutan jawaban."""
    hasil = {k: copy.deepcopy(v) for k, v in konten.items() if k != "aktivitas"}
    hasil["aktivitas"] = []
    for a in konten["aktivitas"]:
        b = {k: copy.deepcopy(v) for k, v in a.items() if k not in FIELD_RAHASIA}
        if a["jenis"] == "urutan":
            b["kartu"] = sorted(b["kartu"], key=lambda kartu: kartu["id"])
        hasil["aktivitas"].append(b)
    return hasil


# ------------------------------------------------------------------ pemeriksaan
def _periksa_urutan(a: dict[str, Any], jawaban: dict[str, Any]) -> HasilAktivitas:
    urutan = jawaban.get("urutan")
    kartu = {k["id"]: k["teks"] for k in a["kartu"]}
    if not isinstance(urutan, list) or sorted(map(str, urutan)) != sorted(kartu):
        raise ValueError("Susun semua kartu tepat satu kali.")
    urutan = [str(x) for x in urutan]
    if urutan in a["kunci"]:
        return HasilAktivitas(True, a["penjelasan"], a["penjelasan"], {"urutan": urutan})
    # Tunjuk posisi yang belum tepat (dibanding kunci terdekat) tanpa membuka urutannya.
    terdekat = min(a["kunci"], key=lambda k: sum(x != y for x, y in zip(k, urutan, strict=True)))
    salah = [i + 1 for i, (x, y) in enumerate(zip(terdekat, urutan, strict=True)) if x != y]
    posisi = ", ".join(f"ke-{i}" for i in salah)
    pesan = f"Kartu {posisi} belum di posisi yang tepat. Pikirkan: apa yang harus diketahui dulu?"
    return HasilAktivitas(False, pesan, None, {"urutan": urutan})


def _periksa_pilihan(a: dict[str, Any], jawaban: dict[str, Any]) -> HasilAktivitas:
    banyak = a["jenis"] == "pilihan_banyak"
    langkah = {
        "tipe": "pilihan",
        "opsi": a["opsi"],
        "kunci": a["kunci"],
        "pilih_banyak": banyak,
        "umpan_balik_opsi": a.get("umpan_balik_opsi", {}),
        "penjelasan_benar": a["penjelasan"],
    }
    dipilih = jawaban.get("pilihan")
    ids = {o["id"] for o in a["opsi"]}
    if isinstance(dipilih, list) != banyak:
        # pilihan tunggal harus satu id; pilihan_banyak harus berupa daftar
        raise ValueError("Format pilihan tidak sesuai dengan jenis soal.")
    daftar = dipilih if isinstance(dipilih, list) else [dipilih]
    if not dipilih or not all(isinstance(x, str) and x in ids for x in daftar):
        raise ValueError("Pilih jawaban dari opsi yang tersedia.")
    h = periksa_langkah(langkah, {"pilihan": dipilih})
    return HasilAktivitas(
        h.benar, h.umpan_balik, a["penjelasan"] if h.benar else None, {"pilihan": dipilih}
    )


def _periksa_prediksi(a: dict[str, Any], jawaban: dict[str, Any]) -> HasilAktivitas:
    dipilih = jawaban.get("pilihan")
    if dipilih not in {o["id"] for o in a["opsi"]}:
        raise ValueError("Pilih salah satu tebakan.")
    pesan = a.get("umpan_balik") or "Tebakanmu sudah dicatat."
    return HasilAktivitas(None, pesan, None, {"pilihan": dipilih})


def _periksa_teks(a: dict[str, Any], jawaban: dict[str, Any]) -> HasilAktivitas:
    teks = str(jawaban.get("teks") or "").strip()
    if not teks:
        raise ValueError("Tulis penjelasanmu dulu, atau pilih lewati.")
    if len(teks) > PANJANG_TEKS_MAKS:
        raise ValueError(f"Penjelasan terlalu panjang (maksimal {PANJANG_TEKS_MAKS} huruf).")
    return HasilAktivitas(None, "Terima kasih, penjelasanmu sudah dicatat.", None, {"teks": teks})


_PEMERIKSA = {
    "urutan": _periksa_urutan,
    "pilihan": _periksa_pilihan,
    "pilihan_banyak": _periksa_pilihan,
    "prediksi": _periksa_prediksi,
    "teks": _periksa_teks,
}


def periksa(a: dict[str, Any], jawaban: Any) -> HasilAktivitas:
    """Periksa respons aktivitas. ValueError bila format jawaban tidak sah."""
    if not isinstance(jawaban, dict):
        raise ValueError("Format jawaban tidak sah.")
    return _PEMERIKSA[a["jenis"]](a, jawaban)
