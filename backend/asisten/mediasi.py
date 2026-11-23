"""Mediasi RMT untuk chatbot MISI (Tahap 2F) — dipakai prompt.susun_pesan().

Isi:
- `PRINSIP_MEDIASI`: kriteria MLE (intensionalitas, makna, resiprositas) + batas beban kognitif
  untuk setiap balasan [docs/07 §7.1].
- `tingkat_bantuan()`: tingkat 0–3, DITENTUKAN SERVER dari status siswa (bukan oleh model)
  [docs/07 §7.2, docs/13 §4.2].
- `instruksi_mediasi()`: fokus sesuai tahap RMT langkah dan fase kesalahan terakhir.

STATUS: kerangka tahap/fase = usulan peneliti yang sama dengan segitiga/rmt.py (Tahap 1),
BELUM dikonfirmasi dosen (docs/07 Q1). Ubah di file ini saja bila diputuskan lain.
Chatbot misi TETAP tidak menyebut jawaban akhir langkah yang belum benar (docs/07 §7.2);
penyaring jawaban di pengaman.py tidak diubah. Chatbot BERANDA tidak memakai modul ini.
"""

from __future__ import annotations

PRINSIP_MEDIASI = """\
Cara membimbing (mediasi Rigorous Mathematical Thinking dan beban kognitif):
- Intensionalitas: sebut dengan jelas fokus saat ini, misalnya "Kita fokus mencari tinggi dulu."
- Makna: sesekali jelaskan alasannya, misalnya "½ dipakai karena segitiga adalah setengah \
persegi panjang."
- Resiprositas: ajak siswa berpikir. Jika langkah belum benar, akhiri dengan SATU pertanyaan \
pendek.
- Satu ide per balasan, kalimat pendek, paling banyak sekitar 120 kata. Rujuk gambar yang \
sudah tampil: alas = garis biru, tinggi = garis oranye putus-putus.
- Jangan menambahkan informasi yang tidak dibutuhkan langkah ini."""

# Tahap RMT langkah (segitiga/rmt.py) → fokus bimbingan.
FOKUS_TAHAP: dict[str, str] = {
    "analisis_tugas": "Tahap Analisis Tugas (Input): bantu siswa mengenali informasi yang "
    "diketahui, yang ditanyakan, dan kegunaan setiap angka. Pisahkan angka pengecoh.",
    "representasi": "Tahap Representasi (Elaborasi): bantu siswa menerjemahkan cerita ke gambar "
    "dan model L = ½ × alas × tinggi, serta memahami alasan rumus itu.",
    "manipulasi": "Tahap Manipulasi (Elaborasi): bantu siswa melakukan substitusi dan menghitung "
    "bertahap (kalikan dua angka dulu, lalu ½), tanpa coba-coba.",
    "validasi": "Tahap Validasi (Output): bantu siswa memeriksa apakah hasil masuk akal, "
    "satuannya tepat, dan benar-benar menjawab pertanyaan.",
}

# Fase fungsi kognitif tempat kesalahan terakhir terjadi → arah bantuan.
FOKUS_FASE: dict[str, str] = {
    "input": "Kesalahan terakhir ada pada fase Input: arahkan siswa membaca ulang data dan "
    "memilih informasi yang tepat.",
    "elaborasi": "Kesalahan terakhir ada pada fase Elaborasi: arahkan pada hubungan alas–tinggi, "
    "pemilihan rumus, atau alasan dikali ½.",
    "output": "Kesalahan terakhir ada pada fase Output: arahkan pada ketelitian hitung, satuan, "
    "dan cara menuliskan hasil.",
}

# Bantuan bertambah sedikit demi sedikit saat siswa makin kesulitan (kebalikan dari fading).
BANTUAN: dict[int, str] = {
    0: "Tingkat bantuan 0 (siswa belum salah): jika ditanya konsep atau rumus, jelaskan langsung "
    "dan lengkap. Untuk langkah ini, beri pertanyaan pemantik terbuka.",
    1: "Tingkat bantuan 1 (siswa salah 1 kali): tunjukkan BAGIAN yang perlu diperiksa sesuai "
    "fase kesalahan, beri penjelasan konsep singkat, lalu satu pertanyaan pemandu.",
    2: "Tingkat bantuan 2 (salah 2 kali atau lebih, atau sudah membuka 2 petunjuk): beri CONTOH "
    'SERUPA dengan angka BERBEDA yang diselesaikan lengkap sampai "Jadi, ...", lalu jelaskan '
    "cara menerapkannya pada langkah ini. Jangan memakai angka soal ini.",
    3: "Tingkat bantuan 3 (langkah ini SUDAH BENAR): boleh membahas penyelesaian langkah ini "
    "secara lengkap. Ajak siswa menjelaskan ulang caranya dan melihat di mana cara ini "
    "dipakai lagi (refleksi dan transendensi).",
}


def tingkat_bantuan(sudah_benar: bool, percobaan_salah: int, tingkat_petunjuk: int) -> int:
    """Tingkat bantuan 0–3 dari status siswa pada langkah ini."""
    if sudah_benar:
        return 3
    if percobaan_salah >= 2 or tingkat_petunjuk >= 2:
        return 2
    if percobaan_salah == 1:
        return 1
    return 0


def instruksi_mediasi(tingkat: int, tahap: str | None, fase: str | None) -> str:
    baris = ["MEDIASI UNTUK LANGKAH INI (dari sistem):"]
    if tahap in FOKUS_TAHAP:
        baris.append(FOKUS_TAHAP[tahap])
    if fase in FOKUS_FASE and tingkat < 3:
        baris.append(FOKUS_FASE[fase])
    baris.append(BANTUAN[tingkat])
    return "\n".join(baris)
