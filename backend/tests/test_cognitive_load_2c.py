"""Tes Tahap 2C — Cognitive Load: fading (Soal Cerita Bertahap) dan remedial adaptif.

Dasar: analisis kebutuhan S01 + diagnosis aplikasi (belum berdasarkan hasil uji coba instrumen).
"""

import hashlib
import json
from pathlib import Path

import pytest

import db
from app import buat_app
from asisten.konfigurasi import KonfigurasiAsisten
from segitiga import fading, remedial

AKAR = Path(__file__).resolve().parents[2]
SEED = range(0, 150)


def _jawab(nilai: float, satuan: str) -> dict:
    teks = f"{nilai:,.2f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",")
    return {"nilai": teks.replace("X", "."), "satuan": satuan}


# ================================================================== fading: soal
@pytest.mark.parametrize("tingkat", [1, 2, 3, 4])
def test_soal_publik_tanpa_kunci(tingkat):
    for seed in SEED:
        s = fading.soal_publik(seed, tingkat)
        teks = json.dumps(s, ensure_ascii=False)
        for rahasia in ("kunci", "pola_salah", "konteks_diagnosis", "penjelasan_benar"):
            assert rahasia not in teks
        d = fading.buat_data(seed, tingkat)
        # Hasil akhir tidak pernah tampil sebelum siswa menjawab.
        assert f"= {fading._f(d.total)} " not in teks


def test_bantuan_berkurang_bertahap():
    tampil = [len(fading.TINGKAT[t]["tampil"]) for t in range(1, 5)]
    isian = [len(fading.TINGKAT[t]["isian"]) for t in range(1, 5)]
    assert tampil == sorted(tampil, reverse=True) and tampil[0] > tampil[-1] == 0
    assert isian == sorted(isian)
    # Tingkat 1 masih memperlihatkan hitungan luas satu benda (contoh hampir lengkap).
    s1 = fading.soal_publik(3, 1)
    assert [j for j, _ in s1["langkah_contoh"]][-1] == "Hitung luas satu"
    assert [i["no"] for i in s1["isian"]] == ["total"]
    s4 = fading.soal_publik(3, 4)
    assert s4["langkah_contoh"] == [] and [i["no"] for i in s4["isian"]] == ["satu", "total"]


def test_pengecoh_hanya_di_tingkat_atas_dan_geometrinya_benar():
    for seed in SEED:
        for t in (1, 2):
            assert fading.buat_data(seed, t).sisi_miring is None
        for t in (3, 4):
            d = fading.buat_data(seed, t)
            x = (1 - d.puncak) * d.alas
            assert abs((x**2 + d.tinggi**2) ** 0.5 - d.sisi_miring) < 0.05
            assert d.sisi_miring not in (d.alas, d.tinggi)
            assert "sisi miring" in " ".join(fading.soal_publik(seed, t)["cerita"])


@pytest.mark.parametrize("tingkat", [1, 2, 3, 4])
def test_jawaban_benar_diterima_format_indonesia(tingkat):
    for seed in SEED:
        d = fading.buat_data(seed, tingkat)
        s2 = f"{d.satuan}²"
        for no in fading.TINGKAT[tingkat]["isian"]:
            nilai = d.luas_satu if no == "satu" else d.total
            assert fading.periksa(seed, tingkat, no, _jawab(nilai, s2)).benar, (seed, no)


@pytest.mark.parametrize("tingkat", [1, 2, 3, 4])
def test_kunci_tidak_bertabrakan_dengan_pola_salah(tingkat):
    for seed in SEED:
        d = fading.buat_data(seed, tingkat)
        pola = fading._isian(d, "total")["pola_salah"]
        assert d.total not in [p["nilai"] for p in pola]


def test_diagnosis_kesalahan_umum():
    seed = 11
    d = fading.buat_data(seed, 4)
    s2 = f"{d.satuan}²"
    kode = lambda no, n, sat=s2: fading.periksa(seed, 4, no, _jawab(n, sat)).kode  # noqa: E731
    assert kode("satu", d.alas * d.tinggi) == "LUPA_SETENGAH"
    assert kode("satu", 0.5 * d.alas * d.sisi_miring) == "SALAH_TINGGI"
    assert kode("satu", d.luas_satu, d.satuan) == "SALAH_SATUAN"
    assert kode("total", d.luas_satu) == "LUPA_JUMLAH_BENDA"
    assert kode("total", d.banyak * d.alas * d.tinggi) == "LUPA_SETENGAH"
    assert kode("total", d.banyak * 0.5 * d.alas * d.sisi_miring) == "SALAH_TINGGI"
    assert fading.periksa(seed, 4, "total", {"nilai": "", "satuan": s2}).kode == "FORMAT_ANGKA"


def test_isian_yang_tidak_ada_di_tingkat_ditolak():
    with pytest.raises(ValueError):
        fading.periksa(1, 1, "satu", {"nilai": "1"})  # tingkat 1 hanya isian total
    with pytest.raises(ValueError):
        fading.petunjuk(1, 2, "lain", 1)


def test_petunjuk_bertahap_cara_lengkap_di_akhir():
    d = fading.buat_data(5, 4)
    p = [fading.petunjuk(5, 4, "total", k)["teks"] for k in (1, 2, 3)]
    assert fading._f(d.total) not in p[0] and fading._f(d.total) not in p[1]
    assert fading._f(d.total) in p[2]
    assert fading.petunjuk(5, 4, "satu", 99)["tingkat"] == 3


@pytest.mark.parametrize("masukan", [None, "x", -5, 0, 99, "3"])
def test_normalkan_tingkat(masukan):
    assert 1 <= fading.normalkan_tingkat(masukan) <= 4


# ================================================================== fading: aturan
def test_naik_hanya_satu_tingkat_saat_benar_tanpa_bantuan():
    for t in (1, 2, 3):
        k = fading.tingkat_berikut(t, salah=0, petunjuk_tertinggi=0)
        assert (k.tingkat, k.arah) == (t + 1, "naik")
    assert fading.tingkat_berikut(4, 0, 0).tingkat == 4


def test_tetap_bila_masih_sedikit_salah_atau_petunjuk_ringan():
    assert fading.tingkat_berikut(2, 1, 0).arah == "tetap"
    assert fading.tingkat_berikut(2, 0, 2).arah == "tetap"
    assert fading.tingkat_berikut(3, 2, 1).tingkat == 3


def test_bantuan_ditambah_bila_kesulitan():
    assert fading.tingkat_berikut(3, 0, 3) == fading.KeputusanFading(
        2, "turun", fading.tingkat_berikut(3, 0, 3).pesan
    )
    assert fading.tingkat_berikut(4, 3, 0).tingkat == 3
    assert fading.tingkat_berikut(1, 5, 3).tingkat == 1  # tidak turun di bawah 1


def test_refleksi_pengecoh_hanya_jika_ada_sisi_miring():
    tanya1 = {fading.refleksi(s, 1)["tanya"] for s in range(10)}
    tanya4 = {fading.refleksi(s, 4)["tanya"] for s in range(10)}
    assert not any("sisi miring" in t for t in tanya1)
    assert any("sisi miring" in t for t in tanya4)


# ================================================================== remedial: modul
def test_remedial_di_bawah_ambang_tidak_disarankan():
    assert remedial.saran([("LUPA_SETENGAH", 1, "2a")]) == []


def test_remedial_memetakan_kesalahan_ke_materi():
    hasil = remedial.saran(
        [("LUPA_SETENGAH", 1, "2a"), ("JUMLAH_BUKAN_KALI", 1, "2b"), ("SALAH_TINGGI", 2, "4")]
    )
    assert [h["area"] for h in hasil] == ["rumus_luas"]
    assert hasil[0]["kode"] == {"LUPA_SETENGAH": 1, "JUMLAH_BUKAN_KALI": 1}
    assert any(t["href"] == "#/latihan/bertahap" for t in hasil[0]["tautan"])


def test_remedial_kode_umum_ikut_fase_langkah_dan_petunjuk_lengkap():
    # Misi 1 langkah 1b = analisis tugas → Input → memilah informasi.
    hasil = remedial.saran([("PILIHAN_SALAH", 1, "1b")], [(1, "1b")])
    assert hasil[0]["area"] == "memilah_info" and hasil[0]["bobot"] == 2
    # Isian kosong / format tidak terbaca bukan kesulitan.
    assert remedial.saran([("KOSONG", 1, "1b"), ("FORMAT_ANGKA", 1, "2a")] * 3) == []


def test_remedial_paling_banyak_dua_urut_bobot():
    kes = (
        [("SALAH_SATUAN", 1, "2a")] * 2
        + [("SALAH_TINGGI", 2, "4")] * 4
        + [("SALAH_HITUNG", 2, "5")] * 3
    )
    hasil = remedial.saran(kes)
    assert [h["area"] for h in hasil] == ["alas_tinggi", "operasi_hitung"]


def test_semua_kode_diagnosis_punya_area():
    from segitiga.diagnosis import PESAN

    for kode in set(PESAN) - remedial.rmt.BUKAN_KESALAHAN - {"TIDAK_DIKENALI"}:
        assert remedial.area_kesalahan(kode, 1, "2a"), kode


def test_tautan_remedial_menuju_rute_yang_ada():
    main_js = (AKAR / "frontend" / "js" / "main.js").read_text(encoding="utf-8")
    belajar = (AKAR / "frontend" / "js" / "halaman" / "belajar.js").read_text(encoding="utf-8")
    assert "latihan\\/bertahap" in main_js
    assert "Bandingkan keliling dan luas" in belajar  # layar #/belajar/4/5
    for ar in remedial.AREA.values():
        for _, href in ar.tautan:
            assert href.startswith(("#/belajar/", "#/latihan/")), href


# ================================================================== API
@pytest.fixture
def klien(tmp_path):
    app = buat_app(
        {
            "DB_PATH": str(tmp_path / "uji.db"),
            "TESTING": True,
            "ASISTEN": KonfigurasiAsisten(mode="mati", rahasia_anonim="garam"),
        }
    )
    return app, app.test_client()


def test_api_latihan_bertahap_alur(klien):
    _, c = klien
    s = c.get("/api/latihan/bertahap?tingkat=2&seed=42").get_json()
    assert s["tingkat"] == 2 and s["seed"] == 42 and "kunci" not in json.dumps(s)
    d = fading.buat_data(42, 2)
    r = c.post(
        "/api/latihan/bertahap/periksa",
        json={"seed": 42, "tingkat": 2, "isian": "satu", "jawaban": _jawab(d.alas * d.tinggi, "")},
    ).get_json()
    assert r["benar"] is False and r["kode"] == "LUPA_SETENGAH"
    r = c.post(
        "/api/latihan/bertahap/periksa",
        json={
            "seed": 42,
            "tingkat": 2,
            "isian": "satu",
            "jawaban": _jawab(d.luas_satu, f"{d.satuan}²"),
        },
    ).get_json()
    assert r["benar"] is True
    p = c.post(
        "/api/latihan/bertahap/petunjuk", json={"seed": 42, "tingkat": 2, "isian": "total", "ke": 1}
    ).get_json()
    assert p["tingkat"] == 1 and p["teks"]
    k = c.post(
        "/api/latihan/bertahap/selesai", json={"seed": 42, "tingkat": 2, "salah": 1, "petunjuk": 0}
    ).get_json()
    assert k["tingkat_berikut"] == 2 and k["arah"] == "tetap" and k["refleksi"]["penjelasan"]
    k = c.post(
        "/api/latihan/bertahap/selesai", json={"seed": 42, "tingkat": 2, "salah": 0, "petunjuk": 0}
    ).get_json()
    assert k["tingkat_berikut"] == 3


@pytest.mark.parametrize(
    "url,isi",
    [
        ("/api/latihan/bertahap/periksa", {"seed": "x", "tingkat": 1, "isian": "total"}),
        (
            "/api/latihan/bertahap/periksa",
            {"seed": 1, "tingkat": 1, "isian": "satu", "jawaban": {}},
        ),
        (
            "/api/latihan/bertahap/periksa",
            {"seed": 1, "tingkat": 1, "isian": "total", "jawaban": 5},
        ),
        ("/api/latihan/bertahap/petunjuk", {"seed": 1, "tingkat": 1, "isian": "total", "ke": "a"}),
        ("/api/latihan/bertahap/selesai", {"seed": 1, "tingkat": 1, "salah": "banyak"}),
    ],
)
def test_api_latihan_bertahap_masukan_tidak_valid(klien, url, isi):
    _, c = klien
    assert c.post(url, json=isi).status_code == 400


def _main_misi1(c):
    sesi = c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()
    m = c.post("/api/misi/1/mulai", json={"sesi_id": sesi["sesi_id"]}).get_json()["main_id"]
    return sesi["sesi_id"], m


def test_api_remedial_dari_kesalahan_siswa_sendiri(klien):
    app, c = klien
    sesi_id, m = _main_misi1(c)
    kosong = c.get(f"/api/remedial/{sesi_id}").get_json()
    assert kosong == {"saran": [], "ada_data": False}

    salah = {"nilai": "2.400", "satuan": "cm²"}  # lupa ½ pada langkah 2a (kunci 1.200 cm²)
    for _ in range(2):
        assert c.post(
            "/api/periksa", json={"main_id": m, "langkah": "2a", "jawaban": salah}
        ).get_json()["kode_diagnosis"] == ("LUPA_SETENGAH")

    conn = db.hubungkan(app.config["DB_PATH"])
    sebelum = conn.execute("SELECT * FROM jawaban_langkah ORDER BY id").fetchall()
    r = c.get(f"/api/remedial/{sesi_id}").get_json()
    assert r["ada_data"] and [s["area"] for s in r["saran"]] == ["rumus_luas"]
    assert r["saran"][0]["misi"] == [1]
    # Per main misi
    assert c.get(f"/api/remedial/{sesi_id}?main_id={m}").get_json()["saran"]
    assert c.get(f"/api/remedial/{sesi_id}?main_id=lain").get_json()["saran"] == []
    # Hanya membaca: jawaban siswa tidak berubah atau terhapus.
    sesudah = conn.execute("SELECT * FROM jawaban_langkah ORDER BY id").fetchall()
    assert [tuple(x) for x in sebelum] == [tuple(x) for x in sesudah]


def test_api_remedial_tidak_mengubah_skor(klien):
    from bantuan import jawaban_dari_kunci
    from segitiga import bank_soal

    _, c = klien
    sesi_id, m = _main_misi1(c)
    c.post("/api/periksa", json={"main_id": m, "langkah": "2a", "jawaban": {"nilai": "1"}})
    for lk in bank_soal.ambil_misi(1)["langkah"]:
        c.post(
            "/api/periksa",
            json={"main_id": m, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
    skor = c.post("/api/misi/selesai", json={"main_id": m}).get_json()["skor"]
    c.get(f"/api/remedial/{sesi_id}")
    assert c.get(f"/api/progres/{sesi_id}").get_json()["misi"][0]["skor"] == skor == 6


def test_api_remedial_sesi_tidak_dikenal(klien):
    _, c = klien
    assert c.get("/api/remedial/tidakada").status_code == 404


# ================================================================== yang tidak boleh berubah
def test_soal_kunci_penilai_diagnosis_tetap():
    berkas = {
        "backend/data/soal/misi.json": "7e581c710627",
        "backend/segitiga/penilai.py": "7cd4e9ffc0a3",
        "backend/segitiga/diagnosis.py": "a653c6b5f5b9",
    }
    for jalur, awalan in berkas.items():
        isi = (AKAR / jalur).read_bytes()
        assert hashlib.sha256(isi).hexdigest().startswith(awalan), jalur


def test_tidak_ada_tabel_baru_untuk_2c(klien):
    app, _ = klien
    conn = db.hubungkan(app.config["DB_PATH"])
    tabel = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tabel - {"sqlite_sequence"} == {
        "sesi",
        "main_misi",
        "jawaban_langkah",
        "petunjuk_dibuka",
        "refleksi",
        "percakapan_asisten",
        "percakapan_beranda",
        "aktivitas_rmt",
    }
