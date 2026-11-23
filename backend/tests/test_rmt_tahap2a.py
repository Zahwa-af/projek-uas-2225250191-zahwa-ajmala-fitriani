"""Tes RMT Tahap 2A: konten aktivitas, validasi, kebocoran kunci, endpoint, skor, anonimitas."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

import db
from app import buat_app
from asisten.anonim import kode_anonim
from asisten.konfigurasi import KonfigurasiAsisten
from bantuan import jawaban_dari_kunci
from segitiga import aktivitas_rmt, bank_soal

AKAR = Path(__file__).resolve().parents[2]

# Kolom tabel lama, diambil dari skema commit 8b693f1 (sebelum Tahap 2A).
KOLOM_TABEL_LAMA = {
    "jawaban_langkah": [
        "id",
        "main_id",
        "langkah",
        "percobaan_ke",
        "jawaban",
        "benar",
        "kode_diagnosis",
        "waktu",
    ],
    "main_misi": [
        "id",
        "sesi_id",
        "misi_id",
        "mulai",
        "selesai",
        "skor_rubrik",
        "rincian",
        "bintang",
        "total_petunjuk",
    ],
    "percakapan_asisten": [
        "id",
        "main_id",
        "kode_anonim",
        "misi_id",
        "langkah",
        "peran",
        "teks",
        "teks_asli",
        "disamarkan",
        "disaring",
        "alasan_saring",
        "langkah_benar",
        "percobaan_salah",
        "tingkat_petunjuk",
        "kode_diagnosis",
        "tingkat_bantuan",
        "tahap_rmt",
        "fase_kognitif",
        "sumber",
        "model",
        "token_masuk",
        "token_keluar",
        "durasi_ms",
        "waktu",
    ],
    "percakapan_beranda": [
        "id",
        "sesi_id",
        "kode_anonim",
        "peran",
        "teks",
        "disamarkan",
        "sumber",
        "model",
        "token_masuk",
        "token_keluar",
        "durasi_ms",
        "waktu",
    ],
    "petunjuk_dibuka": ["main_id", "langkah", "tingkat", "otomatis", "waktu"],
    "refleksi": ["main_id", "teks", "waktu"],
    "sesi": ["id", "nama_panggilan", "kode_kelas", "dibuat"],
}

# Sidik jari file penilaian yang TIDAK boleh berubah di Tahap 2A.
SIDIK_JARI = {
    "backend/data/soal/misi.json": "7e581c710627",
    "backend/segitiga/penilai.py": "7cd4e9ffc0a3",
    "backend/segitiga/diagnosis.py": "a653c6b5f5b9",
}

STRING_RAHASIA = ("kunci", "jawaban_sebenarnya", "penjelasan", "umpan_balik")


# ------------------------------------------------------------------ konten
def test_konten_empat_misi_valid():
    konten = aktivitas_rmt.semua_konten()
    assert [k["misi_id"] for k in konten] == [1, 2, 3, 4]
    for k in konten:
        assert k["tujuan"] and k["makna"]
        assert {a["tahap"] for a in k["aktivitas"]} == set(aktivitas_rmt.TAHAP_WAJIB)


def test_kunci_semua_aktivitas_dinilai_benar():
    for k in aktivitas_rmt.semua_konten():
        for a in k["aktivitas"]:
            if a["jenis"] in {"pilihan", "pilihan_banyak"}:
                h = aktivitas_rmt.periksa(a, {"pilihan": a["kunci"]})
            elif a["jenis"] == "urutan":
                h = aktivitas_rmt.periksa(a, {"urutan": a["kunci"][0]})
            else:
                continue
            assert h.benar and h.penjelasan, (k["misi_id"], a["id"])


def _rusak(ubah):
    daftar = [copy.deepcopy(k) for k in aktivitas_rmt.semua_konten()]
    ubah(daftar)
    return daftar


@pytest.mark.parametrize(
    "ubah",
    [
        lambda d: d.pop(),  # misi kurang
        lambda d: d[0].update(tujuan=""),
        lambda d: d[0].update(makna="x" * 300),
        lambda d: d[0]["aktivitas"].pop(),  # tahap transendensi hilang
        lambda d: d[0]["aktivitas"][2].update(kunci="z"),  # kunci pilihan tidak ada di opsi
        lambda d: d[0]["aktivitas"][1].update(kunci=[["m", "k", "t"]]),  # urutan tidak lengkap
        lambda d: d[0]["aktivitas"][1].update(kunci=[["b", "k", "m", "t"]]),  # = urutan alfabet
        lambda d: d[0]["aktivitas"][0].update(jawaban_sebenarnya="z"),
        lambda d: d[0]["aktivitas"][5].update(kunci=["a"]),  # pilihan_banyak < 2
        lambda d: d[0]["aktivitas"][4].update(kalimat_pembuka=[]),
        lambda d: d[0]["aktivitas"][2].update(tahap="bebas"),
        lambda d: d[0]["aktivitas"][2].update(jenis="isian"),
    ],
)
def test_validasi_menolak_konten_rusak(ubah):
    with pytest.raises(ValueError):
        aktivitas_rmt.validasi(_rusak(ubah), {1, 2, 3, 4})


# ------------------------------------------------------------------ kebocoran kunci
def test_konten_publik_tanpa_rahasia():
    for k in aktivitas_rmt.semua_konten():
        teks = json.dumps(aktivitas_rmt.publik(k), ensure_ascii=False)
        for rahasia in STRING_RAHASIA:
            assert f'"{rahasia}' not in teks, (k["misi_id"], rahasia)


def test_urutan_kartu_publik_tidak_membocorkan_jawaban():
    for k in aktivitas_rmt.semua_konten():
        asli = next(a for a in k["aktivitas"] if a["jenis"] == "urutan")
        publik = next(a for a in aktivitas_rmt.publik(k)["aktivitas"] if a["jenis"] == "urutan")
        tampil = [x["id"] for x in publik["kartu"]]
        assert tampil not in asli["kunci"], k["misi_id"]


def _app(tmp_path):
    return buat_app(
        {
            "DB_PATH": str(tmp_path / "uji.db"),
            "TESTING": True,
            "ASISTEN": KonfigurasiAsisten(mode="mati", rahasia_anonim="garam"),
        }
    )


def test_endpoint_konten_tanpa_rahasia(tmp_path):
    c = _app(tmp_path).test_client()
    for misi_id in (1, 2, 3, 4):
        r = c.get(f"/api/rmt/misi/{misi_id}")
        assert r.status_code == 200
        teks = r.get_data(as_text=True)
        for rahasia in STRING_RAHASIA:
            assert f'"{rahasia}' not in teks
    assert c.get("/api/rmt/misi/9").status_code == 404


# ------------------------------------------------------------------ respons
def _mulai(c, nama="Rani"):
    s = c.post("/api/sesi", json={"nama_panggilan": nama, "kode_kelas": "8A"}).get_json()
    return (
        s["sesi_id"],
        c.post("/api/misi/1/mulai", json={"sesi_id": s["sesi_id"]}).get_json()["main_id"],
    )


def _kirim(c, main_id, aktivitas, **isi):
    return c.post("/api/rmt/respons", json={"main_id": main_id, "aktivitas": aktivitas, **isi})


def test_respons_setiap_jenis(tmp_path):
    c = _app(tmp_path).test_client()
    _, m = _mulai(c)

    r = _kirim(c, m, "tebak", jawaban={"pilihan": "a"}).get_json()
    assert r["benar"] is None and r["penjelasan"] is None and "dicatat" in r["umpan_balik"]

    salah = _kirim(c, m, "rencana", jawaban={"urutan": ["t", "m", "k", "b"]}).get_json()
    assert salah["benar"] is False and salah["penjelasan"] is None
    assert "ke-1" in salah["umpan_balik"] and "Hitung" not in salah["umpan_balik"]
    benar = _kirim(c, m, "rencana", jawaban={"urutan": ["k", "m", "t", "b"]}).get_json()
    assert benar["benar"] is True and benar["penjelasan"]  # urutan alternatif diterima

    r = _kirim(c, m, "representasi", jawaban={"pilihan": "a"}).get_json()
    assert r["benar"] is False and "Alas saja" in r["umpan_balik"] and r["penjelasan"] is None
    r = _kirim(c, m, "validasi", jawaban={"pilihan": "a"}).get_json()
    assert r["benar"] is True and "setengah persegi panjang" in r["penjelasan"]

    r = _kirim(c, m, "transendensi", jawaban={"pilihan": ["a"]}).get_json()
    assert r["benar"] is False  # kurang lengkap
    r = _kirim(c, m, "transendensi", jawaban={"pilihan": ["b", "a"]}).get_json()
    assert r["benar"] is True

    r = _kirim(c, m, "refleksi", jawaban={"teks": "Pertama aku hitung luas A dan B."}).get_json()
    assert r["benar"] is None and r["tercatat"]

    assert _kirim(c, m, "transendensi", dilewati=True).get_json() == {
        "tercatat": True,
        "dilewati": True,
    }


@pytest.mark.parametrize(
    ("aktivitas", "isi", "kode"),
    [
        ("tidakada", {"jawaban": {"pilihan": "a"}}, 404),
        ("tebak", {"jawaban": {"pilihan": "z"}}, 400),
        ("rencana", {"jawaban": {"urutan": ["m", "k"]}}, 400),
        ("representasi", {"jawaban": {"pilihan": ["a", "b"]}}, 400),
        ("refleksi", {"jawaban": {"teks": ""}}, 400),
        ("refleksi", {"jawaban": {"teks": "x" * 1001}}, 400),
        ("validasi", {"jawaban": "a"}, 400),
    ],
)
def test_respons_tidak_sah_ditolak(tmp_path, aktivitas, isi, kode):
    c = _app(tmp_path).test_client()
    _, m = _mulai(c)
    assert _kirim(c, m, aktivitas, **isi).status_code == kode


def test_main_tidak_ada_404(tmp_path):
    c = _app(tmp_path).test_client()
    r = _kirim(c, "bukanmain", "tebak", jawaban={"pilihan": "a"})
    assert r.status_code == 404


# ------------------------------------------------------------------ anonim
def test_data_aktivitas_anonim(tmp_path):
    app = _app(tmp_path)
    c = app.test_client()
    sesi_id, m = _mulai(c, nama="Rani")
    _kirim(c, m, "refleksi", jawaban={"teks": "Aku Rani, wa 081234567890. Luasnya sama."})
    _kirim(c, m, "tebak", jawaban={"pilihan": "c"})
    rows = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT * FROM aktivitas_rmt ORDER BY id")
        .fetchall()
    )
    semua = json.dumps([dict(r) for r in rows], ensure_ascii=False)
    assert "Rani" not in semua and "081234567890" not in semua and sesi_id not in semua
    assert all(r["kode_anonim"] == kode_anonim(sesi_id, "garam") for r in rows)
    assert "[nama]" in rows[0]["jawaban"] and "[nomor]" in rows[0]["jawaban"]
    assert [(r["aktivitas"], r["tahap_rmt"], r["percobaan_ke"]) for r in rows] == [
        ("refleksi", "refleksi", 1),
        ("tebak", "input", 1),
    ]


# ------------------------------------------------------------------ skor & tabel lama
def test_aktivitas_tidak_mengubah_skor(tmp_path):
    app = _app(tmp_path)
    c = app.test_client()
    _, m = _mulai(c)
    for lk in bank_soal.ambil_misi(1)["langkah"]:
        c.post(
            "/api/periksa",
            json={"main_id": m, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
    # aktivitas salah, dilewati, dan benar dicampur
    _kirim(c, m, "rencana", jawaban={"urutan": ["t", "m", "k", "b"]})
    _kirim(c, m, "validasi", jawaban={"pilihan": "c"})
    _kirim(c, m, "transendensi", dilewati=True)
    hasil = c.post("/api/misi/selesai", json={"main_id": m}).get_json()
    assert hasil["skor"] == 6 and hasil["maks"] == 6
    assert [r["tahap"] for r in hasil["rincian"]] == [1, 2, 3, 4, 5]  # tidak ada tahap baru
    # aktivitas setelah misi selesai (transendensi/refleksi) tetap diterima, skor tetap
    assert _kirim(c, m, "refleksi", jawaban={"teks": "Aku membandingkan luas."}).status_code == 200
    conn = db.hubungkan(app.config["DB_PATH"])
    assert conn.execute("SELECT skor_rubrik FROM main_misi WHERE id = ?", (m,)).fetchone()[0] == 6
    assert conn.execute("SELECT COUNT(*) FROM jawaban_langkah").fetchone()[0] == 7


def test_tabel_lama_tidak_berubah(tmp_path):
    app = _app(tmp_path)
    conn = db.hubungkan(app.config["DB_PATH"])
    for tabel, kolom in KOLOM_TABEL_LAMA.items():
        assert [r[1] for r in conn.execute(f"PRAGMA table_info({tabel})")] == kolom, tabel
    kolom_baru = [r[1] for r in conn.execute("PRAGMA table_info(aktivitas_rmt)")]
    assert "nama_panggilan" not in kolom_baru and "sesi_id" not in kolom_baru


def test_file_penilaian_tidak_berubah():
    for path, awalan in SIDIK_JARI.items():
        sidik = hashlib.sha256((AKAR / path).read_bytes()).hexdigest()
        assert sidik.startswith(awalan), path


def test_pilihan_banyak_harus_daftar(tmp_path):
    c = _app(tmp_path).test_client()
    _, m = _mulai(c)
    assert _kirim(c, m, "transendensi", jawaban={"pilihan": "a"}).status_code == 400


def test_mode_produksi_tidak_bocor_ke_tes_lain():
    import os

    assert os.environ.get("SEGIPINTAR_PRODUKSI") != "1"
