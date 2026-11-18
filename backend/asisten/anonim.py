"""Kode anonim siswa dan penyamaran data pribadi sebelum teks dikirim ke DeepSeek."""

from __future__ import annotations

import hashlib
import hmac
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
_TELEPON = re.compile(r"(?<!\d)(?:\+?62|0)\s?8[\d\s-]{7,13}\d(?!\d)")
# NIK/NISN/nomor HP tanpa format; titik/koma sesudahnya boleh selama bukan bagian angka
_NOMOR_PANJANG = re.compile(r"(?<![\d.,])\d{10,}(?!\d|[.,]\d)")


def kode_anonim(sesi_id: str, rahasia: str = "") -> str:
    """Kode stabil untuk satu sesi, tidak bisa dibalik ke sesi_id tanpa rahasia."""
    kunci = (rahasia or "segipintar").encode("utf-8")
    ringkas = hmac.new(kunci, sesi_id.encode("utf-8"), hashlib.sha256).hexdigest()[:10]
    return f"S-{ringkas.upper()}"


def samarkan(teks: str, nama: str | None = None, nomor_panjang: bool = True) -> tuple[str, bool]:
    """Ganti email, nomor telepon, nomor panjang, dan nama panggilan siswa dengan penanda.

    nomor_panjang=False dipakai untuk balasan AI: hasil hitungan bisa berupa angka
    10 digit atau lebih dan tidak boleh berubah menjadi "[nomor]".
    """
    hasil = _EMAIL.sub("[email]", teks)
    hasil = _TELEPON.sub("[nomor]", hasil)
    if nomor_panjang:
        hasil = _NOMOR_PANJANG.sub("[nomor]", hasil)
    if nama and len(nama.strip()) >= 3:
        pola = re.compile(rf"(?<!\w){re.escape(nama.strip())}(?!\w)", re.IGNORECASE)
        hasil = pola.sub("[nama]", hasil)
    return hasil, hasil != teks
