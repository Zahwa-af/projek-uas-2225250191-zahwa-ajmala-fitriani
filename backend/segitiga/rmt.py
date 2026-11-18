"""Label Rigorous Mathematical Thinking (RMT) untuk data penelitian — Tahap 1.

Rujukan: Kinard & Kozulin, *Rigorous Mathematical Thinking* (ringkasan 15 hal.), lihat
docs/07-analisis-rmt.md dan docs/12-audit-rmt.md.

- TAHAP: kerangka Analisis Tugas [hal. 8] + Representasi → Manipulasi → Validasi [hal. 14].
  "Perencanaan" belum dipakai karena misi belum punya langkah perencanaan (Tahap 3).
- FASE: fungsi kognitif Input → Elaborasi → Output [hal. 9–10]; dipakai untuk mendiagnosis
  fase yang mengalami kendala [hal. 12].

STATUS: USULAN PENELITI, BELUM DIKONFIRMASI DOSEN. Ubah di file ini saja bila diputuskan lain.
Modul ini tidak memengaruhi soal, kunci, skor, maupun jawaban chatbot (hanya label data).
"""

from __future__ import annotations

ANALISIS_TUGAS = "analisis_tugas"
REPRESENTASI = "representasi"
MANIPULASI = "manipulasi"
VALIDASI = "validasi"
SEMUA_TAHAP = (ANALISIS_TUGAS, REPRESENTASI, MANIPULASI, VALIDASI)

INPUT = "input"
ELABORASI = "elaborasi"
OUTPUT = "output"
SEMUA_FASE = (INPUT, ELABORASI, OUTPUT)

# Tahap RMT setiap langkah misi: (misi_id, no_langkah) -> tahap.
TAHAP_LANGKAH: dict[tuple[int, str], str] = {
    # Misi 1 — Bendera Kelas (Reasoning)
    (1, "1a"): ANALISIS_TUGAS,  # memilah ukuran ke alas/tinggi
    (1, "1b"): ANALISIS_TUGAS,  # menentukan yang harus dibandingkan
    (1, "2a"): MANIPULASI,  # menghitung luas A
    (1, "2b"): MANIPULASI,  # menghitung luas B
    (1, "3"): VALIDASI,  # membandingkan hasil
    (1, "4"): VALIDASI,  # mengambil keputusan dari hasil
    (1, "5"): VALIDASI,  # memberi alasan matematis
    # Misi 2 — Kanopi Sekolah (Formulating)
    (2, "1"): ANALISIS_TUGAS,
    (2, "2"): ANALISIS_TUGAS,
    (2, "3"): REPRESENTASI,  # memilih model L = ½ × a × t
    (2, "4"): MANIPULASI,
    (2, "5"): MANIPULASI,
    (2, "6"): MANIPULASI,
    # Misi 3 — Taman Sekolah (Employing)
    (3, "1"): ANALISIS_TUGAS,
    (3, "2a"): REPRESENTASI,  # substitusi ke rumus
    (3, "2b"): MANIPULASI,
    (3, "3a"): REPRESENTASI,  # model ⅓ × luas
    (3, "3b"): MANIPULASI,
    (3, "4"): MANIPULASI,
    # Misi 4 — Papan Informasi (Interpreting/Evaluating)
    (4, "1"): ANALISIS_TUGAS,  # memahami yang dilakukan Dika
    (4, "2"): REPRESENTASI,  # memilih rumus yang benar
    (4, "3"): MANIPULASI,
    (4, "4"): VALIDASI,  # menafsirkan 3,6 vs 1,8
    (4, "5"): VALIDASI,  # menilai perhitungan Dika
    (4, "6"): VALIDASI,  # menyimpulkan kebutuhan kain
}

# Fase kognitif yang paling mungkin bermasalah untuk setiap kode kesalahan Python
# (usulan docs/07 §7.4). SALAH_HITUNG: usulan Output — menunggu keputusan dosen (Q5).
FASE_KESALAHAN: dict[str, str] = {
    "PILAH_SALAH": INPUT,
    "KURANG_LENGKAP": INPUT,
    "TERTUKAR_BAGIAN": INPUT,
    "LUPA_SETENGAH": ELABORASI,
    "JUMLAH_BUKAN_KALI": ELABORASI,
    "PAKAI_KELILING": ELABORASI,
    "SALAH_TINGGI": ELABORASI,
    "LUPA_JUMLAH_BENDA": ELABORASI,
    "RUMUS_SALAH": ELABORASI,
    "SALAH_SATUAN": OUTPUT,
    "SATUAN_KOSONG": OUTPUT,
    "SALAH_DESIMAL": OUTPUT,
    "SALAH_HITUNG": OUTPUT,
}

# Kode yang fasenya bergantung pada langkahnya (tidak spesifik): pakai tahap langkah.
FASE_DARI_TAHAP: dict[str, str] = {
    ANALISIS_TUGAS: INPUT,
    REPRESENTASI: ELABORASI,
    MANIPULASI: ELABORASI,
    VALIDASI: OUTPUT,
}

# Bukan kesalahan berpikir (isian kosong / format tidak terbaca): tidak diberi fase.
BUKAN_KESALAHAN = {"KOSONG", "FORMAT_ANGKA"}


def tahap_langkah(misi_id: int, no: str) -> str | None:
    return TAHAP_LANGKAH.get((int(misi_id), str(no)))


def fase_kesalahan(kode: str | None, misi_id: int, no: str) -> str | None:
    """Fase kognitif (input/elaborasi/output) untuk sebuah kode kesalahan pada langkah tertentu.

    Kode spesifik dipetakan langsung; kode umum (PILIHAN_SALAH, TIDAK_DIKENALI) mengikuti
    tahap langkahnya. Tanpa kode atau bukan kesalahan berpikir → None.
    """
    if not kode or kode in BUKAN_KESALAHAN:
        return None
    if kode in FASE_KESALAHAN:
        return FASE_KESALAHAN[kode]
    tahap = tahap_langkah(misi_id, no)
    return FASE_DARI_TAHAP.get(tahap) if tahap else None
