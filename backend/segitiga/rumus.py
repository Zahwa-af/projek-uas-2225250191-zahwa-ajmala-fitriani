"""Rumus dasar segitiga."""

from __future__ import annotations

_EPS = 1e-9


def luas_segitiga(alas: float, tinggi: float) -> float:
    """L = ½ × alas × tinggi."""
    if alas <= 0 or tinggi <= 0:
        raise ValueError("Alas dan tinggi harus lebih dari 0.")
    return 0.5 * alas * tinggi


def adalah_segitiga(a: float, b: float, c: float) -> bool:
    """Cek ketaksamaan segitiga: jumlah dua sisi selalu lebih dari sisi ketiga."""
    x, y, z = sorted((a, b, c))
    return x > 0 and x + y > z + _EPS


def keliling_segitiga(a: float, b: float, c: float) -> float:
    """K = sisi 1 + sisi 2 + sisi 3."""
    if not adalah_segitiga(a, b, c):
        raise ValueError("Ketiga sisi tidak membentuk segitiga.")
    return a + b + c


def jenis_menurut_sisi(a: float, b: float, c: float) -> str:
    if not adalah_segitiga(a, b, c):
        raise ValueError("Ketiga sisi tidak membentuk segitiga.")
    if abs(a - b) < _EPS and abs(b - c) < _EPS:
        return "sama sisi"
    if abs(a - b) < _EPS or abs(b - c) < _EPS or abs(a - c) < _EPS:
        return "sama kaki"
    return "sembarang"


def jenis_menurut_sudut(a: float, b: float, c: float) -> str:
    if not adalah_segitiga(a, b, c):
        raise ValueError("Ketiga sisi tidak membentuk segitiga.")
    x, y, z = sorted((a, b, c))
    selisih = x * x + y * y - z * z
    if abs(selisih) < 1e-6 * z * z:
        return "siku-siku"
    return "lancip" if selisih > 0 else "tumpul"
