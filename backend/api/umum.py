"""Fungsi bantu bersama untuk semua route API."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any

from flask import current_app, g, jsonify, request

import db
from segitiga.penilai import StatusLangkah


class GalatApi(Exception):
    def __init__(self, pesan: str, status: int = 400) -> None:
        super().__init__(pesan)
        self.pesan = pesan
        self.status = status


def koneksi() -> sqlite3.Connection:
    if "db" not in g:
        g.db = db.hubungkan(current_app.config["DB_PATH"])
    return g.db


def tutup_koneksi(_exc: BaseException | None = None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def sekarang() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def data_json() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise GalatApi("Data yang dikirim tidak valid.")
    return data


def teks_wajib(data: dict[str, Any], kunci: str, label: str, maks: int) -> str:
    nilai = str(data.get(kunci) or "").strip()
    if not nilai:
        raise GalatApi(f"{label} belum diisi.")
    if len(nilai) > maks:
        raise GalatApi(f"{label} terlalu panjang (maksimal {maks} huruf).")
    return nilai


def ambil_main(main_id: Any) -> sqlite3.Row:
    row = koneksi().execute("SELECT * FROM main_misi WHERE id = ?", (str(main_id),)).fetchone()
    if row is None:
        raise GalatApi("Permainan misi tidak ditemukan. Mulai ulang misinya.", 404)
    return row


def status_langkah(main_id: str) -> dict[str, StatusLangkah]:
    """Status setiap langkah dalam satu permainan misi (dari database)."""
    conn = koneksi()
    status: dict[str, StatusLangkah] = {}
    for r in conn.execute(
        "SELECT langkah, MAX(benar) AS benar FROM jawaban_langkah WHERE main_id = ? "
        "GROUP BY langkah",
        (main_id,),
    ):
        status.setdefault(r["langkah"], StatusLangkah()).benar = bool(r["benar"])
    for r in conn.execute(
        "SELECT langkah, MAX(tingkat) AS tingkat FROM petunjuk_dibuka WHERE main_id = ? "
        "GROUP BY langkah",
        (main_id,),
    ):
        status.setdefault(r["langkah"], StatusLangkah()).tingkat_petunjuk = int(r["tingkat"])
    return status


def daftarkan_penangan_galat(app: Any) -> None:
    @app.errorhandler(GalatApi)
    def _galat_api(e: GalatApi):  # type: ignore[no-untyped-def]
        return jsonify({"galat": e.pesan}), e.status

    app.teardown_appcontext(tutup_koneksi)
