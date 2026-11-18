"""Pengaman balasan: mencegah chatbot membocorkan jawaban akhir langkah.

Instruksi ke model saja tidak cukup, jadi setiap balasan diperiksa di server
sebelum dikirim ke siswa.

Keterbatasan (diketahui):
- Angka yang ditulis dengan kata ("seribu dua ratus") atau dipisah spasi ("1 200") tidak terdeteksi.
- Angka kunci yang juga muncul di cerita soal tidak bisa dilarang (contoh: isian rumus 12 dan 7).
- Untuk soal pilah, isi jawaban tidak diperiksa (terlalu banyak kata umum).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from segitiga.parser_angka import parse_angka, samakah

_ANGKA = re.compile(r"(?:rp\.?\s*)?\d[\d.,]*(?:\s*/\s*\d+)?", re.IGNORECASE)
_PECAHAN_UNICODE = re.compile(r"[½⅓⅔¼¾⅕⅖⅗⅘]")

PENGGANTI = (
    "Aku tidak boleh menyebutkan jawabannya langsung. Kalau kamu sudah punya jawaban, "
    "masukkan lalu tekan Periksa. Bagian mana yang masih membuatmu ragu?"
)


@dataclass(frozen=True)
class HasilPengaman:
    teks: str
    disaring: bool
    alasan: str | None = None


def _angka_dalam(teks: str) -> list[float]:
    hasil = []
    for m in _ANGKA.finditer(teks):
        nilai = parse_angka(m.group().rstrip(".,"))
        if nilai is not None:
            hasil.append(nilai)
    for m in _PECAHAN_UNICODE.finditer(teks):
        nilai = parse_angka(m.group())
        if nilai is not None:
            hasil.append(nilai)
    return hasil


def _normal(teks: str) -> str:
    return re.sub(r"\s+", " ", teks.lower()).strip(" .")


def larangan(misi: dict[str, Any], langkah: dict[str, Any]) -> tuple[list[float], list[str]]:
    """Angka dan kalimat yang tidak boleh muncul di balasan untuk langkah ini."""
    teks_soal = " ".join([*misi["cerita"], langkah["instruksi"]])
    angka_soal = _angka_dalam(teks_soal)
    calon: list[float] = []
    kalimat: list[str] = []
    if langkah["tipe"] == "angka":
        calon = [float(langkah["kunci"]["nilai"])]
    elif langkah["tipe"] == "rumus":
        calon = [v for v in (parse_angka(x) for x in langkah["kunci"]["isian"]) if v is not None]
    elif langkah["tipe"] == "pilihan":
        teks_opsi = {o["id"]: o["teks"] for o in langkah["opsi"]}
        kunci = langkah["kunci"] if isinstance(langkah["kunci"], list) else [langkah["kunci"]]
        kalimat = [_normal(teks_opsi[k]) for k in kunci if len(teks_opsi[k]) >= 15]
    angka = [v for v in calon if not any(samakah(v, a) for a in angka_soal)]
    return angka, kalimat


def periksa_balasan(
    teks: str, angka_terlarang: list[float], kalimat_terlarang: list[str]
) -> HasilPengaman:
    for v in _angka_dalam(teks):
        if any(samakah(v, t) for t in angka_terlarang):
            return HasilPengaman(PENGGANTI, True, "angka_kunci")
    normal = _normal(teks)
    if any(k in normal for k in kalimat_terlarang):
        return HasilPengaman(PENGGANTI, True, "opsi_kunci")
    return HasilPengaman(teks, False)


# ------------------------------------------------------------------ chatbot BERANDA
# Kalimat yang menyuruh siswa menghitung/menjawab sendiri ("tanya balik"). Di Tanya
# Pembimbing ini dilarang: siswa meminta jawaban, bukan latihan. (Tidak dipakai di misi.)
_TANYA_BALIK = re.compile(
    r"(apa|berapa)\s+(hasil|jawaban)(nya|mu)?\b"
    r"|apa\s+jawabanmu"
    r"|coba\s+(kamu\s+)?(hitung|kerjakan|jawab|cari|tentukan)"
    r"|giliran\s*(mu|kamu)"
    r"|sekarang\s+kamu\s+(hitung|coba|kerjakan)"
    r"|bisakah\s+kamu\s+(menghitung|mencari|menentukan)"
    r"|kamu\s+(hitung|kerjakan)\s+(sendiri|dulu)",
    re.IGNORECASE,
)


def menyuruh_siswa_menghitung(teks: str) -> bool:
    """True jika balasan menahan jawaban dan menyuruh siswa menghitung/menjawab sendiri."""
    return bool(_TANYA_BALIK.search(teks))
