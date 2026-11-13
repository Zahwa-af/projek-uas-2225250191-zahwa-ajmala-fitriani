import pytest

from segitiga.rumus import (
    adalah_segitiga,
    jenis_menurut_sisi,
    jenis_menurut_sudut,
    keliling_segitiga,
    luas_segitiga,
)


def test_luas_kisi_kisi():
    assert luas_segitiga(60, 40) == 1200
    assert luas_segitiga(80, 30) == 1200
    assert luas_segitiga(3, 2) == 3
    assert luas_segitiga(12, 7) == 42
    assert luas_segitiga(2.4, 1.5) == pytest.approx(1.8)


def test_luas_tidak_valid():
    with pytest.raises(ValueError):
        luas_segitiga(0, 5)


def test_keliling():
    assert keliling_segitiga(5, 6, 7) == 18
    with pytest.raises(ValueError):
        keliling_segitiga(1, 2, 10)


def test_adalah_segitiga():
    assert adalah_segitiga(3, 4, 5)
    assert not adalah_segitiga(1, 2, 3)  # segaris


@pytest.mark.parametrize(
    ("sisi", "jenis"),
    [((5, 5, 5), "sama sisi"), ((5, 5, 3), "sama kaki"), ((4, 5, 6), "sembarang")],
)
def test_jenis_sisi(sisi, jenis):
    assert jenis_menurut_sisi(*sisi) == jenis


@pytest.mark.parametrize(
    ("sisi", "jenis"), [((3, 4, 5), "siku-siku"), ((5, 5, 5), "lancip"), ((3, 4, 6), "tumpul")]
)
def test_jenis_sudut(sisi, jenis):
    assert jenis_menurut_sudut(*sisi) == jenis
