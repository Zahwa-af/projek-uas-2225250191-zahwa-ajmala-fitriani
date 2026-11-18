"""Tes penanganan galat chatbot: koneksi putus, galat tak terduga, dan pencatatan alasan."""

import http.client

import pytest

import db
from app import buat_app
from asisten.klien import GalatLLM, KlienDeepSeek, KlienTiruan
from asisten.konfigurasi import KonfigurasiAsisten

KUNCI = "sk-or-v1-PALSU-uji-galat-111111"


# ------------------------------------------------------------------ klien
@pytest.mark.parametrize(
    "galat",
    [http.client.IncompleteRead(b'{"choices":'), http.client.BadStatusLine("x")],
)
def test_klien_menangkap_koneksi_putus(galat):
    k = KonfigurasiAsisten(mode="deepseek", api_key=KUNCI, base_url="https://openrouter.ai/api/v1")

    def buka(req, timeout):
        raise galat

    with pytest.raises(GalatLLM) as info:
        KlienDeepSeek(k, buka=buka).balas([])
    assert "terputus" in info.value.pesan and type(galat).__name__ in info.value.pesan


# ------------------------------------------------------------------ endpoint
class KlienMeledak:
    """Klien yang melempar galat tak terduga (bukan GalatLLM)."""

    sumber = "deepseek"

    def balas(self, pesan):
        raise RuntimeError(f"rusak {KUNCI}")


def _app(tmp_path, klien):
    k = KonfigurasiAsisten(mode="tiruan", api_key=KUNCI)
    return buat_app(
        {"DB_PATH": str(tmp_path / "uji.db"), "TESTING": True, "ASISTEN": k, "ASISTEN_KLIEN": klien}
    )


def _sesi(c):
    return c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()[
        "sesi_id"
    ]


def test_beranda_galat_llm_dicatat_dengan_alasan(tmp_path):
    app = _app(tmp_path, KlienTiruan(galat=GalatLLM("Batas permintaan OpenRouter tercapai.", 429)))
    c = app.test_client()
    s = _sesi(c)
    r = c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "halo"})
    assert r.status_code == 503 and "galat" in r.get_json()
    rows = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT peran, sumber, teks FROM percakapan_beranda ORDER BY id")
        .fetchall()
    )
    assert [(x["peran"], x["sumber"]) for x in rows] == [("siswa", "tiruan"), ("asisten", "galat")]
    assert "Batas permintaan OpenRouter" in rows[1]["teks"]


def test_beranda_galat_tak_terduga_jadi_503_json_bukan_500(tmp_path, caplog):
    app = _app(tmp_path, KlienMeledak())
    c = app.test_client()
    s = _sesi(c)
    r = c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "halo"})
    assert (
        r.status_code == 503 and r.is_json
    )  # frontend menampilkan pesan, bukan "Terjadi gangguan"
    alasan = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT teks FROM percakapan_beranda WHERE sumber = 'galat'")
        .fetchone()["teks"]
    )
    assert "RuntimeError" in alasan and KUNCI not in alasan and "[KEY]" in alasan
    assert "galat tak terduga" in caplog.text  # traceback tercatat di log server


def test_misi_galat_tak_terduga_jadi_503_json(tmp_path):
    app = _app(tmp_path, KlienMeledak())
    c = app.test_client()
    s = _sesi(c)
    main_id = c.post("/api/misi/1/mulai", json={"sesi_id": s}).get_json()["main_id"]
    r = c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": "halo"})
    assert r.status_code == 503 and r.is_json
    row = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT teks FROM percakapan_asisten WHERE sumber = 'galat'")
        .fetchone()
    )
    assert "RuntimeError" in row["teks"] and KUNCI not in row["teks"]


def test_beranda_riwayat_tidak_memuat_baris_galat(tmp_path):
    klien = KlienTiruan(["Jawaban pertama."])
    app = _app(tmp_path, klien)
    c = app.test_client()
    s = _sesi(c)
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "pertanyaan satu"})
    # sisipkan baris galat seperti hasil kegagalan sebelumnya
    conn = db.hubungkan(app.config["DB_PATH"])
    conn.execute(
        "INSERT INTO percakapan_beranda (sesi_id, kode_anonim, peran, teks, sumber, waktu) "
        "VALUES (?, 'S-X', 'asisten', 'Batas permintaan tercapai.', 'galat', 'w')",
        (s,),
    )
    conn.commit()
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "pertanyaan dua"})
    isi = [p["content"] for p in klien.panggilan[1]]
    assert "Batas permintaan tercapai." not in isi
    assert isi[1:] == ["pertanyaan satu", "Jawaban pertama.", "pertanyaan dua"]


def test_beranda_normal_tetap_berjalan(tmp_path):
    app = _app(tmp_path, KlienTiruan(["K = 21 cm. Jadi, kelilingnya 21 cm."]))
    c = app.test_client()
    r = c.post("/api/asisten/beranda", json={"sesi_id": _sesi(c), "teks": "keliling 5, 7, 9?"})
    assert r.status_code == 200 and "21 cm" in r.get_json()["balasan"]


def test_pertanyaan_gagal_tidak_ikut_riwayat(tmp_path):
    """Meniru kejadian: pertanyaan keliling gagal dijawab, lalu siswa bertanya luas.

    Sebelumnya, pertanyaan yang gagal ikut terkirim dan model menjawab ulang soal keliling.
    """
    klien = KlienTiruan(["Jawaban A.", "Jawaban luas."])
    app = _app(tmp_path, klien)
    c = app.test_client()
    s = _sesi(c)
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "pertanyaan A"})
    conn = db.hubungkan(app.config["DB_PATH"])
    for peran, teks, sumber in [
        ("siswa", "hitung keliling 5, 7, 9", "deepseek"),
        ("asisten", "Batas permintaan tercapai.", "galat"),
        ("siswa", "pertanyaan tanpa balasan (versi lama, tanpa baris galat)", "deepseek"),
    ]:
        conn.execute(
            "INSERT INTO percakapan_beranda (sesi_id, kode_anonim, peran, teks, sumber, waktu) "
            "VALUES (?, 'S-X', ?, ?, ?, 'w')",
            (s, peran, teks, sumber),
        )
    conn.commit()
    c.post("/api/asisten/beranda", json={"sesi_id": s, "teks": "hitung luas alas 10 tinggi 6"})
    isi = [p["content"] for p in klien.panggilan[1][1:]]
    assert isi == ["pertanyaan A", "Jawaban A.", "hitung luas alas 10 tinggi 6"]
