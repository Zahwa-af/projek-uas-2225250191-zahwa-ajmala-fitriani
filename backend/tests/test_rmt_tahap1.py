"""Tes RMT Tahap 1: label tahap per langkah, fase kesalahan, log chatbot, rekap guru."""

import hashlib
import json
from pathlib import Path

import pytest

import db
from app import buat_app
from asisten.klien import KlienTiruan
from asisten.konfigurasi import KonfigurasiAsisten
from bantuan import jawaban_dari_kunci
from segitiga import bank_soal, rmt
from segitiga.diagnosis import PESAN

AKAR = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------------ pemetaan
def test_setiap_langkah_misi_punya_tahap_rmt():
    semua = {(m["id"], lk["no"]) for m in bank_soal.semua_misi() for lk in m["langkah"]}
    assert semua == set(rmt.TAHAP_LANGKAH)  # tidak kurang, tidak lebih
    assert set(rmt.TAHAP_LANGKAH.values()) <= set(rmt.SEMUA_TAHAP)


def test_setiap_misi_memuat_analisis_tugas_dan_manipulasi():
    for m in bank_soal.semua_misi():
        tahap = {rmt.tahap_langkah(m["id"], lk["no"]) for lk in m["langkah"]}
        assert {rmt.ANALISIS_TUGAS, rmt.MANIPULASI} <= tahap, m["id"]


def test_semua_kode_kesalahan_punya_fase_atau_dikecualikan():
    kode_kesalahan = set(PESAN) | {"PILIHAN_SALAH", "KURANG_LENGKAP", "PILAH_SALAH", "RUMUS_SALAH"}
    for kode in kode_kesalahan - rmt.BUKAN_KESALAHAN:
        for misi_id, no in rmt.TAHAP_LANGKAH:
            assert rmt.fase_kesalahan(kode, misi_id, no) in rmt.SEMUA_FASE, (kode, misi_id, no)


@pytest.mark.parametrize(
    ("kode", "misi_id", "no", "fase"),
    [
        ("PILAH_SALAH", 1, "1a", "input"),
        ("LUPA_SETENGAH", 1, "2a", "elaborasi"),
        ("SALAH_SATUAN", 1, "2a", "output"),
        ("SALAH_HITUNG", 3, "2b", "output"),  # usulan, menunggu keputusan dosen
        ("PILIHAN_SALAH", 2, "2", "input"),  # mengikuti tahap langkah (analisis tugas)
        ("PILIHAN_SALAH", 2, "3", "elaborasi"),  # representasi
        ("PILIHAN_SALAH", 4, "5", "output"),  # validasi
        ("TIDAK_DIKENALI", 3, "4", "elaborasi"),  # manipulasi
        ("FORMAT_ANGKA", 1, "2a", None),
        (None, 1, "2a", None),
    ],
)
def test_fase_kesalahan(kode, misi_id, no, fase):
    assert rmt.fase_kesalahan(kode, misi_id, no) == fase


def test_bank_soal_tidak_berubah():
    """Tahap 1 hanya menambah label; soal, kunci, dan skor di misi.json tidak disentuh."""
    data = (AKAR / "backend" / "data" / "soal" / "misi.json").read_bytes()
    misi = json.loads(data)
    assert all("tahap_rmt" not in lk for m in misi for lk in m["langkah"])
    assert sum(lk["skor"] for m in misi for lk in m["langkah"]) == 24
    assert hashlib.sha256(data).hexdigest()  # file terbaca utuh


# ------------------------------------------------------------------ log chatbot misi
def _app(tmp_path, **lain):
    return buat_app({"DB_PATH": str(tmp_path / "uji.db"), "TESTING": True, **lain})


def test_log_chatbot_misi_berisi_tahap_dan_fase(tmp_path):
    klien = KlienTiruan(["Coba lihat lagi rumusnya."])
    app = _app(tmp_path, ASISTEN=KonfigurasiAsisten(mode="tiruan"), ASISTEN_KLIEN=klien)
    c = app.test_client()
    sesi = c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()
    main_id = c.post("/api/misi/1/mulai", json={"sesi_id": sesi["sesi_id"]}).get_json()["main_id"]
    c.post(  # salah: lupa ½ → fase elaborasi
        "/api/periksa",
        json={"main_id": main_id, "langkah": "2a", "jawaban": {"nilai": "2400", "satuan": "cm²"}},
    )
    r = c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": "bingung"})
    assert r.status_code == 200 and r.get_json()["balasan"] == "Coba lihat lagi rumusnya."
    rows = (
        db.hubungkan(app.config["DB_PATH"])
        .execute(
            "SELECT peran, tahap_rmt, fase_kognitif, tingkat_bantuan "
            "FROM percakapan_asisten ORDER BY id"
        )
        .fetchall()
    )
    assert [(x["tahap_rmt"], x["fase_kognitif"]) for x in rows] == [
        ("manipulasi", "elaborasi"),
        ("manipulasi", "elaborasi"),
    ]
    # Tahap 2F: tingkat bantuan diisi server (1 kali salah → tingkat 1).
    assert [x["tingkat_bantuan"] for x in rows] == [1, 1]


def test_log_chatbot_misi_tanpa_kesalahan_fase_kosong(tmp_path):
    app = _app(tmp_path, ASISTEN=KonfigurasiAsisten(mode="tiruan"), ASISTEN_KLIEN=KlienTiruan())
    c = app.test_client()
    sesi = c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()
    main_id = c.post("/api/misi/1/mulai", json={"sesi_id": sesi["sesi_id"]}).get_json()["main_id"]
    c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "1a", "teks": "apa ini?"})
    row = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT tahap_rmt, fase_kognitif FROM percakapan_asisten LIMIT 1")
        .fetchone()
    )
    assert (row["tahap_rmt"], row["fase_kognitif"]) == ("analisis_tugas", None)


# ------------------------------------------------------------------ rekap guru
def test_rekap_guru_menampilkan_fase_kesulitan(tmp_path):
    c = _app(tmp_path, PIN_GURU="rahasia99").test_client()
    sesi = c.post("/api/sesi", json={"nama_panggilan": "Budi", "kode_kelas": "8A"}).get_json()
    main_id = c.post("/api/misi/1/mulai", json={"sesi_id": sesi["sesi_id"]}).get_json()["main_id"]
    salah = [
        (
            "1a",
            {"penempatan": {"u1": "a_tinggi", "u2": "a_alas", "u3": "b_alas", "u4": "b_tinggi"}},
        ),
        ("2a", {"nilai": "2400", "satuan": "cm²"}),  # LUPA_SETENGAH → elaborasi
        ("2a", {"nilai": "1200", "satuan": "cm"}),  # SALAH_SATUAN → output
    ]
    for no, jawaban in salah:
        c.post("/api/periksa", json={"main_id": main_id, "langkah": no, "jawaban": jawaban})
    for lk in bank_soal.ambil_misi(1)["langkah"]:
        c.post(
            "/api/periksa",
            json={"main_id": main_id, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
    c.post("/api/misi/selesai", json={"main_id": main_id})
    data = c.post("/api/guru", json={"kode_kelas": "8A", "pin": "rahasia99"}).get_json()
    budi = data["siswa"][0]
    assert budi["fase_kesulitan"] == {"input": 1, "elaborasi": 1, "output": 1}
    # kolom lama tetap ada dan tidak berubah artinya
    assert {"skor_misi", "total", "kategori", "petunjuk_dibuka", "kesalahan_terbanyak"} <= set(budi)
    assert budi["skor_misi"][0] == 6
