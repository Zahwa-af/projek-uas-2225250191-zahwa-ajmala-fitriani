import json

import pytest

from app import buat_app
from bantuan import jawaban_dari_kunci
from segitiga import bank_soal


@pytest.fixture()
def klien(tmp_path):
    app = buat_app({"DB_PATH": str(tmp_path / "uji.db"), "PIN_GURU": "9999", "TESTING": True})
    return app.test_client()


def _sesi(klien, nama="Ani", kelas="8a"):
    r = klien.post("/api/sesi", json={"nama_panggilan": nama, "kode_kelas": kelas})
    assert r.status_code == 200
    return r.get_json()["sesi_id"]


def _mainkan_semua_benar(klien, sesi_id, misi_id):
    main_id = klien.post(f"/api/misi/{misi_id}/mulai", json={"sesi_id": sesi_id}).get_json()[
        "main_id"
    ]
    for lk in bank_soal.ambil_misi(misi_id)["langkah"]:
        r = klien.post(
            "/api/periksa",
            json={"main_id": main_id, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
        assert r.get_json()["benar"], lk["no"]
    return main_id


def test_halaman_utama_dan_js(klien):
    assert klien.get("/").status_code == 200
    r = klien.get("/js/main.js")
    assert r.status_code == 200
    assert "javascript" in r.content_type


def test_sesi_validasi(klien):
    assert (
        klien.post("/api/sesi", json={"nama_panggilan": "", "kode_kelas": "x"}).status_code == 400
    )
    sesi_id = _sesi(klien)
    data = klien.get(f"/api/sesi/{sesi_id}").get_json()
    assert data["kode_kelas"] == "8A"


def test_isi_misi_tidak_membocorkan_kunci(klien):
    for misi_id in (1, 2, 3, 4):
        teks = json.dumps(klien.get(f"/api/misi/{misi_id}").get_json())
        for rahasia in ("kunci", "petunjuk", "penjelasan_benar", "pola_salah", "umpan_balik"):
            assert f'"{rahasia}' not in teks


def test_misi_terkunci_berurutan(klien):
    sesi_id = _sesi(klien)
    daftar = klien.get(f"/api/misi?sesi_id={sesi_id}").get_json()
    assert [m["terbuka"] for m in daftar] == [True, False, False, False]
    r = klien.post("/api/misi/2/mulai", json={"sesi_id": sesi_id})
    assert r.status_code == 403


def test_alur_misi_penuh_skor_6(klien):
    sesi_id = _sesi(klien)
    main_id = _mainkan_semua_benar(klien, sesi_id, 1)
    hasil = klien.post("/api/misi/selesai", json={"main_id": main_id}).get_json()
    assert hasil["skor"] == 6 and hasil["bintang"] == 3 and hasil["lencana"] == "Penalar"
    assert len(hasil["ringkasan"]) == 7
    daftar = klien.get(f"/api/misi?sesi_id={sesi_id}").get_json()
    assert daftar[1]["terbuka"]


def test_tiga_kali_salah_membuka_petunjuk_dan_skor_nol(klien):
    sesi_id = _sesi(klien)
    main1 = _mainkan_semua_benar(klien, sesi_id, 1)
    klien.post("/api/misi/selesai", json={"main_id": main1})
    main_id = klien.post("/api/misi/2/mulai", json={"sesi_id": sesi_id}).get_json()["main_id"]

    salah = {"nilai": "75000"}
    for _i in range(3):
        r = klien.post(
            "/api/periksa", json={"main_id": main_id, "langkah": "6", "jawaban": salah}
        ).get_json()
        assert not r["benar"] and r["kode_diagnosis"] == "LUPA_JUMLAH_BENDA"
    assert r["boleh_lanjut"] and r["tingkat_petunjuk"] == 3
    assert [p["tingkat"] for p in r["petunjuk_baru"]] == [1, 2, 3]

    misi = bank_soal.ambil_misi(2)
    for lk in misi["langkah"]:
        if lk["no"] != "6":
            klien.post(
                "/api/periksa",
                json={"main_id": main_id, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
            )
    hasil = klien.post("/api/misi/selesai", json={"main_id": main_id}).get_json()
    assert hasil["skor"] == 5


def test_format_salah_tidak_dihitung_percobaan(klien):
    sesi_id = _sesi(klien)
    main_id = klien.post("/api/misi/1/mulai", json={"sesi_id": sesi_id}).get_json()["main_id"]
    for _ in range(5):
        r = klien.post(
            "/api/periksa",
            json={"main_id": main_id, "langkah": "2a", "jawaban": {"nilai": "abc"}},
        ).get_json()
    assert r["kode_diagnosis"] == "FORMAT_ANGKA" and r["tingkat_petunjuk"] == 0


def test_petunjuk_bertahap(klien):
    sesi_id = _sesi(klien)
    main_id = klien.post("/api/misi/1/mulai", json={"sesi_id": sesi_id}).get_json()["main_id"]
    for t in (1, 2, 3):
        r = klien.post("/api/petunjuk", json={"main_id": main_id, "langkah": "2a"}).get_json()
        assert r["tingkat_petunjuk"] == t
        assert r["petunjuk_baru"][0]["tingkat"] == t
    assert r["boleh_lanjut"]
    assert (
        klien.post("/api/petunjuk", json={"main_id": main_id, "langkah": "2a"}).status_code == 400
    )


def test_selesai_ditolak_jika_belum_lengkap(klien):
    sesi_id = _sesi(klien)
    main_id = klien.post("/api/misi/1/mulai", json={"sesi_id": sesi_id}).get_json()["main_id"]
    assert klien.post("/api/misi/selesai", json={"main_id": main_id}).status_code == 400


def test_progres_dan_guru(klien):
    sesi_id = _sesi(klien, "Budi", "8A")
    main_id = _mainkan_semua_benar(klien, sesi_id, 1)
    klien.post("/api/misi/selesai", json={"main_id": main_id})
    klien.post("/api/refleksi", json={"main_id": main_id, "teks": "Hitung luas dulu."})

    p = klien.get(f"/api/progres/{sesi_id}").get_json()
    assert p["total"] == 6 and p["lencana"] == ["Penalar"]

    assert klien.post("/api/guru", json={"kode_kelas": "8A", "pin": "0000"}).status_code == 403
    g = klien.post("/api/guru", json={"kode_kelas": "8a", "pin": "9999"}).get_json()
    assert g["siswa"][0]["nama_panggilan"] == "Budi"
    assert g["siswa"][0]["refleksi"] == ["Hitung luas dulu."]


def test_latihan(klien):
    soal = klien.get("/api/latihan/pilah").get_json()
    assert all("kunci" not in s for s in soal)
    s = bank_soal.latihan()["pilah"][0]
    r = klien.post(
        "/api/latihan/pilah/periksa", json={"soal_id": s["id"], "penempatan": s["kunci"]}
    ).get_json()
    assert r["benar"]

    t = klien.get("/api/latihan/tinggi?seed=5").get_json()
    assert all("peran" not in k for k in t["kandidat"])
    r = klien.post("/api/latihan/tinggi/periksa", json={"seed": 5, "pilihan": "P"}).get_json()
    assert "benar" in r
