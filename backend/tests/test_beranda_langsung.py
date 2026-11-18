"""Tes backend chatbot beranda (Tanya Pembimbing): aturan misi tidak ikut campur."""

from datetime import UTC, datetime, timedelta

import db
from app import buat_app
from asisten.anonim import samarkan
from asisten.klien import KlienTiruan
from asisten.konfigurasi import KonfigurasiAsisten
from asisten.prompt import INSTRUKSI_BERANDA


def _app(tmp_path, klien):
    return buat_app(
        {
            "DB_PATH": str(tmp_path / "uji.db"),
            "TESTING": True,
            "ASISTEN": KonfigurasiAsisten(mode="tiruan"),
            "ASISTEN_KLIEN": klien,
        }
    )


def _sesi(c):
    return c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()[
        "sesi_id"
    ]


def test_jawaban_langsung_tidak_disaring_pengaman_misi(tmp_path):
    # 1.200 cm² adalah kunci Misi 1; di beranda jawaban ini harus tetap utuh.
    jawaban = "L = ½ × 60 × 40\nL = 1.200 cm²\nJadi, luasnya 1.200 cm²."
    c = _app(tmp_path, KlienTiruan([jawaban])).test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": "hitung ½ × 60 × 40"})
    assert r.get_json()["balasan"] == jawaban


def test_angka_panjang_hasil_hitungan_tidak_disamarkan(tmp_path):
    jawaban = "2⁴⁰ = 1099511627776"
    c = _app(tmp_path, KlienTiruan([jawaban])).test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": "berapa 2 pangkat 40?"})
    assert "1099511627776" in r.get_json()["balasan"]
    # pertanyaan siswa tetap disamarkan seperti sebelumnya
    assert samarkan("NIK 3201234567890123")[0] == "NIK [nomor]"


def test_pertanyaan_umum_diteruskan_tanpa_pembatasan(tmp_path):
    klien = KlienTiruan(["Ibu kota Indonesia adalah Jakarta."])
    c = _app(tmp_path, klien).test_client()
    r = c.post(
        "/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": "Apa ibu kota Indonesia?"}
    )
    assert r.status_code == 200 and "Jakarta" in r.get_json()["balasan"]
    assert klien.panggilan[0][0]["content"] == INSTRUKSI_BERANDA  # bukan instruksi misi


def test_riwayat_lama_tidak_ikut_dikirim(tmp_path):
    """Balasan lama bergaya 'coba hitung sendiri' tidak boleh menjadi contoh bagi model."""
    klien = KlienTiruan(["Jawaban baru."])
    app = _app(tmp_path, klien)
    c = app.test_client()
    s = _sesi(c)
    lama = (datetime.now(UTC) - timedelta(hours=3)).isoformat(timespec="seconds")
    baru = (datetime.now(UTC) - timedelta(minutes=5)).isoformat(timespec="seconds")
    conn = db.hubungkan(app.config["DB_PATH"])
    for peran, teks, waktu in [
        ("siswa", "hitung keliling 5, 7, 9", lama),
        ("asisten", "Coba hitung sendiri, apa hasilnya?", lama),
        ("siswa", "apa itu alas?", baru),
        ("asisten", "Alas adalah sisi dasar segitiga.", baru),
    ]:
        conn.execute(
            "INSERT INTO percakapan_beranda (sesi_id, kode_anonim, peran, teks, sumber, waktu) "
            "VALUES (?, 'S-X', ?, ?, 'deepseek', ?)",
            (s, peran, teks, waktu),
        )
    conn.commit()
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "lalu apa itu tinggi?"})
    isi = [p["content"] for p in klien.panggilan[0][1:]]
    assert isi == ["apa itu alas?", "Alas adalah sisi dasar segitiga.", "lalu apa itu tinggi?"]
