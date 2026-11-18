"""Tes: chatbot beranda tidak menahan jawaban (kasus nyata 'hiasan dinding', 18 Nov 2026)."""

import socket

import db
from app import buat_app, port_sudah_dipakai
from asisten.klien import KlienTiruan
from asisten.konfigurasi import KonfigurasiAsisten
from asisten.pengaman import menyuruh_siswa_menghitung
from asisten.prompt import INSTRUKSI_BERANDA

# Balasan asli yang tersimpan di database saat masalah terjadi.
BALASAN_ASLI_1 = (
    "Pertama, cari hasil perkalian alas dan tinggi (40 cm × 30 cm).\n"
    "Setelah mendapatkan hasil perkalian, bagi hasilnya dengan 2 untuk mendapatkan luas.\n"
    "Apa hasil perkalian 40 dan 30?"
)
BALASAN_ASLI_2 = (
    "Tenang, kita hitung pelan-pelan ya.\n"
    "Kalikan angka 40 dengan 30, lalu bagi hasilnya dengan 2.\n"
    "Apa hasil perkalian 40 dan 30?"
)
JAWABAN_LANGSUNG = (
    "Diketahui:\nAlas = 40 cm\nTinggi = 30 cm\nRumus:\nL = ½ × alas × tinggi\n"
    "Penyelesaian:\nL = ½ × 40 × 30\nL = ½ × 1.200\nL = 600 cm²\n"
    "Jadi, luas hiasan dinding tersebut adalah 600 cm²."
)
SOAL = (
    "Sebuah hiasan dinding berbentuk segitiga memiliki alas 40 cm dan tinggi 30 cm. "
    "Hiasan itu dibuat oleh 5 siswa. Berapa luas hiasan dinding itu?"
)


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


# ------------------------------------------------------------------ deteksi
def test_deteksi_balasan_asli_yang_bermasalah():
    assert menyuruh_siswa_menghitung(BALASAN_ASLI_1)
    assert menyuruh_siswa_menghitung(BALASAN_ASLI_2)
    assert menyuruh_siswa_menghitung("Coba kamu hitung keliling segitiga itu, ya?")
    assert not menyuruh_siswa_menghitung(JAWABAN_LANGSUNG)
    assert not menyuruh_siswa_menghitung("Hasil perkalian 40 × 30 adalah 1.200.")


# ------------------------------------------------------------------ minta ulang
def test_balasan_menahan_jawaban_diminta_ulang(tmp_path):
    klien = KlienTiruan([BALASAN_ASLI_1, JAWABAN_LANGSUNG])
    app = _app(tmp_path, klien)
    c = app.test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": SOAL})
    assert r.get_json()["balasan"] == JAWABAN_LANGSUNG
    assert len(klien.panggilan) == 2
    permintaan_ulang = klien.panggilan[1][-1]["content"]
    assert "langsung selesaikan sampai hasil akhir" in permintaan_ulang
    # yang disimpan hanya jawaban akhir, bukan balasan yang menahan jawaban
    teks_db = [
        r["teks"]
        for r in db.hubungkan(app.config["DB_PATH"]).execute(
            "SELECT teks FROM percakapan_beranda WHERE peran = 'asisten'"
        )
    ]
    assert teks_db == [JAWABAN_LANGSUNG]


def test_jawaban_langsung_tidak_diminta_ulang(tmp_path):
    klien = KlienTiruan([JAWABAN_LANGSUNG])
    c = _app(tmp_path, klien).test_client()
    c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": SOAL})
    assert len(klien.panggilan) == 1


# ------------------------------------------------------------------ riwayat
def _isi_riwayat(app, sesi, baris):
    conn = db.hubungkan(app.config["DB_PATH"])
    for peran, teks in baris:
        conn.execute(
            "INSERT INTO percakapan_beranda (sesi_id, kode_anonim, peran, teks, sumber, waktu) "
            "VALUES (?, 'S-X', ?, ?, 'deepseek', strftime('%Y-%m-%dT%H:%M:%S+00:00','now'))",
            (sesi, peran, teks),
        )
    conn.commit()


def test_aku_tidak_tahu_soal_terakhir_tetap_terkirim(tmp_path):
    """Kasus C: soal dijawab dengan tanya balik, lalu siswa: 'aku tidak tahu, coba kamu hitung'."""
    klien = KlienTiruan([JAWABAN_LANGSUNG])
    app = _app(tmp_path, klien)
    c = app.test_client()
    s = _sesi(c)
    _isi_riwayat(app, s, [("siswa", SOAL), ("asisten", BALASAN_ASLI_1)])
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "aku tidak tahu, coba kamu hitung"})
    isi = [p["content"] for p in klien.panggilan[0][1:]]
    assert isi == [SOAL, "aku tidak tahu, coba kamu hitung"]  # soal ada, tanya balik dibuang


def test_contoh_tanya_balik_lama_dibuang_seluruhnya(tmp_path):
    klien = KlienTiruan([JAWABAN_LANGSUNG])
    app = _app(tmp_path, klien)
    c = app.test_client()
    s = _sesi(c)
    _isi_riwayat(
        app,
        s,
        [
            ("siswa", "hitung keliling 5, 7, 9"),
            ("asisten", "Coba kamu hitung keliling segitiga itu, ya?"),
            ("siswa", "apa itu alas?"),
            ("asisten", "Alas adalah sisi dasar segitiga."),
        ],
    )
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": SOAL})
    isi = [p["content"] for p in klien.panggilan[0][1:]]
    assert isi == ["apa itu alas?", "Alas adalah sisi dasar segitiga.", SOAL]


# ------------------------------------------------------------------ instruksi
def test_instruksi_memuat_susunan_dan_aturan_tidak_tahu():
    t = INSTRUKSI_BERANDA
    assert "SELESAIKAN SAMPAI HASIL AKHIR" in t
    assert "Jangan menahan hasil" in t
    for bagian in ("Diketahui:", "Rumus:", "Penyelesaian:", "Jadi,"):
        assert bagian in t
    assert '"coba kamu hitung"' in t and "L = 600 cm²" in t
    assert "BUKAN permintaan latihan" in t
    assert "bertahap" in t  # hanya dalam larangan "Jangan menahan hasil ... bertahap"
    assert "bimbing secara bertahap" not in t.lower() and "petunjuk bertahap" not in t.lower()


# ------------------------------------------------------------------ dua server
def test_deteksi_port_sudah_dipakai():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        assert port_sudah_dipakai(port)
    assert not port_sudah_dipakai(port)


# ------------------------------------------------------------------ galat sementara
class KlienBerurutan:
    """Melempar galat dari daftar dulu, lalu memberi jawaban."""

    sumber = "deepseek"

    def __init__(self, galat, jawaban="Jadi, luasnya 600 cm²."):
        self.galat = list(galat)
        self.jawaban = jawaban
        self.jumlah = 0

    def balas(self, pesan):
        from asisten.klien import HasilLLM

        self.jumlah += 1
        if self.galat:
            raise self.galat.pop(0)
        return HasilLLM(teks=self.jawaban, model="uji")


def test_galat_sementara_dicoba_ulang_sekali(tmp_path):
    from asisten.klien import GalatLLM

    kosong = GalatLLM("Balasan kosong: jatah token habis untuk proses berpikir model.")
    klien = KlienBerurutan([kosong])
    c = _app(tmp_path, klien).test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": SOAL})
    assert r.status_code == 200 and "600 cm²" in r.get_json()["balasan"]
    assert klien.jumlah == 2


def test_galat_tetap_tidak_diulang(tmp_path):
    from asisten.klien import GalatLLM

    klien = KlienBerurutan([GalatLLM("API key ditolak.", 401)])
    c = _app(tmp_path, klien).test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": SOAL})
    assert r.status_code == 503 and klien.jumlah == 1


def test_gagal_dua_kali_alasan_keduanya_dicatat(tmp_path):
    from asisten.klien import GalatLLM

    klien = KlienBerurutan([GalatLLM("Balasan kosong.", None), GalatLLM("Batas permintaan.", 429)])
    app = _app(tmp_path, klien)
    c = app.test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": SOAL})
    assert r.status_code == 503 and klien.jumlah == 2
    alasan = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT teks FROM percakapan_beranda WHERE sumber = 'galat'")
        .fetchone()["teks"]
    )
    assert "Balasan kosong." in alasan and "Batas permintaan." in alasan
