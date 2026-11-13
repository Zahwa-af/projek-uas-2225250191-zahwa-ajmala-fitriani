from segitiga.diagnosis import diagnosis_angka


def test_lupa_setengah():
    assert diagnosis_angka(2400, 1200, {"alas": 60, "tinggi": 40}).kode == "LUPA_SETENGAH"
    assert diagnosis_angka(3.6, 1.8, {"alas": 2.4, "tinggi": 1.5}).kode == "LUPA_SETENGAH"


def test_jumlah_bukan_kali():
    assert diagnosis_angka(19, 42, {"alas": 12, "tinggi": 7}).kode == "JUMLAH_BUKAN_KALI"
    assert diagnosis_angka(9.5, 42, {"alas": 12, "tinggi": 7}).kode == "JUMLAH_BUKAN_KALI"


def test_pakai_keliling():
    assert diagnosis_angka(18, 6, {"sisi": [5, 6, 7]}).kode == "PAKAI_KELILING"


def test_salah_tinggi_pakai_sisi_miring():
    # alas 6, tinggi 4, sisi miring 5 → siswa menghitung ½ × 6 × 5 = 15
    konteks = {"alas": 6, "tinggi": 4, "sisi_miring": 5}
    assert diagnosis_angka(15, 12, konteks).kode == "SALAH_TINGGI"


def test_salah_desimal():
    assert diagnosis_angka(18, 1.8).kode == "SALAH_DESIMAL"
    assert diagnosis_angka(120, 1200).kode == "SALAH_DESIMAL"


def test_salah_hitung_kecil():
    assert diagnosis_angka(48, 42, {"alas": 12, "tinggi": 7}).kode == "SALAH_HITUNG"


def test_pola_khusus_didahulukan():
    pola = [{"nilai": 28, "kode": "TERTUKAR_BAGIAN", "pesan": "Itu luas rumput."}]
    d = diagnosis_angka(28, 14, {}, pola)
    assert d.kode == "TERTUKAR_BAGIAN"
    assert d.pesan == "Itu luas rumput."


def test_tidak_dikenali():
    assert diagnosis_angka(999, 42, {"alas": 12, "tinggi": 7}).kode == "TIDAK_DIKENALI"
