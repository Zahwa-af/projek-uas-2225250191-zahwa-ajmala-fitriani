"""Server Flask SegiPintar.

Jalankan:  python backend/app.py
Lalu buka http://localhost:5000 (laptop) atau http://<IP-laptop>:5000 (HP di Wi-Fi yang sama).
"""

from __future__ import annotations

import mimetypes
import os
import socket
import sys
from pathlib import Path
from typing import Any

from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

FOLDER_BACKEND = Path(__file__).resolve().parent
if str(FOLDER_BACKEND) not in sys.path:
    sys.path.insert(0, str(FOLDER_BACKEND))

try:
    from dotenv import load_dotenv

    # Rahasia (API key DeepSeek, PIN guru) dibaca dari .env di folder proyek.
    # override=False: variabel lingkungan sistem/Vercel tetap diutamakan.
    load_dotenv(FOLDER_BACKEND.parent / ".env", override=False)
except ImportError:  # python-dotenv opsional; Vercel memakai Environment Variables
    pass

import db  # noqa: E402
from api import (  # noqa: E402
    routes_asisten,
    routes_periksa,
    routes_progres,
    routes_rmt,
    routes_soal,
)
from api.keamanan import pasang_keamanan  # noqa: E402
from api.umum import daftarkan_penangan_galat  # noqa: E402
from asisten.klien import buat_klien  # noqa: E402
from asisten.konfigurasi import dari_env  # noqa: E402

FOLDER_FRONTEND = FOLDER_BACKEND.parent / "frontend"
DB_BAWAAN = FOLDER_BACKEND / "data" / "segipintar.db"
PIN_BAWAAN = "1234"

# Windows kadang memetakan .js ke text/plain sehingga ES module gagal dimuat.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/manifest+json", ".webmanifest")


PIN_PRODUKSI_MIN = 6  # panjang minimal PIN guru di versi online


def _pin_guru(produksi: bool) -> str | None:
    """PIN guru dari env. Di versi online: wajib diisi dan minimal 6 karakter.

    Jika tidak memenuhi syarat, halaman guru DIMATIKAN (bukan memakai PIN bawaan 1234),
    karena di internet PIN pendek mudah ditebak.
    """
    pin = (os.environ.get("SEGIPINTAR_PIN_GURU") or "").strip()
    if not produksi:
        return pin or PIN_BAWAAN
    if len(pin) < PIN_PRODUKSI_MIN:
        return None
    return pin


def buat_app(konfigurasi: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(FOLDER_FRONTEND), static_url_path="")
    produksi = os.environ.get("SEGIPINTAR_PRODUKSI") == "1"
    app.config.update(
        PRODUKSI=produksi,
        DB_PATH=os.environ.get("SEGIPINTAR_DB_PATH") or str(DB_BAWAAN),
        PIN_GURU=_pin_guru(produksi),
        MISI_BEBAS=os.environ.get("SEGIPINTAR_MISI_BEBAS") == "1",
        # Lokal: selalu muat file terbaru. Online: izinkan browser menyimpan 1 jam.
        SEND_FILE_MAX_AGE_DEFAULT=3600 if produksi else 0,
        JSON_AS_ASCII=False,
        MAX_CONTENT_LENGTH=64 * 1024,  # permintaan JSON siswa kecil; tolak kiriman raksasa
        # Batas laju per IP (lihat api/keamanan.py)
        BATAS_ASISTEN_PER_IP=30,
        BATAS_ASISTEN_DETIK=10 * 60,
        BATAS_SESI_PER_IP=30,
        BATAS_SESI_DETIK=60 * 60,
        # Aktivitas tanpa skor (respons RMT, latihan). Longgar karena satu kelas bisa berbagi
        # satu IP sekolah; tujuannya menahan banjir otomatis, bukan membatasi siswa.
        BATAS_AKTIVITAS_PER_IP=900,
        BATAS_AKTIVITAS_DETIK=10 * 60,
        BATAS_GAGAL_PIN=5,
        BATAS_GAGAL_PIN_DETIK=15 * 60,
    )
    app.json.ensure_ascii = False  # type: ignore[attr-defined]
    if konfigurasi:
        app.config.update(konfigurasi)

    if produksi and app.config["PIN_GURU"] is None:
        app.logger.warning(
            "Halaman guru dimatikan: SEGIPINTAR_PIN_GURU kosong atau kurang dari %d karakter.",
            PIN_PRODUKSI_MIN,
        )
    if os.environ.get("SEGIPINTAR_DI_BELAKANG_PROXY") == "1":
        # Hosting (PythonAnywhere) meneruskan IP pengunjung lewat header X-Forwarded-For.
        # Hanya diaktifkan di hosting; di laptop header itu bisa dipalsukan.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[method-assign]
    pasang_keamanan(app)

    # Chatbot: konfigurasi dari env, kecuali tes memberi ASISTEN / ASISTEN_KLIEN sendiri.
    if "ASISTEN" not in app.config:
        app.config["ASISTEN"] = dari_env()
    for pesan in app.config["ASISTEN"].peringatan:
        app.logger.warning(pesan)
    klien = app.config.get("ASISTEN_KLIEN") or buat_klien(app.config["ASISTEN"])
    if klien is not None:
        app.extensions[routes_asisten.KUNCI_KLIEN] = klien

    db.siapkan(app.config["DB_PATH"])
    daftarkan_penangan_galat(app)
    app.register_blueprint(routes_soal.bp)
    app.register_blueprint(routes_periksa.bp)
    app.register_blueprint(routes_progres.bp)
    app.register_blueprint(routes_asisten.bp)
    app.register_blueprint(routes_rmt.bp)  # aktivitas pendamping RMT (tanpa skor)

    @app.get("/")
    def beranda():  # type: ignore[no-untyped-def]
        return send_from_directory(FOLDER_FRONTEND, "index.html")

    return app


def _ip_lokal() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # tidak mengirim data apa pun
            return s.getsockname()[0]
    except OSError:
        return None


def port_sudah_dipakai(port: int) -> bool:
    """True jika sudah ada server yang menerima koneksi di port ini.

    Di Windows, dua server Flask bisa sama-sama "mendengarkan" port 5000 tanpa error.
    Permintaan browser lalu jatuh acak ke server lama (kode lama) atau server baru,
    sehingga perubahan kode seolah tidak berpengaruh.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    if port_sudah_dipakai(port):
        print(f"\n  GAGAL: port {port} sudah dipakai server lain.")
        print("  Kemungkinan SegiPintar versi lama masih berjalan di jendela terminal lain.")
        print("  Tutup server lama (Ctrl+C di jendela itu), lalu jalankan ulang perintah ini.\n")
        raise SystemExit(1)
    app = buat_app()
    print("\n  SegiPintar berjalan.")
    print(f"  Laptop : http://localhost:{port}")
    ip = _ip_lokal()
    if ip:
        print(f"  HP     : http://{ip}:{port}  (HP harus di Wi-Fi yang sama)")
    if app.config["PIN_GURU"] == PIN_BAWAAN:
        print("  PERINGATAN: PIN guru masih bawaan (1234). Atur SEGIPINTAR_PIN_GURU.")
    asisten = app.config["ASISTEN"]
    keterangan = f" (model {asisten.model})" if asisten.mode == "deepseek" else ""
    print(f"  Pembimbing AI: {asisten.mode}{keterangan}")  # API key tidak pernah dicetak
    for pesan in asisten.peringatan:
        print(f"  PERINGATAN: {pesan}")
    print()
    app.run(host="0.0.0.0", port=port, debug=False)
