"""Titik masuk server ONLINE (PythonAnywhere).

File konfigurasi WSGI di PythonAnywhere cukup berisi:

    import sys
    sys.path.insert(0, "/home/NAMA_PENGGUNA/NAMA_FOLDER_PROYEK")
    from wsgi import application

Rahasia (API key, PIN guru) dibaca dari file .env di folder proyek DI SERVER.
File .env itu dibuat langsung di PythonAnywhere dan TIDAK pernah masuk GitHub.
Panduan lengkap: docs/11-deploy-pythonanywhere.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent

# Mode online: PIN guru wajib kuat, header & batas laju aktif, IP dibaca dari proxy hosting.
os.environ.setdefault("SEGIPINTAR_PRODUKSI", "1")
os.environ.setdefault("SEGIPINTAR_DI_BELAKANG_PROXY", "1")

sys.path.insert(0, str(AKAR / "backend"))

from app import buat_app  # noqa: E402  (backend/app.py; ikut memuat AKAR/.env)

application = buat_app()
