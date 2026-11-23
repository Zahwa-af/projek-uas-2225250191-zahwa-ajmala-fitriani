"""Latihan "Soal Cerita Bertahap" dengan *fading* (Cognitive Load, Tahap 2C).

Pola: contoh lengkap (materi Belajar topik 5) → contoh hampir lengkap → lengkapi hitungan →
sedikit bantuan → mandiri (Renkl & Atkinson; Sweller, van Merriënboer & Paas 1998).
Dasar kebutuhan: wawancara S01 — GL01 (gambar + contoh cara menghitung), GL03 (petunjuk satu
per satu), IL04/EL05 (soal cerita & kegunaan angka), IL01 (alas vs tinggi).

CATATAN PENELITIAN: aturan naik/turun tingkat di bawah adalah rancangan berdasarkan analisis
kebutuhan dan diagnosis aplikasi, BELUM berdasarkan hasil uji coba instrumen.

- Latihan ini TIDAK berskor dan tidak menyentuh skor misi.
- Soal dibuat ulang dari (seed, tingkat) saat diperiksa, jadi kunci tidak dikirim ke browser.
- Pemeriksaan memakai penilai yang sama dengan misi (`penilai.periksa_langkah`), sehingga
  diagnosis kesalahan (lupa ½, salah tinggi, lupa banyak benda, salah satuan) konsisten.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from .penilai import HasilPeriksa, periksa_langkah

TINGKAT_MIN = 1
TINGKAT_MAKS = 4
PETUNJUK_MAKS = 3

# Bantuan per tingkat: langkah contoh yang DITAMPILKAN (sudah terisi) dan isian siswa.
# Semakin tinggi tingkat, semakin sedikit bantuan (fading).
TINGKAT: dict[int, dict[str, Any]] = {
    1: {
        "nama": "Contoh hampir lengkap",
        "keterangan": "Sebagian besar langkah sudah dikerjakan. Lengkapi langkah terakhir.",
        "tampil": ("diketahui", "ditanyakan", "rumus", "satu"),
        "isian": ("total",),
        "pengecoh": False,
    },
    2: {
        "nama": "Lengkapi hitungan",
        "keterangan": "Diketahui, ditanyakan, dan rumus sudah ada. Hitung sendiri luasnya.",
        "tampil": ("diketahui", "ditanyakan", "rumus"),
        "isian": ("satu", "total"),
        "pengecoh": False,
    },
    3: {
        "nama": "Sedikit bantuan",
        "keterangan": "Hanya data yang dipakai yang ditunjukkan. Rumus kamu ingat sendiri.",
        "tampil": ("diketahui",),
        "isian": ("satu", "total"),
        "pengecoh": True,
    },
    4: {
        "nama": "Mandiri",
        "keterangan": "Kerjakan sendiri. Petunjuk tetap bisa dibuka bila perlu.",
        "tampil": (),
        "isian": ("satu", "total"),
        "pengecoh": True,
    },
}

# (benda, bahan, satuan)
KONTEKS: tuple[tuple[str, str, str], ...] = (
    ("hiasan dinding", "kertas", "cm"),
    ("bendera", "kain", "cm"),
    ("ubin", "keramik", "cm"),
    ("layar perahu mainan", "kain", "cm"),
    ("petak taman", "rumput", "m"),
)

PILIHAN_SATUAN = {"cm": ["cm", "cm²", "m²"], "m": ["m", "m²", "cm²"]}


def _f(n: float) -> str:
    """Angka format Indonesia: 1200 → 1.200, 7.5 → 7,5."""
    if float(n).is_integer():
        return f"{int(n):,}".replace(",", ".")
    return f"{n:,.2f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",").replace("X", ".")


def normalkan_tingkat(tingkat: Any) -> int:
    try:
        t = int(tingkat)
    except (TypeError, ValueError):
        return TINGKAT_MIN
    return min(max(t, TINGKAT_MIN), TINGKAT_MAKS)


@dataclass(frozen=True)
class Data:
    benda: str
    bahan: str
    satuan: str
    alas: int
    tinggi: int
    banyak: int
    sisi_miring: int | None
    puncak: float  # posisi titik puncak di atas alas (0 = ujung kiri, 1 = ujung kanan)

    @property
    def luas_satu(self) -> float:
        return 0.5 * self.alas * self.tinggi

    @property
    def total(self) -> float:
        return self.banyak * self.luas_satu


# Tripel Pythagoras (jarak mendatar, tinggi, sisi miring): sisi miring pengecoh benar-benar
# cocok dengan bentuk segitiga yang digambar.
TRIPEL_CM = ((16, 12, 20), (20, 15, 25), (24, 18, 30), (18, 24, 30), (40, 30, 50))
TRIPEL_M = ((4, 3, 5), (8, 6, 10))


def buat_data(seed: int, tingkat: int) -> Data:
    """Angka dibuat dari seed. Tingkat 1–2: angka kecil tanpa pengecoh.
    Tingkat 3–4: angka lebih besar + sisi miring sebagai informasi pengecoh (IL01, EL05)."""
    tingkat = normalkan_tingkat(tingkat)
    rng = random.Random(f"{seed}-{tingkat}")
    benda, bahan, satuan = rng.choice(KONTEKS)
    banyak = rng.randint(2, 3) if tingkat <= 2 else rng.randint(3, 6)
    if TINGKAT[tingkat]["pengecoh"]:
        x, tinggi, sisi = rng.choice(TRIPEL_M if satuan == "m" else TRIPEL_CM)
        tambah = [k for k in ((2, 4) if satuan == "m" else (4, 6, 8, 10)) if x + k != sisi]
        alas = x + rng.choice(tambah)
        return Data(benda, bahan, satuan, alas, tinggi, banyak, sisi, round(1 - x / alas, 3))
    if satuan == "m":
        alas, tinggi = rng.choice([4, 6, 8, 10]), rng.choice([3, 5, 6, 7])
    else:
        alas, tinggi = rng.choice([10, 20, 30, 40]), rng.choice([10, 20, 30])
    return Data(benda, bahan, satuan, alas, tinggi, banyak, None, 0.35)


def _cerita(d: Data) -> list[str]:
    kalimat = [f"Sebuah {d.benda} berbentuk segitiga dengan alas {d.alas} {d.satuan}."]
    if d.sisi_miring:
        kalimat.append(
            f"Tingginya {d.tinggi} {d.satuan}, dan sisi miringnya {d.sisi_miring} {d.satuan}."
        )
    else:
        kalimat.append(f"Tingginya {d.tinggi} {d.satuan}.")
    kalimat.append(f"Ada {d.banyak} {d.benda} yang sama.")
    kalimat.append(f"Berapa luas {d.bahan} untuk semua {d.benda}?")
    return kalimat


def _hitung_satu(d: Data) -> str:
    kali = _f(d.alas * d.tinggi)
    return f"L = ½ × {d.alas} × {d.tinggi} = ½ × {kali} = {_f(d.luas_satu)} {d.satuan}²."


def _langkah_contoh(d: Data) -> dict[str, tuple[str, str]]:
    return {
        "diketahui": (
            "Diketahui",
            f"alas = {d.alas} {d.satuan}, tinggi = {d.tinggi} {d.satuan}, banyak = {d.banyak}.",
        ),
        "ditanyakan": ("Ditanyakan", f"luas {d.bahan} untuk {d.banyak} {d.benda}."),
        "rumus": ("Rumus", "L = ½ × alas × tinggi, lalu dikali banyak benda."),
        "satu": (
            "Hitung luas satu",
            _hitung_satu(d),
        ),
    }


_INSTRUKSI = {
    "satu": "Berapa luas satu {benda}?",
    "total": "Berapa luas {bahan} untuk semua {benda}?",
}


def _isian(d: Data, no: str) -> dict[str, Any]:
    """Bentuk isian sama dengan langkah tipe "angka" di misi.json, agar penilai bisa dipakai."""
    s2 = f"{d.satuan}²"
    if no == "satu":
        konteks: dict[str, Any] = {"alas": d.alas, "tinggi": d.tinggi}
        if d.sisi_miring:
            konteks["sisi_miring"] = d.sisi_miring
        return {
            "no": "satu",
            "tipe": "angka",
            "instruksi": _INSTRUKSI["satu"].format(benda=d.benda),
            "kunci": {"nilai": d.luas_satu, "satuan": s2},
            "konteks_diagnosis": konteks,
            "pilihan_satuan": PILIHAN_SATUAN[d.satuan],
            "penjelasan_benar": f"Tepat! Luas satu {d.benda} = {_f(d.luas_satu)} {s2}.",
        }
    pola = [
        {"nilai": d.luas_satu, "kode": "LUPA_JUMLAH_BENDA"},
        {
            "nilai": d.banyak * d.alas * d.tinggi,
            "kode": "LUPA_SETENGAH",
            "pesan": "Hasilmu 2 kali lebih besar. Sudahkah luas satu benda dikali ½?",
        },
    ]
    if d.sisi_miring:
        pola.append(
            {
                "nilai": d.banyak * 0.5 * d.alas * d.sisi_miring,
                "kode": "SALAH_TINGGI",
                "pesan": "Kamu memakai sisi miring. Tinggi harus tegak lurus dengan alas.",
            }
        )
    return {
        "no": "total",
        "tipe": "angka",
        "instruksi": _INSTRUKSI["total"].format(bahan=d.bahan, benda=d.benda),
        "kunci": {"nilai": d.total, "satuan": s2},
        "pola_salah": pola,
        "pilihan_satuan": PILIHAN_SATUAN[d.satuan],
        "penjelasan_benar": (
            f"Tepat! {d.banyak} × {_f(d.luas_satu)} = {_f(d.total)} {s2}. "
            f"Jadi, {d.bahan} yang dibutuhkan {_f(d.total)} {s2}."
        ),
    }


def _petunjuk(d: Data, no: str) -> list[str]:
    s2 = f"{d.satuan}²"
    if no == "satu":
        awal = "Luas satu benda memakai alas dan tinggi."
        if d.sisi_miring:
            awal += " Sisi miring tidak dipakai, karena tidak tegak lurus dengan alas."
        return [
            awal,
            "Rumusnya L = ½ × alas × tinggi.",
            _hitung_satu(d),
        ]
    return [
        f"Ada {d.banyak} benda yang sama. Luas semuanya = banyak × luas satu benda.",
        f"Cari luas satu benda dulu, lalu kalikan {d.banyak}.",
        f"Luas satu = {_f(d.luas_satu)} {s2}. Semuanya: {d.banyak} × {_f(d.luas_satu)} "
        f"= {_f(d.total)} {s2}.",
    ]


# ---------------------------------------------------------------- API modul
def soal_publik(seed: int, tingkat: Any) -> dict[str, Any]:
    """Soal untuk browser: cerita, gambar, langkah contoh sesuai tingkat, isian TANPA kunci."""
    t = normalkan_tingkat(tingkat)
    info = TINGKAT[t]
    d = buat_data(seed, t)
    contoh = _langkah_contoh(d)
    return {
        "seed": seed,
        "tingkat": t,
        "tingkat_maks": TINGKAT_MAKS,
        "nama_tingkat": info["nama"],
        "keterangan": info["keterangan"],
        "cerita": _cerita(d),
        "gambar": {
            "tipe": "segitiga",
            "alas": d.alas,
            "tinggi": d.tinggi,
            "satuan": d.satuan,
            "puncak": d.puncak,
            # Tingkat 3–4: angka diambil sendiri dari cerita (gambar tetap menunjukkan tinggi).
            "tanpa_angka": bool(d.sisi_miring),
            "judul": f"1 {d.benda} (ada {d.banyak})",
        },
        "langkah_contoh": [list(contoh[k]) for k in info["tampil"]],
        "isian": [
            {
                k: v
                for k, v in _isian(d, no).items()
                if k in {"no", "tipe", "instruksi", "pilihan_satuan"}
            }
            for no in info["isian"]
        ],
    }


def _isian_valid(t: int, no: str) -> bool:
    return no in TINGKAT[t]["isian"]


def periksa(seed: int, tingkat: Any, no: str, jawaban: dict[str, Any]) -> HasilPeriksa:
    t = normalkan_tingkat(tingkat)
    if not _isian_valid(t, no):
        raise ValueError("Isian tidak dikenal.")
    return periksa_langkah(_isian(buat_data(seed, t), no), jawaban)


def petunjuk(seed: int, tingkat: Any, no: str, ke: Any) -> dict[str, Any]:
    """Petunjuk ke-1..3 (bertahap; yang ke-3 berisi cara lengkap, GL03)."""
    t = normalkan_tingkat(tingkat)
    if not _isian_valid(t, no):
        raise ValueError("Isian tidak dikenal.")
    try:
        k = min(max(int(ke), 1), PETUNJUK_MAKS)
    except (TypeError, ValueError) as e:
        raise ValueError("Nomor petunjuk tidak valid.") from e
    return {"tingkat": k, "teks": _petunjuk(buat_data(seed, t), no)[k - 1]}


# ---------------------------------------------------------------- aturan fading
@dataclass(frozen=True)
class KeputusanFading:
    tingkat: int
    arah: str  # "naik" | "tetap" | "turun"
    pesan: str


AMBANG_TURUN_SALAH = 3  # total percobaan salah dalam satu soal


def tingkat_berikut(tingkat: Any, salah: int, petunjuk_tertinggi: int) -> KeputusanFading:
    """Tentukan tingkat bantuan untuk soal berikutnya.

    - Benar tanpa salah dan tanpa petunjuk → bantuan dikurangi SATU tingkat (tidak langsung
      mandiri; "jangan langsung menghilangkan semua bantuan").
    - Membuka petunjuk ke-3 (cara lengkap) atau salah ≥ 3 kali → bantuan ditambah satu tingkat.
    - Selain itu (sedikit salah / petunjuk 1–2) → tetap di tingkat yang sama.
    """
    t = normalkan_tingkat(tingkat)
    salah = max(int(salah or 0), 0)
    pt = max(int(petunjuk_tertinggi or 0), 0)
    if pt >= PETUNJUK_MAKS or salah >= AMBANG_TURUN_SALAH:
        if t == TINGKAT_MIN:
            return KeputusanFading(
                t, "tetap", "Tidak apa-apa. Coba soal lain dengan bantuan yang sama."
            )
        return KeputusanFading(
            t - 1, "turun", "Soal berikutnya diberi bantuan lebih banyak. Pelan-pelan saja."
        )
    if salah == 0 and pt == 0:
        if t == TINGKAT_MAKS:
            return KeputusanFading(t, "tetap", "Hebat! Kamu sudah bisa mengerjakan sendiri.")
        return KeputusanFading(
            t + 1, "naik", "Kamu benar tanpa bantuan. Bantuan di soal berikutnya dikurangi."
        )
    return KeputusanFading(t, "tetap", "Bagus! Coba satu soal lagi dengan bantuan yang sama.")


# Pertanyaan penjelasan diri (Germane): siswa menulis dulu, lalu membandingkan.
_REFLEKSI = (
    (
        "Mengapa luas segitiga dikali ½?",
        "Segitiga adalah setengah dari persegi panjang dengan alas dan tinggi yang sama. "
        "Jadi luasnya setengah dari alas × tinggi.",
    ),
    (
        "Mengapa luas satu benda masih harus dikali banyak benda?",
        "Rumus segitiga hanya memberi luas satu benda. "
        "Karena bendanya ada beberapa, luas semuanya = banyak × luas satu.",
    ),
)
_REFLEKSI_PENGECOH = (
    "Mengapa sisi miring tidak dipakai dalam rumus luas?",
    "Tinggi harus tegak lurus dengan alas. Sisi miring tidak tegak lurus dengan alas, "
    "jadi bukan tinggi.",
)


def refleksi(seed: int, tingkat: Any) -> dict[str, str]:
    t = normalkan_tingkat(tingkat)
    pilihan = list(_REFLEKSI) + ([_REFLEKSI_PENGECOH] if TINGKAT[t]["pengecoh"] else [])
    tanya, penjelasan = pilihan[int(seed) % len(pilihan)]
    return {"tanya": tanya, "penjelasan": penjelasan}
