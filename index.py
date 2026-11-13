"""Titik masuk untuk Vercel (serverless).

Vercel mencari objek `app` di file ini. Server lokal tetap dijalankan dengan
`python backend/app.py`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

FOLDER_BACKEND = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(FOLDER_BACKEND))

from app import buat_app  # noqa: E402  (backend/app.py)

_DI_VERCEL = bool(os.environ.get("VERCEL"))

app = buat_app(
    {
        # Di Vercel hanya folder /tmp yang boleh ditulis. Data di sini SEMENTARA:
        # bisa hilang saat server tidur atau berpindah instance.
        "DB_PATH": (
            "/tmp/segipintar.db" if _DI_VERCEL else str(FOLDER_BACKEND / "data" / "segipintar.db")
        ),
        # Karena progres bisa hilang, semua misi dibuka agar siswa tidak terkunci.
        "MISI_BEBAS": os.environ.get("SEGIPINTAR_MISI_BEBAS", "1" if _DI_VERCEL else "0") == "1",
        # Halaman guru hanya aktif jika PIN diatur di Environment Variables Vercel.
        "PIN_GURU": os.environ.get("SEGIPINTAR_PIN_GURU") or (None if _DI_VERCEL else "1234"),
    }
)
