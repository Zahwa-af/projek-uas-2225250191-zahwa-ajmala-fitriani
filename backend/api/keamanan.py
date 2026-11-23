"""Pengaman untuk versi online (internet publik).

- Batas laju per alamat IP: mencegah orang asing menghabiskan kuota AI atau membanjiri
  pembuatan sesi.
- Kunci sementara setelah PIN guru salah berkali-kali (mencegah tebak-tebakan PIN).
- Header keamanan browser (CSP, nosniff, larangan dibingkai situs lain).

Penyimpanan hitungan ada di memori proses. Cukup untuk satu proses server
(PythonAnywhere gratis / laptop); hitungan kembali nol saat server di-restart.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Any

from flask import current_app, jsonify, request

KUNCI_EKSTENSI = "segipintar_pembatas"

PESAN_TERLALU_BANYAK = "Terlalu banyak permintaan. Tunggu beberapa menit, lalu coba lagi."

# Aturan keamanan browser. Frontend tidak memakai skrip/CSS/font eksternal,
# innerHTML, maupun eval (sudah diperiksa), jadi kebijakan ketat ini aman.
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "connect-src 'self'; font-src 'self'; manifest-src 'self'; object-src 'none'; "
    "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
)


class PembatasLaju:
    """Jendela geser sederhana: paling banyak `maks` kejadian per `detik` untuk tiap kunci."""

    def __init__(self, maks: int, detik: float) -> None:
        self.maks = maks
        self.detik = detik
        self._catatan: dict[str, deque[float]] = defaultdict(deque)
        self._kunci = threading.Lock()

    def _bersihkan(self, antrean: deque[float], sekarang: float) -> None:
        while antrean and sekarang - antrean[0] > self.detik:
            antrean.popleft()

    def penuh(self, kunci: str) -> bool:
        with self._kunci:
            antrean = self._catatan[kunci]
            self._bersihkan(antrean, time.monotonic())
            return len(antrean) >= self.maks

    def catat(self, kunci: str) -> None:
        with self._kunci:
            antrean = self._catatan[kunci]
            sekarang = time.monotonic()
            self._bersihkan(antrean, sekarang)
            antrean.append(sekarang)

    def izinkan(self, kunci: str) -> bool:
        """Catat satu kejadian bila masih di bawah batas. False jika batas tercapai."""
        with self._kunci:
            antrean = self._catatan[kunci]
            sekarang = time.monotonic()
            self._bersihkan(antrean, sekarang)
            if len(antrean) >= self.maks:
                return False
            antrean.append(sekarang)
            return True


def ip_klien() -> str:
    # Di balik proxy hosting, ProxyFix (dipasang di app.py) sudah mengisi remote_addr
    # dengan IP pengunjung yang sebenarnya.
    return request.remote_addr or "tidak-diketahui"


def _pembatas(nama: str) -> PembatasLaju:
    return current_app.extensions[KUNCI_EKSTENSI][nama]


def pin_terkunci() -> bool:
    return _pembatas("gagal_pin").penuh(ip_klien())


def catat_pin_salah() -> None:
    _pembatas("gagal_pin").catat(ip_klien())


# Jalur yang dibatasi: (metode, awalan jalur) -> nama pembatas
_JALUR_DIBATASI = {
    ("POST", "/api/asisten/"): "asisten",
    ("POST", "/api/sesi"): "sesi",
    ("POST", "/api/rmt/"): "aktivitas",
    ("POST", "/api/latihan/"): "aktivitas",
}


def pasang_keamanan(app: Any) -> None:
    c = app.config
    app.extensions[KUNCI_EKSTENSI] = {
        "asisten": PembatasLaju(c["BATAS_ASISTEN_PER_IP"], c["BATAS_ASISTEN_DETIK"]),
        "sesi": PembatasLaju(c["BATAS_SESI_PER_IP"], c["BATAS_SESI_DETIK"]),
        "aktivitas": PembatasLaju(c["BATAS_AKTIVITAS_PER_IP"], c["BATAS_AKTIVITAS_DETIK"]),
        "gagal_pin": PembatasLaju(c["BATAS_GAGAL_PIN"], c["BATAS_GAGAL_PIN_DETIK"]),
    }

    @app.before_request
    def _batasi_laju():  # type: ignore[no-untyped-def]
        for (metode, awalan), nama in _JALUR_DIBATASI.items():
            if request.method == metode and request.path.startswith(awalan):
                if not _pembatas(nama).izinkan(ip_klien()):
                    return (
                        jsonify({"galat": PESAN_TERLALU_BANYAK}),
                        429,
                    )
        return None

    @app.after_request
    def _header_keamanan(respons):  # type: ignore[no-untyped-def]
        h = respons.headers
        h.setdefault("Content-Security-Policy", CSP)
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "no-referrer")
        h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if request.path.startswith("/api/"):
            h.setdefault("Cache-Control", "no-store")  # data siswa tidak disimpan di cache
        return respons
