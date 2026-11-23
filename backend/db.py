"""Koneksi dan skema SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SKEMA = """
CREATE TABLE IF NOT EXISTS sesi (
    id TEXT PRIMARY KEY,
    nama_panggilan TEXT NOT NULL,
    kode_kelas TEXT NOT NULL,
    dibuat TEXT NOT NULL
);

-- Satu baris = satu kali siswa memainkan satu misi.
CREATE TABLE IF NOT EXISTS main_misi (
    id TEXT PRIMARY KEY,
    sesi_id TEXT NOT NULL REFERENCES sesi(id),
    misi_id INTEGER NOT NULL,
    mulai TEXT NOT NULL,
    selesai TEXT,
    skor_rubrik REAL,
    rincian TEXT,
    bintang INTEGER,
    total_petunjuk INTEGER
);

CREATE TABLE IF NOT EXISTS jawaban_langkah (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_id TEXT NOT NULL REFERENCES main_misi(id),
    langkah TEXT NOT NULL,
    percobaan_ke INTEGER NOT NULL,
    jawaban TEXT NOT NULL,
    benar INTEGER NOT NULL,
    kode_diagnosis TEXT,
    waktu TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS petunjuk_dibuka (
    main_id TEXT NOT NULL REFERENCES main_misi(id),
    langkah TEXT NOT NULL,
    tingkat INTEGER NOT NULL,
    otomatis INTEGER NOT NULL DEFAULT 0,
    waktu TEXT NOT NULL,
    PRIMARY KEY (main_id, langkah, tingkat)
);

CREATE TABLE IF NOT EXISTS refleksi (
    main_id TEXT NOT NULL REFERENCES main_misi(id),
    teks TEXT NOT NULL,
    waktu TEXT NOT NULL
);

-- Riwayat chatbot di dalam misi.
CREATE TABLE IF NOT EXISTS percakapan_asisten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_id TEXT NOT NULL REFERENCES main_misi(id),
    kode_anonim TEXT NOT NULL,
    misi_id INTEGER NOT NULL,
    langkah TEXT NOT NULL,
    peran TEXT NOT NULL CHECK (peran IN ('siswa', 'asisten')),
    teks TEXT NOT NULL,
    teks_asli TEXT,
    disamarkan INTEGER NOT NULL DEFAULT 0,
    disaring INTEGER NOT NULL DEFAULT 0,
    alasan_saring TEXT,
    langkah_benar INTEGER NOT NULL DEFAULT 0,
    percobaan_salah INTEGER NOT NULL DEFAULT 0,
    tingkat_petunjuk INTEGER NOT NULL DEFAULT 0,
    kode_diagnosis TEXT,
    tingkat_bantuan INTEGER,
    tahap_rmt TEXT,
    fase_kognitif TEXT,
    sumber TEXT,
    model TEXT,
    token_masuk INTEGER,
    token_keluar INTEGER,
    durasi_ms INTEGER,
    waktu TEXT NOT NULL
);

-- Riwayat chatbot di beranda.
-- Terpisah dari misi dan tidak memengaruhi skor.
CREATE TABLE IF NOT EXISTS percakapan_beranda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sesi_id TEXT NOT NULL REFERENCES sesi(id),
    kode_anonim TEXT NOT NULL,
    peran TEXT NOT NULL CHECK (peran IN ('siswa', 'asisten')),
    teks TEXT NOT NULL,
    disamarkan INTEGER NOT NULL DEFAULT 0,
    sumber TEXT,
    model TEXT,
    token_masuk INTEGER,
    token_keluar INTEGER,
    durasi_ms INTEGER,
    waktu TEXT NOT NULL
);

-- Respons aktivitas pendamping RMT (Tahap 2A). TIDAK memengaruhi skor rubrik.
-- Tanpa nama siswa: hanya kode anonim. Teks bebas disamarkan sebelum disimpan.
CREATE TABLE IF NOT EXISTS aktivitas_rmt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_id TEXT NOT NULL REFERENCES main_misi(id),
    kode_anonim TEXT NOT NULL,
    misi_id INTEGER NOT NULL,
    aktivitas TEXT NOT NULL,
    tahap_rmt TEXT NOT NULL,
    percobaan_ke INTEGER NOT NULL,
    jawaban TEXT,
    dilewati INTEGER NOT NULL DEFAULT 0,
    benar INTEGER,
    waktu TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_main_sesi
ON main_misi(sesi_id);

CREATE INDEX IF NOT EXISTS idx_jawaban_main
ON jawaban_langkah(main_id);

CREATE INDEX IF NOT EXISTS idx_sesi_kelas
ON sesi(kode_kelas);

CREATE INDEX IF NOT EXISTS idx_asisten_main
ON percakapan_asisten(main_id, langkah);

CREATE INDEX IF NOT EXISTS idx_beranda_sesi
ON percakapan_beranda(sesi_id, id);

CREATE INDEX IF NOT EXISTS idx_aktivitas_rmt_main
ON aktivitas_rmt(main_id, aktivitas);
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
