"""Memeriksa jawaban per langkah dan menghitung skor rubrik misi."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any

from .diagnosis import PESAN, diagnosis_angka
from .parser_angka import parse_angka, parse_satuan, samakah

TINGKAT_PETUNJUK_MAKS = 3
BATAS_PERCOBAAN = 3


@dataclass
class HasilPeriksa:
    benar: bool
    kode: str | None
    umpan_balik: str


@dataclass
class StatusLangkah:
    benar: bool = False
    tingkat_petunjuk: int = 0


@dataclass
class SkorMisi:
    skor: float
    maks: float
    rincian: list[dict[str, Any]] = field(default_factory=list)
    bintang: int = 0
    total_petunjuk: int = 0


def _benar(langkah: dict[str, Any]) -> HasilPeriksa:
    return HasilPeriksa(True, None, langkah.get("penjelasan_benar", "Tepat!"))


def _salah(kode: str, pesan: str | None = None) -> HasilPeriksa:
    return HasilPeriksa(False, kode, pesan or PESAN.get(kode, PESAN["TIDAK_DIKENALI"]))


# ---------------------------------------------------------------- pilihan ganda
def _periksa_pilihan(langkah: dict[str, Any], jawaban: dict[str, Any]) -> HasilPeriksa:
    kunci = langkah["kunci"]
    kunci_set = set(kunci) if isinstance(kunci, list) else {kunci}
    dipilih = jawaban.get("pilihan")
    dipilih_set = set(dipilih) if isinstance(dipilih, list) else ({dipilih} if dipilih else set())
    if not dipilih_set:
        return _salah("KOSONG", "Pilih jawabanmu dulu.")
    if dipilih_set == kunci_set:
        return _benar(langkah)

    teks_opsi = {o["id"]: o["teks"] for o in langkah["opsi"]}
    umpan_opsi = langkah.get("umpan_balik_opsi", {})
    keliru = sorted(dipilih_set - kunci_set)
    if keliru:
        pertama = keliru[0]
        pesan = umpan_opsi.get(pertama)
        if not pesan:
            pesan = (
                f"Pilihan “{teks_opsi.get(pertama, pertama)}” belum tepat. Baca lagi pertanyaannya."
            )
        return _salah("PILIHAN_SALAH", pesan)
    kurang = len(kunci_set) - len(dipilih_set)
    return _salah(
        "KURANG_LENGKAP",
        f"Pilihanmu sudah benar, tetapi masih kurang {kurang}. Pilih {len(kunci_set)} jawaban.",
    )


# ---------------------------------------------------------------- isian angka
def _periksa_angka(langkah: dict[str, Any], jawaban: dict[str, Any]) -> HasilPeriksa:
    kunci = langkah["kunci"]
    target = float(kunci["nilai"])
    nilai = parse_angka(jawaban.get("nilai"))
    if nilai is None:
        return _salah("FORMAT_ANGKA")

    if samakah(nilai, target):
        satuan_kunci = kunci.get("satuan")
        if satuan_kunci and satuan_kunci != "Rp":
            satuan = parse_satuan(jawaban.get("satuan"))
            if not satuan:
                return _salah("SATUAN_KOSONG")
            if satuan != satuan_kunci:
                pesan = PESAN["SALAH_SATUAN"]
                if satuan_kunci.endswith("²") and not satuan.endswith("²"):
                    pesan = "Angkamu benar! Satuan luas memakai pangkat dua, misalnya cm² atau m²."
                elif satuan_kunci.rstrip("²") != satuan.rstrip("²"):
                    dasar = satuan_kunci.rstrip("²")
                    pesan = f"Angkamu benar! Perhatikan satuan pada soal: ukurannya dalam {dasar}."
                return _salah("SALAH_SATUAN", pesan)
        return _benar(langkah)

    d = diagnosis_angka(nilai, target, langkah.get("konteks_diagnosis"), langkah.get("pola_salah"))
    return _salah(d.kode, d.pesan)


# ---------------------------------------------------------------- kalimat rumpang
def _susunan_kunci(isian: list[float], bebas_tukar: list[list[int]]) -> list[list[float]]:
    """Semua susunan kunci yang diterima (misal alas & tinggi boleh tertukar)."""
    hasil = []
    for pilihan in itertools.product([False, True], repeat=len(bebas_tukar)):
        s = list(isian)
        for tukar, (i, j) in zip(pilihan, bebas_tukar, strict=True):
            if tukar:
                s[i], s[j] = s[j], s[i]
        hasil.append(s)
    return hasil


def _periksa_rumus(langkah: dict[str, Any], jawaban: dict[str, Any]) -> HasilPeriksa:
    kunci = langkah["kunci"]
    isian_kunci = [parse_angka(x) for x in kunci["isian"]]
    isian = jawaban.get("isian") or []
    if len(isian) != len(isian_kunci):
        return _salah("KOSONG", "Isi semua kotak dulu.")
    nilai = [parse_angka(x) for x in isian]
    for i, v in enumerate(nilai):
        if v is None:
            return _salah("FORMAT_ANGKA", f"Kotak ke-{i + 1} belum berisi angka.")

    susunan = _susunan_kunci(isian_kunci, kunci.get("bebas_tukar", []))
    terbaik: list[int] | None = None
    for s in susunan:
        salah = [i for i, (v, k) in enumerate(zip(nilai, s, strict=True)) if not samakah(v, k)]
        if not salah:
            return _benar(langkah)
        if terbaik is None or len(salah) < len(terbaik):
            terbaik = salah
    assert terbaik is not None

    for pola in langkah.get("pola_salah_isian", []):
        i = pola["isian_ke"] - 1
        if i in terbaik and samakah(nilai[i], float(parse_angka(pola["nilai"]) or 0)):
            return _salah(pola["kode"], pola.get("pesan"))

    daftar = ", ".join(f"ke-{i + 1}" for i in terbaik)
    return _salah("RUMUS_SALAH", f"Kotak {daftar} belum tepat. Kotak lainnya sudah benar.")


# ---------------------------------------------------------------- pilah informasi
def _periksa_pilah(langkah: dict[str, Any], jawaban: dict[str, Any]) -> HasilPeriksa:
    kunci: dict[str, str] = langkah["kunci"]
    penempatan: dict[str, str] = jawaban.get("penempatan") or {}
    teks_item = {it["id"]: it["teks"] for it in langkah["item"]}
    belum = [i for i in kunci if not penempatan.get(i)]
    if belum:
        return _salah("KOSONG", f"Masih ada {len(belum)} yang belum ditempatkan.")
    keliru = [i for i in kunci if penempatan.get(i) != kunci[i]]
    if not keliru:
        return _benar(langkah)
    nama = ", ".join(f"“{teks_item[i]}”" for i in keliru)
    pesan = f"Cek lagi: {nama} belum di tempat yang tepat."
    khusus = langkah.get("umpan_balik_item", {}).get(keliru[0])
    if khusus:
        pesan += " " + khusus
    return _salah("PILAH_SALAH", pesan)


_PEMERIKSA = {
    "pilihan": _periksa_pilihan,
    "angka": _periksa_angka,
    "rumus": _periksa_rumus,
    "pilah": _periksa_pilah,
}


def periksa_langkah(langkah: dict[str, Any], jawaban: dict[str, Any]) -> HasilPeriksa:
    """Periksa jawaban siswa untuk satu langkah."""
    pemeriksa = _PEMERIKSA.get(langkah["tipe"])
    if pemeriksa is None:
        raise ValueError(f"Tipe langkah tidak dikenal: {langkah['tipe']}")
    if not isinstance(jawaban, dict):
        return _salah("KOSONG", "Isi jawabanmu dulu.")
    return pemeriksa(langkah, jawaban)


# ---------------------------------------------------------------- skor
def langkah_dapat_skor(status: StatusLangkah) -> bool:
    """Skor penuh jika benar tanpa membuka petunjuk tingkat 3 (cara lengkap)."""
    return status.benar and status.tingkat_petunjuk < TINGKAT_PETUNJUK_MAKS


def hitung_bintang(skor: float, maks: float, total_petunjuk: int) -> int:
    if skor >= maks and total_petunjuk <= 1:
        return 3
    if skor >= 4:
        return 2
    return 1


def hitung_skor_misi(misi: dict[str, Any], status: dict[str, StatusLangkah]) -> SkorMisi:
    """Hitung skor rubrik (maks 6) per tahapan sesuai kisi-kisi."""
    per_tahap: dict[int, dict[str, float]] = {}
    total_petunjuk = 0
    for langkah in misi["langkah"]:
        st = status.get(langkah["no"], StatusLangkah())
        total_petunjuk += st.tingkat_petunjuk
        t = per_tahap.setdefault(langkah["tahap"], {"skor": 0.0, "maks": 0.0})
        t["maks"] += langkah["skor"]
        if langkah_dapat_skor(st):
            t["skor"] += langkah["skor"]
    rincian = [
        {"tahap": k, "skor": v["skor"], "maks": v["maks"]} for k, v in sorted(per_tahap.items())
    ]
    skor = sum(r["skor"] for r in rincian)
    maks = sum(r["maks"] for r in rincian)
    return SkorMisi(skor, maks, rincian, hitung_bintang(skor, maks, total_petunjuk), total_petunjuk)


def kategori_literasi(total: float) -> str:
    """Kategori dari total skor 4 misi (maks 24)."""
    if total >= 20:
        return "Sangat baik"
    if total >= 15:
        return "Baik"
    if total >= 10:
        return "Cukup"
    return "Perlu bimbingan"
