"""Tes Tahap 2F (mediasi RMT chatbot misi) dan perbaikan hasil audit (T1–T2, S1, S3, S4).

Semua tes memakai klien tiruan: TIDAK ada permintaan ke API AI sungguhan.
"""

import json
import re
from pathlib import Path

import pytest

import db
from api import routes_rmt
from app import buat_app
from asisten import mediasi
from asisten.klien import KlienTiruan
from asisten.konfigurasi import KonfigurasiAsisten
from asisten.prompt import INSTRUKSI_BERANDA, StatusSiswa, susun_pesan, susun_pesan_beranda
from bantuan import jawaban_dari_kunci
from segitiga import aktivitas_rmt, bank_soal

AKAR = Path(__file__).resolve().parents[2]


def _app(tmp_path, klien=None, **lain):
    k = KonfigurasiAsisten(mode="tiruan" if klien else "mati", rahasia_anonim="garam")
    return buat_app(
        {
            "DB_PATH": str(tmp_path / "uji.db"),
            "TESTING": True,
            "ASISTEN": k,
            "ASISTEN_KLIEN": klien,
            **lain,
        }
    )


def _sesi(c, nama="Ani"):
    return c.post("/api/sesi", json={"nama_panggilan": nama, "kode_kelas": "8A"}).get_json()[
        "sesi_id"
    ]


def _main(c, sesi_id, misi=1):
    r = c.post(f"/api/misi/{misi}/mulai", json={"sesi_id": sesi_id})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["main_id"]


SALAH_2A = {"nilai": "2.400", "satuan": "cm²"}  # misi 1 langkah 2a: lupa ½ (kunci 1.200 cm²)


# ================================================================== 2F: mediasi chatbot misi
@pytest.mark.parametrize(
    "benar,salah,petunjuk,harap",
    [(False, 0, 0, 0), (False, 1, 0, 1), (False, 2, 0, 2), (False, 0, 2, 2), (False, 5, 3, 2)]
    + [(True, 3, 3, 3), (True, 0, 0, 3)],
)
def test_tingkat_bantuan_ditentukan_status(benar, salah, petunjuk, harap):
    assert mediasi.tingkat_bantuan(benar, salah, petunjuk) == harap


def test_instruksi_mediasi_sesuai_tahap_dan_fase():
    t = mediasi.instruksi_mediasi(1, "manipulasi", "elaborasi")
    assert "Manipulasi" in t and "fase Elaborasi" in t and "Tingkat bantuan 1" in t
    # Setelah benar, fokus kesalahan tidak relevan lagi.
    assert "fase" not in mediasi.instruksi_mediasi(3, "validasi", "output").split("\n")[-1]
    assert "Kesalahan terakhir" not in mediasi.instruksi_mediasi(3, "validasi", "output")


def test_prompt_misi_berisi_mediasi_beranda_tidak():
    misi = bank_soal.ambil_misi(1)
    lk = bank_soal.cari_langkah(misi, "2a")
    sistem = susun_pesan(misi, lk, StatusSiswa(percobaan_salah=2), [], "x", "manipulasi")[0]
    assert "MEDIASI UNTUK LANGKAH INI" in sistem["content"]
    assert "Tingkat bantuan 2" in sistem["content"] and "CONTOH SERUPA" in sistem["content"]
    assert susun_pesan_beranda([], "x")[0] == {"role": "system", "content": INSTRUKSI_BERANDA}
    assert "MEDIASI" not in INSTRUKSI_BERANDA


def test_api_chat_misi_memakai_tingkat_bantuan_dari_server(tmp_path):
    klien = KlienTiruan(lambda pesan: "Kita fokus pada rumus. Kenapa dikali ½?")
    app = _app(tmp_path, klien)
    c = app.test_client()
    m = _main(c, _sesi(c))
    for _ in range(2):
        c.post("/api/periksa", json={"main_id": m, "langkah": "2a", "jawaban": SALAH_2A})
    r = c.post("/api/asisten/pesan", json={"main_id": m, "langkah": "2a", "teks": "bingung"})
    assert r.status_code == 200
    sistem = klien.panggilan[-1][0]["content"]
    assert "Tingkat bantuan 2" in sistem and "fase Elaborasi" in sistem and "Manipulasi" in sistem
    tingkat = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT DISTINCT tingkat_bantuan FROM percakapan_asisten")
        .fetchall()
    )
    assert [t[0] for t in tingkat] == [2]


def test_pengaman_tetap_menyaring_walau_petunjuk_lengkap_dibuka(tmp_path):
    """docs/07 §7.2: jawaban akhir langkah yang belum benar tidak pernah diberikan chatbot."""
    klien = KlienTiruan(lambda pesan: "Jawabannya 1.200 cm².")
    c = _app(tmp_path, klien).test_client()
    m = _main(c, _sesi(c))
    for _ in range(3):
        c.post("/api/petunjuk", json={"main_id": m, "langkah": "2a"})
    r = c.post("/api/asisten/pesan", json={"main_id": m, "langkah": "2a", "teks": "jawabannya?"})
    assert "1.200" not in r.get_json()["balasan"]


def test_setelah_benar_tingkat_3_boleh_membahas(tmp_path):
    klien = KlienTiruan(lambda pesan: "Benar, 1.200 cm² karena ½ × 60 × 40.")
    c = _app(tmp_path, klien).test_client()
    m = _main(c, _sesi(c))
    lk = bank_soal.cari_langkah(bank_soal.ambil_misi(1), "2a")
    c.post("/api/periksa", json={"main_id": m, "langkah": "2a", "jawaban": jawaban_dari_kunci(lk)})
    r = c.post("/api/asisten/pesan", json={"main_id": m, "langkah": "2a", "teks": "kenapa?"})
    assert "1.200" in r.get_json()["balasan"]
    assert "Tingkat bantuan 3" in klien.panggilan[-1][0]["content"]


# ================================================================== T2: refleksi disamarkan
def test_refleksi_lama_disamarkan(tmp_path):
    app = _app(tmp_path, PIN_GURU="9999")
    c = app.test_client()
    m = _main(c, _sesi(c, "Ani"))
    teks = "Aku Ani, hubungi 081234567890. Pertama hitung luas."
    assert c.post("/api/refleksi", json={"main_id": m, "teks": teks}).get_json()["tersimpan"]
    simpan = db.hubungkan(app.config["DB_PATH"]).execute("SELECT teks FROM refleksi").fetchone()[0]
    assert "Ani" not in simpan and "081234567890" not in simpan and "Pertama hitung" in simpan


# ================================================================== S1: pembatasan permintaan
def test_rate_limit_aktivitas_per_ip(tmp_path):
    c = _app(tmp_path, BATAS_AKTIVITAS_PER_IP=3).test_client()
    m = _main(c, _sesi(c))
    kode = [
        c.post(
            "/api/rmt/respons", json={"main_id": m, "aktivitas": "tebak", "dilewati": True}
        ).status_code
        for _ in range(4)
    ]
    assert kode == [200, 200, 200, 429]
    r = c.post(
        "/api/latihan/bertahap/selesai", json={"seed": 1, "tingkat": 1, "salah": 0, "petunjuk": 0}
    )
    assert r.status_code == 429
    # Alur berskor tidak ikut dibatasi.
    r = c.post("/api/periksa", json={"main_id": m, "langkah": "2a", "jawaban": SALAH_2A})
    assert r.status_code == 200


def test_batas_percobaan_per_aktivitas(tmp_path, monkeypatch):
    monkeypatch.setattr(routes_rmt, "MAKS_PERCOBAAN", 2)
    app = _app(tmp_path)
    c = app.test_client()
    m = _main(c, _sesi(c))
    isi = {"main_id": m, "aktivitas": "tebak", "dilewati": True}
    assert [c.post("/api/rmt/respons", json=isi).status_code for _ in range(3)] == [200, 200, 429]
    n = db.hubungkan(app.config["DB_PATH"]).execute("SELECT COUNT(*) FROM aktivitas_rmt")
    assert n.fetchone()[0] == 2


# ================================================================== S3: remedial terbaru
def _misi1_benar(c, m, salah_dulu=0):
    for _ in range(salah_dulu):
        c.post("/api/periksa", json={"main_id": m, "langkah": "2a", "jawaban": SALAH_2A})
    for lk in bank_soal.ambil_misi(1)["langkah"]:
        c.post(
            "/api/periksa",
            json={"main_id": m, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
    return c.post("/api/misi/selesai", json={"main_id": m}).get_json()


def test_remedial_hasilku_memakai_percobaan_terakhir(tmp_path):
    c = _app(tmp_path).test_client()
    s = _sesi(c)
    lama = _main(c, s)
    _misi1_benar(c, lama, salah_dulu=2)
    assert [x["area"] for x in c.get(f"/api/remedial/{s}").get_json()["saran"]] == ["rumus_luas"]
    baru = _main(c, s)
    assert _misi1_benar(c, baru)["skor"] == 6
    # Setelah berhasil tanpa salah, saran Hasilku hilang; riwayat lama tetap bisa dibaca.
    assert c.get(f"/api/remedial/{s}").get_json()["saran"] == []
    assert c.get(f"/api/remedial/{s}?main_id={lama}").get_json()["saran"]
    # Mulai misi tanpa menjawab apa pun tidak menghapus saran percobaan terakhir yang berisi.
    s2 = _sesi(c, "Budi")
    m2 = _main(c, s2)
    _misi1_benar(c, m2, salah_dulu=2)
    _main(c, s2)
    assert c.get(f"/api/remedial/{s2}").get_json()["saran"]


# ================================================================== S4: web-statis
def test_web_statis_punya_semua_fungsi_api_frontend():
    api_js = (AKAR / "frontend" / "js" / "api.js").read_text(encoding="utf-8")
    statis = (AKAR / "web-statis" / "js" / "lokal" / "layanan.js").read_text(encoding="utf-8")
    nama = set(re.findall(r"^\s{2}(\w+):", api_js, re.MULTILINE))
    assert {"rmtMisi", "remedial", "soalBertahap"} <= nama
    for n in nama - {"statusAsisten", "pesanAsisten", "pesanAsistenBeranda"}:
        assert re.search(rf"\b{n}\b", statis), f"web-statis belum punya api.{n}"


# ================================================================== misi 1–4 lengkap
def _jawaban_rmt(a):
    if a["jenis"] == "prediksi":
        return {"pilihan": a["opsi"][0]["id"]}
    if a["jenis"] == "urutan":
        return {"urutan": a["kunci"][0]}
    if a["jenis"] == "teks":
        return {"teks": "Pertama aku membaca data, lalu memilih rumus, jadi hasilnya kuperiksa."}
    return {"pilihan": a["kunci"]}


def test_misi_1_sampai_4_dengan_semua_aktivitas_rmt(tmp_path):
    app = _app(tmp_path)
    c = app.test_client()
    s = _sesi(c)
    for misi_id in (1, 2, 3, 4):
        m = _main(c, s, misi_id)  # misi berikutnya terbuka setelah sebelumnya selesai
        konten = aktivitas_rmt.ambil(misi_id)
        per_tahap = {a["tahap"]: a for a in konten["aktivitas"]}
        assert len(konten["aktivitas"]) == 6

        def kirim(tahap, m=m, per_tahap=per_tahap, misi_id=misi_id):
            a = per_tahap[tahap]
            r = c.post(
                "/api/rmt/respons",
                json={"main_id": m, "aktivitas": a["id"], "jawaban": _jawaban_rmt(a)},
            ).get_json()
            assert r["tercatat"] and r["benar"] in (True, None), (misi_id, tahap, r)

        for tahap in ("input", "perencanaan", "representasi"):
            kirim(tahap)
        for lk in bank_soal.ambil_misi(misi_id)["langkah"]:
            r = c.post(
                "/api/periksa",
                json={"main_id": m, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
            )
            assert r.get_json()["benar"], (misi_id, lk["no"])
        kirim("validasi")
        hasil = c.post("/api/misi/selesai", json={"main_id": m}).get_json()
        assert hasil["skor"] == 6, (misi_id, hasil)
        kirim("transendensi")
        kirim("refleksi")

    conn = db.hubungkan(app.config["DB_PATH"])
    per_misi = conn.execute(
        "SELECT misi_id, COUNT(DISTINCT aktivitas) FROM aktivitas_rmt GROUP BY misi_id"
    ).fetchall()
    assert [tuple(x) for x in per_misi] == [(1, 6), (2, 6), (3, 6), (4, 6)]
    p = c.get(f"/api/progres/{s}").get_json()
    assert p["total"] == 24 and all(x["skor"] == 6 for x in p["misi"])
    assert json.loads(conn.execute("SELECT rincian FROM main_misi LIMIT 1").fetchone()[0])
