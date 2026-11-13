"""Memuat, memvalidasi, dan menyaring bank soal JSON."""

from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

FOLDER_SOAL = Path(__file__).resolve().parent.parent / "data" / "soal"

# Field yang TIDAK boleh dikirim ke browser sebelum siswa menjawab (CLAUDE.md).
FIELD_RAHASIA = {
    "kunci",
    "petunjuk",
    "pola_salah",
    "pola_salah_isian",
    "konteks_diagnosis",
    "penjelasan_benar",
    "umpan_balik_opsi",
    "umpan_balik_item",
}

TIPE_LANGKAH = {"pilihan", "angka", "rumus", "pilah"}


def _validasi_langkah(langkah: dict[str, Any], lokasi: str, wajib_petunjuk: bool) -> None:
    for f in ("tipe", "instruksi", "kunci", "penjelasan_benar"):
        if f not in langkah:
            raise ValueError(f"{lokasi}: field '{f}' tidak ada")
    tipe = langkah["tipe"]
    if tipe not in TIPE_LANGKAH:
        raise ValueError(f"{lokasi}: tipe '{tipe}' tidak dikenal")
    if wajib_petunjuk and len(langkah.get("petunjuk", [])) != 3:
        raise ValueError(f"{lokasi}: petunjuk harus tepat 3 tingkat")
    if tipe == "pilihan":
        ids = {o["id"] for o in langkah["opsi"]}
        kunci = langkah["kunci"] if isinstance(langkah["kunci"], list) else [langkah["kunci"]]
        if not set(kunci) <= ids:
            raise ValueError(f"{lokasi}: kunci pilihan tidak ada di opsi")
    elif tipe == "pilah":
        item_ids = {i["id"] for i in langkah["item"]}
        kotak_ids = {k["id"] for k in langkah["kotak"]}
        if set(langkah["kunci"]) != item_ids or not set(langkah["kunci"].values()) <= kotak_ids:
            raise ValueError(f"{lokasi}: kunci pilah tidak cocok dengan item/kotak")
    elif tipe == "rumus":
        if langkah["template"].count("[]") != len(langkah["kunci"]["isian"]):
            raise ValueError(f"{lokasi}: banyak kotak template ≠ banyak kunci")
    elif tipe == "angka":
        if "nilai" not in langkah["kunci"]:
            raise ValueError(f"{lokasi}: kunci angka tanpa nilai")


def validasi_misi(daftar: list[dict[str, Any]]) -> None:
    for misi in daftar:
        nomor = set()
        for langkah in misi["langkah"]:
            lokasi = f"misi {misi['id']} langkah {langkah.get('no')}"
            for f in ("no", "tahap", "skor"):
                if f not in langkah:
                    raise ValueError(f"{lokasi}: field '{f}' tidak ada")
            if langkah["no"] in nomor:
                raise ValueError(f"{lokasi}: nomor langkah ganda")
            nomor.add(langkah["no"])
            _validasi_langkah(langkah, lokasi, wajib_petunjuk=True)
        total = sum(lk["skor"] for lk in misi["langkah"])
        if abs(total - 6) > 1e-9:
            raise ValueError(f"misi {misi['id']}: skor maksimum {total}, seharusnya 6")


@lru_cache(maxsize=1)
def semua_misi() -> tuple[dict[str, Any], ...]:
    with open(FOLDER_SOAL / "misi.json", encoding="utf-8") as f:
        daftar = json.load(f)
    validasi_misi(daftar)
    return tuple(daftar)


@lru_cache(maxsize=1)
def latihan() -> dict[str, Any]:
    with open(FOLDER_SOAL / "latihan.json", encoding="utf-8") as f:
        data = json.load(f)
    for soal in data["pilah"]:
        _validasi_langkah(soal, f"latihan {soal['id']}", wajib_petunjuk=False)
    return data


def ambil_misi(misi_id: int) -> dict[str, Any] | None:
    return next((m for m in semua_misi() if m["id"] == misi_id), None)


def cari_langkah(misi: dict[str, Any], no: str) -> dict[str, Any] | None:
    return next((lk for lk in misi["langkah"] if lk["no"] == no), None)


def saring_rahasia(data: dict[str, Any]) -> dict[str, Any]:
    """Salinan langkah/soal tanpa kunci, petunjuk, dan umpan balik."""
    return {k: copy.deepcopy(v) for k, v in data.items() if k not in FIELD_RAHASIA}


def misi_publik(misi: dict[str, Any]) -> dict[str, Any]:
    hasil = {k: copy.deepcopy(v) for k, v in misi.items() if k != "langkah"}
    hasil["langkah"] = [saring_rahasia(lk) for lk in misi["langkah"]]
    return hasil
