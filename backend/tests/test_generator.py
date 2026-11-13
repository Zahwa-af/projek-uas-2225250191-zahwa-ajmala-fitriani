import math

from segitiga.generator_soal import buat_soal_tinggi, periksa_soal_tinggi, soal_tinggi_publik


def _tegak_lurus_alas(k: dict) -> bool:
    # Alas mendatar, jadi garis tinggi harus vertikal.
    return math.isclose(k["dari"]["x"], k["ke"]["x"], abs_tol=1e-6)


def test_tepat_satu_kandidat_tegak_lurus():
    for seed in range(1, 600):
        soal = buat_soal_tinggi(seed)
        tegak = [k for k in soal["kandidat"] if _tegak_lurus_alas(k)]
        assert len(tegak) == 1, seed
        assert tegak[0]["peran"] == "tinggi"
        assert {k["id"] for k in soal["kandidat"]} == {"P", "Q", "R"}


def test_seed_sama_soal_sama():
    assert buat_soal_tinggi(42) == buat_soal_tinggi(42)


def test_tumpul_kaki_tinggi_di_luar_alas():
    for seed in range(2, 300, 3):  # seed % 3 == 2 → tumpul
        soal = buat_soal_tinggi(seed)
        assert soal["jenis"] == "tumpul"
        assert soal["titik"]["C"]["x"] < soal["titik"]["A"]["x"]


def test_publik_tanpa_peran():
    publik = soal_tinggi_publik(buat_soal_tinggi(7))
    assert all("peran" not in k for k in publik["kandidat"])


def test_periksa():
    soal = buat_soal_tinggi(10)
    benar = next(k["id"] for k in soal["kandidat"] if k["peran"] == "tinggi")
    salah = next(k["id"] for k in soal["kandidat"] if k["peran"] != "tinggi")
    assert periksa_soal_tinggi(10, benar)["benar"]
    hasil = periksa_soal_tinggi(10, salah)
    assert not hasil["benar"] and hasil["kunci"] == benar
    assert not periksa_soal_tinggi(10, "Z")["benar"]
