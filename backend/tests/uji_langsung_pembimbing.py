"""Uji LANGSUNG chatbot beranda ke model sungguhan (memakai kuota OpenRouter/DeepSeek).

Sengaja tidak bernama test_*.py agar tidak ikut `pytest` (butuh internet & kuota, dan
jawaban model bisa bervariasi). Jalankan manual dari folder proyek:

    .venv\\Scripts\\python backend\\tests\\uji_langsung_pembimbing.py

Memakai konfigurasi .env, kode server saat ini, dan database SEMENTARA (data asli tidak
tersentuh). API key tidak pernah dicetak.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR / "backend"))

from dotenv import dotenv_values  # noqa: E402

from api.routes_asisten import KUNCI_KLIEN  # noqa: E402
from app import buat_app  # noqa: E402
from asisten.klien import KlienDeepSeek  # noqa: E402
from asisten.konfigurasi import dari_env  # noqa: E402
from asisten.pengaman import menyuruh_siswa_menghitung  # noqa: E402

SOAL_HIASAN = (
    "Sebuah hiasan dinding berbentuk segitiga memiliki alas 40 cm dan tinggi 30 cm. "
    "Hiasan itu dibuat oleh 5 siswa. Berapa luas hiasan dinding itu?"
)
LUAS_600 = r"600\s*cm(²|2|\^2)"

# (kode, kelompok sesi, pertanyaan, pola wajib, keterangan)
KASUS = [
    (
        "A",
        "a",
        "Hitung luas segitiga dengan alas 10 cm dan tinggi 6 cm.",
        [r"30\s*cm(²|2|\^2)"],
        "langkah lengkap sampai 30 cm²",
    ),
    (
        "B",
        "b",
        "Berapa luas segitiga dengan alas 40 cm dan tinggi 30 cm?",
        [LUAS_600],
        "langkah lengkap sampai 600 cm²",
    ),
    ("Soal cerita", "c", SOAL_HIASAN, [LUAS_600], "langsung 600 cm² (5 siswa diabaikan)"),
    (
        "C",
        "c",
        "Aku tidak tahu, coba kamu hitung.",
        [LUAS_600],
        "lanjutan soal hiasan: langsung hasil lengkap 600 cm²",
    ),
    (
        "D",
        "d",
        "Apa itu segitiga sama sisi?",
        [r"(ketiga|tiga|ke-?3|semua)\s+sisi(nya)?\s+(sama|yang sama)", r"60"],
        "definisi benar: ketiga sisi sama panjang, sudut 60°",
    ),
    ("E", "e", "Apa ibu kota Indonesia?", [r"Jakarta|Nusantara"], "jawaban langsung sesuai fakta"),
]


class Penghitung:
    """Membungkus klien asli untuk menghitung panggilan (deteksi 'minta ulang')."""

    sumber = "deepseek"

    def __init__(self, klien):
        self.klien = klien
        self.jumlah = 0

    def balas(self, pesan):
        self.jumlah += 1
        return self.klien.balas(pesan)


def periksa(kode: str, balasan: str, wajib: list[str]) -> list[str]:
    masalah = [f"tidak memuat /{p}/" for p in wajib if not re.search(p, balasan, re.I)]
    if menyuruh_siswa_menghitung(balasan):
        masalah.append("menyuruh siswa menghitung sendiri")
    if balasan.rstrip().endswith("?"):
        masalah.append("diakhiri pertanyaan")
    if kode == "E" and "segitiga" in balasan.lower():
        masalah.append("memaksakan materi segitiga")
    return masalah


def main() -> int:
    konfig = dari_env(dotenv_values(AKAR / ".env"))
    if konfig.mode != "deepseek":
        print(f"Mode chatbot di .env adalah '{konfig.mode}', bukan 'deepseek'. Uji dibatalkan.")
        return 2
    print(f"Model: {konfig.model} | base_url: {konfig.base_url}\n")

    with tempfile.TemporaryDirectory() as tmp:
        hitung = Penghitung(KlienDeepSeek(konfig))
        app = buat_app(
            {"DB_PATH": str(Path(tmp) / "uji.db"), "ASISTEN": konfig, "ASISTEN_KLIEN": hitung}
        )
        assert app.extensions[KUNCI_KLIEN] is hitung
        c = app.test_client()
        sesi: dict[str, str] = {}
        gagal = 0
        kasus = KASUS
        pilihan = {a.upper() for a in sys.argv[1:]}  # mis.: ... uji_langsung_pembimbing.py D
        kasus = [
            k for k in KASUS if not pilihan or k[0].upper() in pilihan or k[1].upper() in pilihan
        ]
        for kode, kelompok, tanya, wajib, ket in kasus:
            if kelompok not in sesi:  # sesi baru per kelompok; C memakai sesi soal cerita
                r = c.post("/api/sesi", json={"nama_panggilan": "Uji", "kode_kelas": "UJI"})
                sesi[kelompok] = r.get_json()["sesi_id"]
            sebelum = hitung.jumlah
            r = c.post("/api/asisten/beranda", json={"sesi_id": sesi[kelompok], "teks": tanya})
            data = r.get_json() or {}
            balasan = (data.get("balasan") or data.get("galat") or "").replace(
                konfig.api_key, "[KEY]"
            )
            masalah = (
                [f"HTTP {r.status_code}"] if r.status_code != 200 else periksa(kode, balasan, wajib)
            )
            gagal += bool(masalah)
            ulang = hitung.jumlah - sebelum > 1
            print(f"[{kode}] SISWA : {tanya}")
            print(f"     HARAP : {ket}")
            print("     AI    :", balasan.replace("\n", "\n             "))
            catatan = "MEMINTA ULANG ke model" if ulang else "tidak perlu meminta ulang"
            print(f"     CATATAN: server {catatan}")
            print("     HASIL :", "LULUS" if not masalah else "GAGAL - " + "; ".join(masalah))
            print("-" * 72)
    print(f"\n{len(kasus) - gagal} dari {len(kasus)} kasus lulus.")
    return 1 if gagal else 0


if __name__ == "__main__":
    raise SystemExit(main())
