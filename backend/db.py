"""Koneksi dan skema SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SKEMA = """
CREATE TABLE IF NOT EXISTS sesi (
  id             TEXT PRIMARY KEY,
  nama_panggilan TEXT NOT NULL,
  kode_kelas     TEXT NOT NULL,
  dibuat         TEXT NOT NULL
);

-- Satu baris = satu kali siswa memainkan satu misi.
CREATE TABLE IF NOT EXISTS main_misi (
  id             TEXT PRIMARY KEY,
  sesi_id        TEXT NOT NULL REFERENCES sesi(id),
  misi_id        INTEGER NOT NULL,
  mulai          TEXT NOT NULL,
  selesai        TEXT,
  skor_rubrik    REAL,
  rincian        TEXT,
  bintang        INTEGER,
  total_petunjuk INTEGER
);

CREATE TABLE IF NOT EXISTS jawaban_langkah (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  main_id        TEXT NOT NULL REFERENCES main_misi(id),
  langkah        TEXT NOT NULL,
  percobaan_ke   INTEGER NOT NULL,
  jawaban        TEXT NOT NULL,
  benar          INTEGER NOT NULL,
  kode_diagnosis TEXT,
  waktu          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS petunjuk_dibuka (
  main_id  TEXT NOT NULL REFERENCES main_misi(id),
  langkah  TEXT NOT NULL,
  tingkat  INTEGER NOT NULL,
  otomatis INTEGER NOT NULL DEFAULT 0,
  waktu    TEXT NOT NULL,
  PRIMARY KEY (main_id, langkah, tingkat)
);

CREATE TABLE IF NOT EXISTS refleksi (
  main_id TEXT NOT NULL REFERENCES main_misi(id),
  teks    TEXT NOT NULL,
  waktu   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_main_sesi ON main_misi(sesi_id);
CREATE INDEX IF NOT EXISTS idx_jawaban_main ON jawaban_langkah(main_id);
CREATE INDEX IF NOT EXISTS idx_sesi_kelas ON sesi(kode_kelas);
"""


def hubungkan(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def siapkan(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = hubungkan(path)
    try:
        conn.executescript(SKEMA)
        conn.commit()
    finally:
        conn.close()
