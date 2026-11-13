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

FOLDER_BACKEND = Path(__file__).resolve().parent
if str(FOLDER_BACKEND) not in sys.path:
    sys.path.insert(0, str(FOLDER_BACKEND))

import db  # noqa: E402
from api import routes_periksa, routes_progres, routes_soal  # noqa: E402
from api.umum import daftarkan_penangan_galat  # noqa: E402

FOLDER_FRONTEND = FOLDER_BACKEND.parent / "frontend"
DB_BAWAAN = FOLDER_BACKEND / "data" / "segipintar.db"
PIN_BAWAAN = "1234"

# Windows kadang memetakan .js ke text/plain sehingga ES module gagal dimuat.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/manifest+json", ".webmanifest")


def buat_app(konfigurasi: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(FOLDER_FRONTEND), static_url_path="")
    app.config.update(
        DB_PATH=str(DB_BAWAAN),
        PIN_GURU=os.environ.get("SEGIPINTAR_PIN_GURU", PIN_BAWAAN),
        MISI_BEBAS=os.environ.get("SEGIPINTAR_MISI_BEBAS") == "1",
        SEND_FILE_MAX_AGE_DEFAULT=0,  # selalu muat file terbaru saat pengembangan
        JSON_AS_ASCII=False,
    )
    app.json.ensure_ascii = False  # type: ignore[attr-defined]
    if konfigurasi:
        app.config.update(konfigurasi)

    db.siapkan(app.config["DB_PATH"])
    daftarkan_penangan_galat(app)
    app.register_blueprint(routes_soal.bp)
    app.register_blueprint(routes_periksa.bp)
    app.register_blueprint(routes_progres.bp)

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


if __name__ == "__main__":
    app = buat_app()
    port = int(os.environ.get("PORT", "5000"))
    print("\n  SegiPintar berjalan.")
    print(f"  Laptop : http://localhost:{port}")
    ip = _ip_lokal()
    if ip:
        print(f"  HP     : http://{ip}:{port}  (HP harus di Wi-Fi yang sama)")
    if app.config["PIN_GURU"] == PIN_BAWAAN:
        print("  PERINGATAN: PIN guru masih bawaan (1234). Atur SEGIPINTAR_PIN_GURU.")
    print()
    app.run(host="0.0.0.0", port=port, debug=False)
