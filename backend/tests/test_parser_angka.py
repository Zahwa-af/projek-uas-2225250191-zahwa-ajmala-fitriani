import pytest

from segitiga.parser_angka import format_angka, parse_angka, parse_satuan, samakah


@pytest.mark.parametrize(
    ("teks", "hasil"),
    [
        ("1,8", 1.8),
        ("1.200", 1200),
        ("2.400", 2400),
        ("Rp300.000", 300000),
        ("rp 300.000", 300000),
        ("Rp. 25.000", 25000),
        ("300000", 300000),
        ("300.000", 300000),
        ("1200 cm²", 1200),
        ("1200 cm2", 1200),
        ("1200cm^2", 1200),
        ("42 m²", 42),
        ("1200", 1200),
        (" 42 ", 42),
        ("1.5", 1.5),  # titik tanpa 3 digit = desimal
        ("0.333", 0.333),  # angka nol di depan bukan ribuan
        ("1.200,5", 1200.5),
        ("1,200.5", 1200.5),
        ("1/3", 1 / 3),
        ("⅓", 1 / 3),
        ("2/3", 2 / 3),
        ("½", 0.5),
        ("-4", -4),
        (12, 12),
        (1.8, 1.8),
    ],
)
def test_parse_angka_diterima(teks, hasil):
    assert parse_angka(teks) == pytest.approx(hasil)


@pytest.mark.parametrize("teks", ["", "abc", "1/0", "1.2.3", "1,2,3", None, "cm²", True])
def test_parse_angka_ditolak(teks):
    assert parse_angka(teks) is None


@pytest.mark.parametrize(
    ("teks", "hasil"),
    [
        ("cm2", "cm²"),
        ("cm²", "cm²"),
        ("CM^2", "cm²"),
        ("m", "m"),
        ("m2", "m²"),
        ("Rp", "Rp"),
        ("", None),
        (None, None),
        ("kg", None),
    ],
)
def test_parse_satuan(teks, hasil):
    assert parse_satuan(teks) == hasil


def test_samakah_toleransi():
    assert samakah(0.3333, 1 / 3)
    assert samakah(14.0, 14)
    assert not samakah(14.5, 14)
    assert samakah(0, 0)


@pytest.mark.parametrize(
    ("nilai", "teks"),
    [(1200, "1.200"), (1.8, "1,8"), (300000, "300.000"), (42, "42"), (0.25, "0,25")],
)
def test_format_angka(nilai, teks):
    assert format_angka(nilai) == teks
