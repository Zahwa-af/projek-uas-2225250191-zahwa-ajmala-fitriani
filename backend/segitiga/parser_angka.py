"""Membaca angka yang diketik siswa dalam format Indonesia.

Contoh yang diterima:
    "1,8"        -> 1.8      (koma = desimal)
    "1.200"      -> 1200     (titik + tepat 3 digit = ribuan)
    "Rp300.000"  -> 300000
    "1200 cm²"   -> 1200     (satuan dibuang; dicek terpisah)
    "1/3", "⅓"   -> 0.333...
"""

from __future__ import annotations

import re

PECAHAN_UNICODE: dict[str, float] = {
    "½": 1 / 2,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "¼": 1 / 4,
    "¾": 3 / 4,
    "⅕": 1 / 5,
    "⅖": 2 / 5,
    "⅗": 3 / 5,
    "⅘": 4 / 5,
}

_SATUAN_DI_AKHIR = re.compile(r"(cm|mm|m)(\^?2|²)?$")
_RIBUAN_TITIK = re.compile(r"^-?[1-9]\d{0,2}(\.\d{3})+$")
_RIBUAN_KOMA = re.compile(r"^-?[1-9]\d{0,2}(,\d{3}){2,}$")
_ANGKA_BIASA = re.compile(r"^-?\d+(\.\d+)?$")

TOLERANSI_RELATIF = 0.005  # 0,5% — mengatasi pembulatan seperti ⅓


def _bersihkan(teks: str) -> str:
    t = teks.strip().lower().replace(" ", "").replace("−", "-")
    if t.startswith("rp"):
        t = t[2:].lstrip(".")
    return _SATUAN_DI_AKHIR.sub("", t)


def _ke_angka(t: str) -> float | None:
    if not t:
        return None
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")  # gaya Indonesia: 1.200,5
        else:
            t = t.replace(",", "")  # gaya Inggris: 1,200.5
    elif "," in t:
        if t.count(",") == 1:
            t = t.replace(",", ".")
        elif _RIBUAN_KOMA.match(t):
            t = t.replace(",", "")
        else:
            return None
    elif "." in t:
        if _RIBUAN_TITIK.match(t):
            t = t.replace(".", "")
        elif t.count(".") > 1:
            return None
    if not _ANGKA_BIASA.match(t):
        return None
    return float(t)


def parse_angka(teks: str | int | float | None) -> float | None:
    """Ubah teks jawaban siswa menjadi float. Kembalikan None jika tidak terbaca."""
    if teks is None:
        return None
    if isinstance(teks, bool):
        return None
    if isinstance(teks, int | float):
        return float(teks)
    t = _bersihkan(str(teks))
    if t in PECAHAN_UNICODE:
        return PECAHAN_UNICODE[t]
    if t.count("/") == 1:
        atas, bawah = t.split("/")
        a, b = _ke_angka(atas), _ke_angka(bawah)
        if a is None or b is None or b == 0:
            return None
        return a / b
    return _ke_angka(t)


def parse_satuan(teks: str | None) -> str | None:
    """Normalkan satuan: 'cm2' / 'cm^2' / 'cm²' -> 'cm²'."""
    if not teks:
        return None
    t = str(teks).strip().lower().replace(" ", "")
    if t == "rp":
        return "Rp"
    m = re.fullmatch(r"(cm|mm|m)(\^?2|²)?", t)
    if not m:
        return None
    return m.group(1) + ("²" if m.group(2) else "")


def samakah(nilai: float, target: float, toleransi: float = TOLERANSI_RELATIF) -> bool:
    """Bandingkan dua angka dengan toleransi relatif."""
    if target == 0:
        return abs(nilai) < 1e-9
    return abs(nilai - target) / abs(target) <= toleransi


def format_angka(nilai: float) -> str:
    """Tulis angka dalam format Indonesia: 1200 -> '1.200', 1.8 -> '1,8'."""
    if abs(nilai - round(nilai)) < 1e-9:
        return f"{round(nilai):,}".replace(",", ".")
    teks = f"{nilai:,.2f}".rstrip("0").rstrip(".")
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")
