"""Mendiagnosis kesalahan umum pada jawaban angka.

Umpan balik selalu menunjuk kemungkinan penyebab, bukan sekadar "salah" (DS02, IL05).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .parser_angka import samakah

PESAN: dict[str, str] = {
    "LUPA_SETENGAH": "Hasilmu 2 kali lebih besar. Sudahkah kamu mengalikan dengan ½?",
    "PAKAI_KELILING": "Itu cara menghitung keliling. Yang ditanya adalah luas.",
    "JUMLAH_BUKAN_KALI": "Pada rumus luas, alas dan tinggi dikalikan, bukan dijumlahkan.",
    "SALAH_TINGGI": "Tinggi harus tegak lurus dengan alas. Lihat garis oranye putus-putus.",
    "LUPA_JUMLAH_BENDA": "Itu baru untuk satu benda. Ada berapa banyak bendanya?",
    "TERTUKAR_BAGIAN": "Itu luas bagian yang lain. Baca lagi bagian mana yang ditanya.",
    "SALAH_SATUAN": "Angkamu benar! Coba periksa satuannya lagi.",
    "SATUAN_KOSONG": "Angkamu benar! Sekarang pilih juga satuannya.",
    "SALAH_HITUNG": "Caramu sudah mendekati. Coba hitung ulang perkaliannya dengan teliti.",
    "SALAH_DESIMAL": "Angkamu 10 kali terlalu besar atau terlalu kecil. "
    "Periksa letak koma atau banyaknya angka nol.",
    "FORMAT_ANGKA": "Tulis jawabanmu sebagai angka, misalnya 1.200 atau 1,8.",
    "TIDAK_DIKENALI": "Jawabanmu belum tepat. Coba baca lagi langkahnya, atau buka petunjuk.",
}


@dataclass(frozen=True)
class Diagnosis:
    kode: str
    pesan: str


def buat(kode: str, pesan: str | None = None) -> Diagnosis:
    return Diagnosis(kode, pesan or PESAN[kode])


def diagnosis_angka(
    nilai: float,
    kunci: float,
    konteks: dict[str, Any] | None = None,
    pola_salah: list[dict[str, Any]] | None = None,
) -> Diagnosis:
    """Cari pola kesalahan yang paling mungkin untuk jawaban angka yang salah.

    Urutan: pola khusus dari bank soal → pola umum dari konteks (alas/tinggi/sisi) →
    salah letak koma → salah hitung kecil → tidak dikenali.
    """
    konteks = konteks or {}
    for pola in pola_salah or []:
        if samakah(nilai, float(pola["nilai"])):
            return buat(pola["kode"], pola.get("pesan"))

    alas = konteks.get("alas")
    tinggi = konteks.get("tinggi")
    if alas and tinggi:
        if samakah(nilai, alas * tinggi):
            return buat("LUPA_SETENGAH")
        if samakah(nilai, alas + tinggi) or samakah(nilai, (alas + tinggi) / 2):
            return buat("JUMLAH_BUKAN_KALI")

    sisi = konteks.get("sisi")
    if sisi and samakah(nilai, float(sum(sisi))):
        return buat("PAKAI_KELILING")

    sisi_miring = konteks.get("sisi_miring")
    if alas and sisi_miring and samakah(nilai, 0.5 * alas * sisi_miring):
        return buat("SALAH_TINGGI")

    if kunci:
        for faktor in (10, 100, 0.1, 0.01):
            if samakah(nilai, kunci * faktor):
                return buat("SALAH_DESIMAL")
        if abs(nilai - kunci) / abs(kunci) <= 0.2:
            return buat("SALAH_HITUNG")

    return buat("TIDAK_DIKENALI")
