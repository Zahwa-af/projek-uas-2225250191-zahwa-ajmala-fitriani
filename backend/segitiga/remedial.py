"""Saran remedial adaptif dari jejak kesalahan siswa di aplikasi (Cognitive Load, Tahap 2C).

Sumber data: tabel `jawaban_langkah` (kode diagnosis jawaban salah) dan `petunjuk_dibuka`
(petunjuk ke-3 = cara lengkap) milik sesi siswa itu sendiri. Modul ini HANYA membaca data;
skor, jawaban, dan riwayat siswa tidak diubah atau dihapus.

CATATAN PENELITIAN: pemetaan kesalahan → materi penguatan dan ambang "perlu diperkuat"
disusun dari analisis kebutuhan (wawancara S01: IL01, IL03, IL04, IL05, EL05) dan diagnosis
aplikasi, BELUM berdasarkan analisis hasil uji coba instrumen Mathematical Literacy.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from . import rmt

# Bobot satu jawaban salah dan satu petunjuk ke-3 (cara lengkap) yang terbuka.
BOBOT_SALAH = 1
BOBOT_PETUNJUK_LENGKAP = 1
# Area disarankan bila bobotnya mencapai ambang ini (satu kali keliru belum dianggap kesulitan).
AMBANG = 2
# Paling banyak area yang ditampilkan sekaligus (mengurangi extraneous load).
MAKS_SARAN = 2


@dataclass(frozen=True)
class Area:
    id: str
    judul: str
    pesan: str
    tautan: tuple[tuple[str, str], ...]  # (label, href)


AREA: dict[str, Area] = {
    "alas_tinggi": Area(
        "alas_tinggi",
        "Menentukan alas dan tinggi",
        "Tinggi harus tegak lurus dengan alas. Ulangi materinya, lalu latih menunjuk tinggi.",
        (
            ("Materi alas dan tinggi", "#/belajar/2/1"),
            ("Latihan Tunjuk Tingginya", "#/latihan/tinggi"),
        ),
    ),
    "rumus_luas": Area(
        "rumus_luas",
        "Rumus luas segitiga",
        "Luas segitiga = ½ × alas × tinggi. Lihat lagi asal rumusnya, lalu berlatih bertahap.",
        (("Materi rumus luas", "#/belajar/4/1"), ("Soal Cerita Bertahap", "#/latihan/bertahap")),
    ),
    "luas_keliling": Area(
        "luas_keliling",
        "Membedakan luas dan keliling",
        "Keliling mengukur tepi, luas mengukur daerah. Bandingkan keduanya.",
        (("Bandingkan keliling dan luas", "#/belajar/4/5"), ("Materi keliling", "#/belajar/3/1")),
    ),
    "memilah_info": Area(
        "memilah_info",
        "Memilah informasi soal cerita",
        "Tentukan dulu angka mana yang dipakai dan apa yang ditanyakan.",
        (("Latihan Pilah Informasi", "#/latihan/pilah"), ("Langkah soal cerita", "#/belajar/5/1")),
    ),
    "satuan": Area(
        "satuan",
        "Satuan luas",
        "Satuan luas memakai pangkat dua, misalnya cm² atau m².",
        (("Materi satuan luas", "#/belajar/4/4"), ("Soal Cerita Bertahap", "#/latihan/bertahap")),
    ),
    "operasi_hitung": Area(
        "operasi_hitung",
        "Operasi hitung",
        "Caramu sudah benar, tetapi hitungannya meleset. Hitung bertahap dan periksa lagi.",
        (("Soal Cerita Bertahap", "#/latihan/bertahap"),),
    ),
    "menafsirkan": Area(
        "menafsirkan",
        "Menafsirkan hasil dan menyimpulkan",
        "Setelah menghitung, bandingkan hasilnya dengan pertanyaan soal, lalu tulis kesimpulan.",
        (("Langkah menyimpulkan", "#/belajar/5/5"), ("Soal Cerita Bertahap", "#/latihan/bertahap")),
    ),
}

# Kode diagnosis (penilai/diagnosis.py) → area materi.
AREA_KODE: dict[str, str] = {
    "SALAH_TINGGI": "alas_tinggi",
    "LUPA_SETENGAH": "rumus_luas",
    "JUMLAH_BUKAN_KALI": "rumus_luas",
    "RUMUS_SALAH": "rumus_luas",
    "PAKAI_KELILING": "luas_keliling",
    "PILAH_SALAH": "memilah_info",
    "KURANG_LENGKAP": "memilah_info",
    "TERTUKAR_BAGIAN": "memilah_info",
    "LUPA_JUMLAH_BENDA": "memilah_info",
    "SALAH_SATUAN": "satuan",
    "SATUAN_KOSONG": "satuan",
    "SALAH_HITUNG": "operasi_hitung",
    "SALAH_DESIMAL": "operasi_hitung",
}

# Kode umum (PILIHAN_SALAH, TIDAK_DIKENALI) dan petunjuk ke-3: ikuti fase kognitif langkahnya.
AREA_FASE: dict[str, str] = {
    rmt.INPUT: "memilah_info",
    rmt.ELABORASI: "rumus_luas",
    rmt.OUTPUT: "menafsirkan",
}


def area_kesalahan(kode: str | None, misi_id: int, langkah: str) -> str | None:
    """Area materi untuk satu jawaban salah. Isian kosong/format tidak terbaca → None."""
    if not kode or kode in rmt.BUKAN_KESALAHAN:
        return None
    if kode in AREA_KODE:
        return AREA_KODE[kode]
    fase = rmt.fase_kesalahan(kode, misi_id, langkah)
    return AREA_FASE.get(fase) if fase else None


def area_langkah(misi_id: int, langkah: str) -> str | None:
    tahap = rmt.tahap_langkah(misi_id, langkah)
    fase = rmt.FASE_DARI_TAHAP.get(tahap) if tahap else None
    return AREA_FASE.get(fase) if fase else None


def saran(
    kesalahan: Iterable[tuple[str | None, int, str]],
    petunjuk_lengkap: Iterable[tuple[int, str]] = (),
) -> list[dict[str, Any]]:
    """Daftar area yang perlu diperkuat, urut dari yang paling sering bermasalah.

    kesalahan: (kode_diagnosis, misi_id, no_langkah) untuk setiap jawaban SALAH.
    petunjuk_lengkap: (misi_id, no_langkah) untuk setiap langkah yang petunjuk ke-3-nya terbuka.
    """
    bobot: Counter[str] = Counter()
    rincian: dict[str, Counter[str]] = {}
    misi: dict[str, set[int]] = {}
    for kode, misi_id, no in kesalahan:
        a = area_kesalahan(kode, misi_id, no)
        if a:
            bobot[a] += BOBOT_SALAH
            rincian.setdefault(a, Counter())[str(kode)] += 1
            misi.setdefault(a, set()).add(int(misi_id))
    for misi_id, no in petunjuk_lengkap:
        a = area_langkah(misi_id, no)
        if a:
            bobot[a] += BOBOT_PETUNJUK_LENGKAP
            rincian.setdefault(a, Counter())["PETUNJUK_LENGKAP"] += 1
            misi.setdefault(a, set()).add(int(misi_id))

    urut = sorted(
        (a for a, b in bobot.items() if b >= AMBANG),
        key=lambda a: (-bobot[a], list(AREA).index(a)),
    )
    hasil = []
    for a in urut[:MAKS_SARAN]:
        ar = AREA[a]
        hasil.append(
            {
                "area": ar.id,
                "judul": ar.judul,
                "pesan": ar.pesan,
                "bobot": bobot[a],
                "kode": dict(rincian[a]),
                "misi": sorted(misi[a]),
                "tautan": [{"label": lbl, "href": href} for lbl, href in ar.tautan],
            }
        )
    return hasil
