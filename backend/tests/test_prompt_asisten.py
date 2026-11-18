"""Tes instruksi sistem chatbot (beranda vs misi) dan penanganan jawaban terpotong."""

import io
import json

from app import buat_app
from asisten.klien import CATATAN_TERPOTONG, KlienDeepSeek, KlienTiruan, potong_ke_kalimat_utuh
from asisten.konfigurasi import KonfigurasiAsisten
from asisten.prompt import (
    ATURAN_PEMBIMBING,
    INSTRUKSI_BERANDA,
    StatusSiswa,
    susun_pesan,
    susun_pesan_beranda,
)
from segitiga import bank_soal


# ------------------------------------------------------------------ isi instruksi
def test_instruksi_beranda_memuat_ketentuan_jawab_langsung():
    t = INSTRUKSI_BERANDA
    assert "JAWAB LANGSUNG" in t  # ketentuan 1
    assert "SELESAIKAN SAMPAI HASIL AKHIR" in t  # ketentuan 2
    assert "Ditanya rumus: beri rumusnya" in t  # ketentuan 3
    assert "bahasa sederhana untuk siswa SMP" in t  # ketentuan 4
    for frasa in ("coba hitung sendiri", "sekarang giliran", "apa hasilnya?"):  # ketentuan 5
        assert frasa in t  # disebut sebagai contoh kalimat yang DILARANG
    assert "pertanyaan umum dan pelajaran lain" in t  # ketentuan 6
    assert "Jangan mengakhiri jawaban dengan pertanyaan" in t  # ketentuan 7
    assert "Jangan mengarang fakta" in t  # ketentuan 8
    assert "latihan atau kuis HANYA jika siswa memintanya" in t  # ketentuan 9
    assert "Bahasa Indonesia yang alami, ramah" in t  # ketentuan 10
    assert "L = 600 cm²" in t and "bukan LaTeX" in t  # contoh format
    assert "walaupun gaya jawaban di riwayat percakapan sebelumnya berbeda" in t


def test_instruksi_beranda_tanpa_aturan_yang_bertentangan():
    t = INSTRUKSI_BERANDA
    assert "khusus membantu belajar matematika" not in t  # dulu: tolak pertanyaan umum
    assert "Akhiri setiap balasan dengan" not in t
    assert "Maksimal tiga kalimat" not in t
    # "bertahap" hanya boleh muncul sebagai larangan menahan jawaban
    assert "bimbing secara bertahap" not in t.lower() and "petunjuk bertahap" not in t.lower()
    # aturan misi tidak boleh bocor ke beranda
    assert "Jangan pernah menyebutkan jawaban akhir" not in t
    assert "MISI" not in t and "KONTEKS" not in t and "tombol Periksa" not in t


def test_aturan_misi_tetap_utuh_dan_terpisah():
    t = ATURAN_PEMBIMBING
    assert "Jangan pernah menyebutkan jawaban akhir langkah misi ini" in t
    assert "tombol Periksa" in t
    assert INSTRUKSI_BERANDA not in t


def test_instruksi_misi_memuat_aturan_umum_dan_pengecualian():
    t = ATURAN_PEMBIMBING
    assert "kerjakan sampai hasil akhir" in t
    assert "contoh serupa sampai selesai dengan angka yang berbeda" in t


def test_susun_pesan_beranda_dan_misi():
    p = susun_pesan_beranda([{"role": "user", "content": "x"}] * 20, "Hitung keliling 5, 7, 9 cm")
    assert p[0] == {"role": "system", "content": INSTRUKSI_BERANDA}
    assert p[-1]["content"] == "Hitung keliling 5, 7, 9 cm" and len(p) == 1 + 8 + 1

    misi = bank_soal.ambil_misi(1)
    lk = bank_soal.cari_langkah(misi, "2a")
    sistem = susun_pesan(misi, lk, StatusSiswa(), [], "?")[0]["content"]
    assert sistem.startswith(ATURAN_PEMBIMBING) and "KONTEKS" in sistem


def test_endpoint_beranda_memakai_instruksi_baru(tmp_path):
    klien = KlienTiruan(["K = 5 + 7 + 9\nK = 21 cm\nJadi, kelilingnya 21 cm."])
    app = buat_app(
        {
            "DB_PATH": str(tmp_path / "uji.db"),
            "TESTING": True,
            "ASISTEN": KonfigurasiAsisten(mode="tiruan"),
            "ASISTEN_KLIEN": klien,
        }
    )
    c = app.test_client()
    sesi = c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()
    r = c.post(
        "/api/asisten/beranda",
        json={"sesi_id": sesi["sesi_id"], "teks": "Hitung keliling segitiga 5 cm, 7 cm, 9 cm"},
    )
    assert r.status_code == 200 and "21 cm" in r.get_json()["balasan"]
    sistem = klien.panggilan[0][0]
    assert sistem == {"role": "system", "content": INSTRUKSI_BERANDA}


# ------------------------------------------------------------------ jawaban terpotong
def test_potong_membuang_kalimat_menggantung():
    teks = "Luas segitiga adalah ½ × alas × tinggi.\nL = ½ × 12 × 7\nL = 42 cm²\nJadi, luasnya ada"
    hasil = potong_ke_kalimat_utuh(teks)
    assert "Jadi, luasnya ada" not in hasil
    assert "L = 42 cm²" in hasil and hasil.endswith(CATATAN_TERPOTONG)


def test_potong_tidak_memecah_angka_desimal():
    teks = "Luasnya 1,8 m² dan 1.200 cm². Lalu kita bandingkan dengan"
    hasil = potong_ke_kalimat_utuh(teks)
    assert hasil.startswith("Luasnya 1,8 m² dan 1.200 cm².")
    assert "bandingkan dengan" not in hasil


class _Respons(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _klien_dengan(alasan_selesai, isi):
    k = KonfigurasiAsisten(
        mode="deepseek", api_key="sk-or-palsu", base_url="https://openrouter.ai/api/v1"
    )
    badan = {"choices": [{"finish_reason": alasan_selesai, "message": {"content": isi}}]}
    return KlienDeepSeek(k, buka=lambda req, timeout: _Respons(json.dumps(badan).encode()))


def test_klien_memangkas_hanya_jika_terpotong():
    isi = "K = 5 + 7 + 9\nK = 21 cm\nJadi, keliling segitiga tersebut ada"
    terpotong = _klien_dengan("length", isi).balas([]).teks
    assert "tersebut ada" not in terpotong and CATATAN_TERPOTONG in terpotong
    utuh = _klien_dengan("stop", "K = 21 cm\nJadi, kelilingnya 21 cm.").balas([]).teks
    assert utuh == "K = 21 cm\nJadi, kelilingnya 21 cm."


def test_instruksi_beranda_memuat_rujukan_fakta_segitiga():
    t = INSTRUKSI_BERANDA
    assert "Segitiga sama sisi: KETIGA sisinya sama panjang" in t and "60°" in t
    assert "Segitiga sama kaki: DUA sisinya sama panjang" in t
    assert "Jumlah ketiga sudut segitiga selalu 180°" in t
    assert "L = ½ × alas × tinggi" in t and "K = s₁ + s₂ + s₃" in t
