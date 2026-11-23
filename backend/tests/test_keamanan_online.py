"""Tes pengaman versi online: PIN guru, kunci PIN, batas laju, header, proxy, wsgi."""

import importlib
import sys
from pathlib import Path

import pytest

from app import buat_app
from asisten.klien import KlienTiruan
from asisten.konfigurasi import KonfigurasiAsisten

AKAR = Path(__file__).resolve().parents[2]


def _app(tmp_path, **lain):
    return buat_app({"DB_PATH": str(tmp_path / "uji.db"), "TESTING": True, **lain})


def _sesi(c, nama="Ani"):
    r = c.post("/api/sesi", json={"nama_panggilan": nama, "kode_kelas": "8A"})
    return r


# ------------------------------------------------------------------ PIN guru
@pytest.mark.parametrize(("pin", "aktif"), [(None, False), ("1234", False), ("guru2026x", True)])
def test_pin_guru_di_produksi(tmp_path, monkeypatch, pin, aktif):
    monkeypatch.setenv("SEGIPINTAR_PRODUKSI", "1")
    if pin is None:
        monkeypatch.delenv("SEGIPINTAR_PIN_GURU", raising=False)
    else:
        monkeypatch.setenv("SEGIPINTAR_PIN_GURU", pin)
    app = _app(tmp_path)
    assert (app.config["PIN_GURU"] is not None) is aktif
    r = app.test_client().post("/api/guru", json={"kode_kelas": "8A", "pin": pin or ""})
    assert r.status_code == (200 if aktif else 403)


def test_lokal_tetap_memakai_pin_bawaan(tmp_path, monkeypatch):
    monkeypatch.delenv("SEGIPINTAR_PRODUKSI", raising=False)
    monkeypatch.delenv("SEGIPINTAR_PIN_GURU", raising=False)
    assert _app(tmp_path).config["PIN_GURU"] == "1234"


def test_pin_salah_berkali_kali_dikunci(tmp_path):
    c = _app(tmp_path, PIN_GURU="rahasia99").test_client()
    for _ in range(5):
        assert c.post("/api/guru", json={"kode_kelas": "8A", "pin": "salah"}).status_code == 403
    # setelah 5 kali salah, PIN benar pun ditolak sementara
    r = c.post("/api/guru", json={"kode_kelas": "8A", "pin": "rahasia99"})
    assert r.status_code == 429 and "15 menit" in r.get_json()["galat"]


def test_pin_benar_tidak_menambah_hitungan(tmp_path):
    c = _app(tmp_path, PIN_GURU="rahasia99").test_client()
    for _ in range(10):
        assert c.post("/api/guru", json={"kode_kelas": "8A", "pin": "rahasia99"}).status_code == 200


# ------------------------------------------------------------------ batas laju
def test_batas_laju_pembuatan_sesi(tmp_path):
    c = _app(tmp_path, BATAS_SESI_PER_IP=3).test_client()
    assert [_sesi(c).status_code for _ in range(4)] == [200, 200, 200, 429]
    assert c.get("/api/misi").status_code == 200  # jalur lain tidak terpengaruh


def test_batas_laju_chatbot_per_ip(tmp_path):
    app = _app(
        tmp_path,
        BATAS_ASISTEN_PER_IP=2,
        ASISTEN=KonfigurasiAsisten(mode="tiruan"),
        ASISTEN_KLIEN=KlienTiruan(lambda p: "Jadi, luasnya 30 cm²."),
    )
    c = app.test_client()
    s = _sesi(c).get_json()["sesi_id"]
    kode = [
        c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "hitung"}).status_code
        for _ in range(3)
    ]
    assert kode == [200, 200, 429]
    r = c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "hitung"})
    assert r.is_json and "Terlalu banyak permintaan" in r.get_json()["galat"]


def test_ip_berbeda_dihitung_terpisah_di_balik_proxy(tmp_path, monkeypatch):
    monkeypatch.setenv("SEGIPINTAR_DI_BELAKANG_PROXY", "1")
    c = _app(tmp_path, BATAS_SESI_PER_IP=1).test_client()
    satu = {"X-Forwarded-For": "203.0.113.1"}
    dua = {"X-Forwarded-For": "203.0.113.2"}
    kirim = {"nama_panggilan": "A", "kode_kelas": "8A"}
    assert c.post("/api/sesi", json=kirim, headers=satu).status_code == 200
    assert c.post("/api/sesi", json=kirim, headers=satu).status_code == 429
    assert c.post("/api/sesi", json=kirim, headers=dua).status_code == 200


def test_tanpa_mode_proxy_header_palsu_diabaikan(tmp_path, monkeypatch):
    monkeypatch.delenv("SEGIPINTAR_DI_BELAKANG_PROXY", raising=False)
    c = _app(tmp_path, BATAS_SESI_PER_IP=1).test_client()
    kirim = {"nama_panggilan": "A", "kode_kelas": "8A"}
    assert (
        c.post("/api/sesi", json=kirim, headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    )
    assert (
        c.post("/api/sesi", json=kirim, headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 429
    )


# ------------------------------------------------------------------ header & ukuran
def test_header_keamanan(tmp_path):
    c = _app(tmp_path).test_client()
    h = c.get("/").headers
    assert "default-src 'self'" in h["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"]
    assert h["X-Content-Type-Options"] == "nosniff" and h["X-Frame-Options"] == "DENY"
    assert c.get("/api/misi").headers["Cache-Control"] == "no-store"


def test_kiriman_terlalu_besar_ditolak(tmp_path):
    c = _app(tmp_path).test_client()
    r = c.post("/api/sesi", json={"nama_panggilan": "x" * 100_000, "kode_kelas": "8A"})
    assert r.status_code == 413


# ------------------------------------------------------------------ wsgi.py
def test_wsgi_membuat_aplikasi_produksi(tmp_path, monkeypatch):
    monkeypatch.setenv("SEGIPINTAR_DB_PATH", str(tmp_path / "online.db"))
    monkeypatch.setenv("SEGIPINTAR_PIN_GURU", "guruonline1")
    # wsgi.py memakai os.environ.setdefault. Nilai diset lewat monkeypatch agar DIKEMBALIKAN
    # setelah tes; tanpa ini mode produksi "bocor" ke tes-tes berikutnya.
    monkeypatch.setenv("SEGIPINTAR_PRODUKSI", "1")
    monkeypatch.setenv("SEGIPINTAR_DI_BELAKANG_PROXY", "1")
    monkeypatch.syspath_prepend(str(AKAR))
    sys.modules.pop("wsgi", None)
    wsgi = importlib.import_module("wsgi")
    app = wsgi.application
    assert app.config["PRODUKSI"] is True
    assert app.config["DB_PATH"] == str(tmp_path / "online.db")
    assert app.config["PIN_GURU"] == "guruonline1"
    c = app.test_client()
    assert c.get("/").status_code == 200 and c.get("/js/main.js").status_code == 200
    sys.modules.pop("wsgi", None)
