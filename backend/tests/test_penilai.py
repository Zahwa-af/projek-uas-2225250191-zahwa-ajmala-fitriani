import pytest

from bantuan import jawaban_dari_kunci
from segitiga import bank_soal
from segitiga.penilai import (
    StatusLangkah,
    hitung_bintang,
    hitung_skor_misi,
    kategori_literasi,
    periksa_langkah,
)

SEMUA_LANGKAH = [(m["id"], lk) for m in bank_soal.semua_misi() for lk in m["langkah"]]


def _langkah(misi_id: int, no: str) -> dict:
    misi = bank_soal.ambil_misi(misi_id)
    assert misi is not None
    lk = bank_soal.cari_langkah(misi, no)
    assert lk is not None
    return lk


def test_bank_soal_valid_dan_4_misi():
    misi = bank_soal.semua_misi()
    assert [m["id"] for m in misi] == [1, 2, 3, 4]
    for m in misi:
        assert sum(lk["skor"] for lk in m["langkah"]) == 6


@pytest.mark.parametrize(("misi_id", "langkah"), SEMUA_LANGKAH, ids=lambda x: str(x)[:20])
def test_kunci_setiap_langkah_dinilai_benar(misi_id, langkah):
    hasil = periksa_langkah(langkah, jawaban_dari_kunci(langkah))
    assert hasil.benar, f"misi {misi_id} langkah {langkah['no']}: {hasil.umpan_balik}"


def test_misi_publik_tanpa_rahasia():
    for m in bank_soal.semua_misi():
        publik = bank_soal.misi_publik(m)
        for lk in publik["langkah"]:
            assert not (set(lk) & bank_soal.FIELD_RAHASIA)


# ---------------------------------------------------------------- angka
def test_angka_lupa_setengah_misi1():
    h = periksa_langkah(_langkah(1, "2a"), {"nilai": "2.400", "satuan": "cm²"})
    assert not h.benar and h.kode == "LUPA_SETENGAH"


def test_angka_satuan_salah_dan_kosong():
    lk = _langkah(1, "2a")
    h = periksa_langkah(lk, {"nilai": "1.200", "satuan": "cm"})
    assert h.kode == "SALAH_SATUAN" and "pangkat dua" in h.umpan_balik
    h = periksa_langkah(lk, {"nilai": "1.200", "satuan": "m²"})
    assert h.kode == "SALAH_SATUAN"
    assert periksa_langkah(lk, {"nilai": "1200"}).kode == "SATUAN_KOSONG"


def test_angka_format_tidak_terbaca():
    assert periksa_langkah(_langkah(1, "2a"), {"nilai": "seribu"}).kode == "FORMAT_ANGKA"


def test_angka_rupiah_tanpa_pilihan_satuan():
    lk = _langkah(2, "6")
    assert periksa_langkah(lk, {"nilai": "300.000"}).benar
    assert periksa_langkah(lk, {"nilai": "Rp300.000"}).benar
    assert periksa_langkah(lk, {"nilai": "75000"}).kode == "LUPA_JUMLAH_BENDA"


def test_angka_misi3_tertukar_bagian():
    assert periksa_langkah(_langkah(3, "3b"), {"nilai": "28", "satuan": "m²"}).kode == (
        "TERTUKAR_BAGIAN"
    )
    assert periksa_langkah(_langkah(3, "4"), {"nilai": "14", "satuan": "m²"}).kode == (
        "TERTUKAR_BAGIAN"
    )


def test_angka_misi4_hasil_dika():
    h = periksa_langkah(_langkah(4, "3"), {"nilai": "3,6", "satuan": "m²"})
    assert h.kode == "LUPA_SETENGAH" and "Dika" in h.umpan_balik
    assert periksa_langkah(_langkah(4, "3"), {"nilai": "1.8", "satuan": "m2"}).benar


# ---------------------------------------------------------------- rumus
def test_rumus_alas_tinggi_boleh_tertukar():
    lk = _langkah(3, "2a")
    assert periksa_langkah(lk, {"isian": ["12", "7"]}).benar
    assert periksa_langkah(lk, {"isian": ["7", "12"]}).benar


def test_rumus_menunjuk_kotak_salah():
    h = periksa_langkah(_langkah(2, "4"), {"isian": ["3", "2", "5"]})
    assert not h.benar and "ke-3" in h.umpan_balik


def test_rumus_pola_khusus_lupa_setengah():
    h = periksa_langkah(_langkah(2, "4"), {"isian": ["3", "2", "6"]})
    assert h.kode == "LUPA_SETENGAH"


def test_rumus_pecahan():
    lk = _langkah(3, "3a")
    assert periksa_langkah(lk, {"isian": ["1/3", "42"]}).benar
    assert periksa_langkah(lk, {"isian": ["42", "⅓"]}).benar
    assert periksa_langkah(lk, {"isian": ["2/3", "42"]}).kode == "TERTUKAR_BAGIAN"


def test_rumus_kotak_kosong():
    assert not periksa_langkah(_langkah(3, "2a"), {"isian": ["12", ""]}).benar


# ---------------------------------------------------------------- pilihan & pilah
def test_pilihan_umpan_balik_khusus():
    h = periksa_langkah(_langkah(2, "3"), {"pilihan": "a"})
    assert not h.benar and "persegi panjang" in h.umpan_balik


def test_pilihan_banyak_kurang_lengkap():
    h = periksa_langkah(_langkah(2, "2"), {"pilihan": ["a"]})
    assert h.kode == "KURANG_LENGKAP"
    assert periksa_langkah(_langkah(2, "2"), {"pilihan": ["b", "a"]}).benar


def test_pilihan_kosong():
    assert periksa_langkah(_langkah(1, "3"), {}).kode == "KOSONG"


def test_pilah_menunjuk_item_salah():
    lk = _langkah(1, "1a")
    salah = {"u1": "a_alas", "u2": "b_tinggi", "u3": "b_alas", "u4": "a_tinggi"}
    h = periksa_langkah(lk, {"penempatan": salah})
    assert not h.benar and "40 cm" in h.umpan_balik and "30 cm" in h.umpan_balik
    assert periksa_langkah(lk, {"penempatan": {"u1": "a_alas"}}).kode == "KOSONG"


def test_latihan_pilah_valid():
    for soal in bank_soal.latihan()["pilah"]:
        assert periksa_langkah(soal, jawaban_dari_kunci(soal)).benar


# ---------------------------------------------------------------- skor
def _semua_benar(misi: dict) -> dict[str, StatusLangkah]:
    return {lk["no"]: StatusLangkah(benar=True) for lk in misi["langkah"]}


def test_skor_penuh():
    for misi in bank_soal.semua_misi():
        skor = hitung_skor_misi(misi, _semua_benar(misi))
        assert skor.skor == 6 and skor.maks == 6 and skor.bintang == 3


def test_skor_petunjuk_tingkat3_nol_tingkat2_penuh():
    misi = bank_soal.ambil_misi(3)
    st = _semua_benar(misi)
    st["2b"] = StatusLangkah(benar=True, tingkat_petunjuk=3)
    st["3b"] = StatusLangkah(benar=True, tingkat_petunjuk=2)
    skor = hitung_skor_misi(misi, st)
    assert skor.skor == 5
    tahap2 = next(r for r in skor.rincian if r["tahap"] == 2)
    assert tahap2 == {"tahap": 2, "skor": 1, "maks": 2}
    assert skor.bintang == 2


def test_skor_setengah_misi1():
    misi = bank_soal.ambil_misi(1)
    st = _semua_benar(misi)
    st["1a"] = StatusLangkah(benar=False, tingkat_petunjuk=3)
    assert hitung_skor_misi(misi, st).skor == 5.5


def test_bintang():
    assert hitung_bintang(6, 6, 1) == 3
    assert hitung_bintang(6, 6, 2) == 2
    assert hitung_bintang(4, 6, 0) == 2
    assert hitung_bintang(1, 6, 9) == 1


@pytest.mark.parametrize(
    ("total", "kategori"),
    [
        (24, "Sangat baik"),
        (20, "Sangat baik"),
        (15, "Baik"),
        (10, "Cukup"),
        (9.5, "Perlu bimbingan"),
    ],
)
def test_kategori(total, kategori):
    assert kategori_literasi(total) == kategori
