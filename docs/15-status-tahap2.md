# 15 — Status Tahap 2: RMT, Cognitive Load, dan Chatbot Misi

> **Tanggal:** 19 November 2026 · **Status kode:** belum di-commit.
>
> Dokumen ini hanya mencatat hasil pengujian **teknis** (otomatis) yang benar-benar dijalankan.
> - **Belum ada data penelitian dari siswa.** Semua data pengujian adalah data simulasi di database sementara.
> - **Chatbot belum diuji dengan model AI sungguhan** pada tahap ini. Semua tes chatbot memakai klien tiruan.

## 1. Fitur yang selesai

| Tahap | Isi | Dokumen |
|---|---|---|
| 1 | Label tahap RMT dan fase kesalahan (Input/Elaborasi/Output) di data | [12](12-audit-rmt.md) |
| 2A | Konten RMT 4 misi × 6 aktivitas (tanpa skor), pemeriksa di Python, tabel `aktivitas_rmt` | [13](13-rencana-implementasi-tahap2.md) |
| 2B | Layar RMT di misi: tujuan & makna, Tebak dulu, Susun rencana, Tata informasi, Cek hasil, Di mana lagi?, refleksi dengan kalimat pembuka. Semua bisa dilewati. | [13](13-rencana-implementasi-tahap2.md) |
| 2C | Cognitive Load: Soal Cerita Bertahap (fading 4 tingkat), remedial adaptif, layar Bandingkan keliling–luas, panel Pembimbing tertutup bawaan | [14](14-cognitive-load-tahap2c.md) |
| 2F | Chatbot misi dengan mediasi RMT (lihat bagian 2) | [asisten/mediasi.py](../backend/asisten/mediasi.py) |
| Audit | Perbaikan hasil audit (bagian 3) | — |

## 2. Chatbot misi (Tahap 2F)

**Konfigurasi:**
- Provider: OpenRouter (format OpenAI), model diatur di `.env`.
- API key hanya dibaca backend dan tidak pernah dikirim ke browser.
- Mode efektif server saat `.env` dimuat: `deepseek` (bukan tiruan). Tes otomatis memaksa mode `mati` atau tiruan, sehingga tidak ada biaya.

**Setiap pertanyaan siswa di panel misi mendapat instruksi tambahan dari server:**
- **Prinsip MLE:** intensionalitas, makna, dan resiprositas. Batas beban kognitif: satu ide per balasan, sekitar 120 kata, dan merujuk gambar (alas biru, tinggi oranye).
- **Fokus tahap RMT langkah:** analisis tugas, representasi, manipulasi, atau validasi.
- **Fase kesalahan terakhir:** Input, Elaborasi, atau Output.
- **Tingkat bantuan 0–3**, ditentukan server (dicatat di `percakapan_asisten.tingkat_bantuan`):

| Tingkat | Kondisi | Bantuan |
|---|---|---|
| 0 | Belum salah | Penjelasan konsep langsung + pertanyaan pemantik |
| 1 | Salah 1 kali | Tunjuk bagian yang perlu diperiksa + satu pertanyaan pemandu |
| 2 | Salah ≥ 2 kali atau sudah membuka 2 petunjuk | Contoh serupa dengan angka berbeda, diselesaikan lengkap |
| 3 | Langkah sudah benar | Boleh membahas penyelesaian lengkap + refleksi dan transendensi |

**Yang tidak berubah:**
- Chatbot misi **tetap tidak menyebut jawaban akhir** langkah yang belum benar, walaupun petunjuk ke-3 sudah dibuka ([07](07-analisis-rmt.md) §7.2). Penyaring `pengaman.py` tidak diubah.
- Chatbot beranda (Tanya Pembimbing) tidak diubah.

⚠️ Kerangka tahap dan fase masih **usulan peneliti**, belum dikonfirmasi dosen ([07](07-analisis-rmt.md) Q1).

## 3. Perbaikan hasil audit

| Temuan | Perbaikan |
|---|---|
| T1 — `sesi_id` siswa lain tertinggal di HP bersama | Tingkat latihan disimpan hanya untuk siswa aktif. "Ganti nama" menghapusnya. |
| T2 — refleksi tersimpan tanpa disamarkan | `/api/refleksi` kini menyamarkan nama panggilan, email, dan nomor HP |
| S1 — tidak ada rate limit endpoint baru | Batas per IP untuk POST `/api/rmt/` dan `/api/latihan/`, ditambah maksimal 50 percobaan per aktivitas per main misi |
| S3 — remedial menghitung semua riwayat | Hasilku memakai percobaan terakhir tiap misi; layar hasil misi memakai main misi itu |
| S4 — `web-statis` rusak untuk fitur baru | Fungsi pengganti: RMT dilewati, remedial disembunyikan, Latihan Bertahap memberi pesan jelas |
| Rendah | Tombol Kirim refleksi tidak bisa terkirim ganda. Layar Bandingkan memakai warna alas biru dan tinggi oranye. Dokumentasi diperbarui. |

**Belum diperbaiki karena butuh tindakan Anda:**
- **T3:** PIN guru bawaan "1234" saat `SEGIPINTAR_PIN_GURU` kosong.
- **S6:** `SEGIPINTAR_RAHASIA_ANONIM` kosong.

Keduanya diisi di `.env`, lihat bagian 6.

## 4. Hasil pengujian otomatis (19 November 2026)

| Pengujian | Hasil | Catatan |
|---|---|---|
| `ruff check backend` | Lulus | |
| `black --check backend wsgi.py index.py` | Lulus | |
| `pytest backend/tests` | **346 lulus** | Termasuk alur lengkap misi 1–4 lewat API: semua 6 aktivitas RMT + langkah berskor, skor 6/6 setiap misi, total 24 |
| E2E RMT (`uji_rmt_misi.mjs`) | 29/29 | HP 360 px dan laptop 1280 px |
| E2E Cognitive Load (`uji_cognitive_load.mjs`) | 34/34 | HP, laptop, dan mode gelap |
| E2E misi 1–4 (`uji_misi_1_4.mjs`) | 59/59 | Semua layar RMT misi 1–4 (misi 1 & 3 di 360 px, misi 2 & 4 di 1280 px), remedial, HP bersama |
| Kesetaraan `web-statis` | Lulus | Penilaian JavaScript identik dengan Python |

Semua E2E tanpa galat JavaScript dan tanpa scroll horizontal.

**Cara menjalankan E2E:**
1. Jalankan server uji dengan database sementara:
   ```
   PORT=5077 SEGIPINTAR_DB_PATH=<file sementara> SEGIPINTAR_ASISTEN=tiruan python backend/app.py
   ```
2. Jalankan skripnya:
   ```
   node backend/tests/e2e/<skrip>.mjs <folder sementara>
   ```

`uji_misi_1_4.mjs` membutuhkan `SEGIPINTAR_MISI_BEBAS=1`.

## 5. Yang perlu diuji langsung oleh mahasiswa
1. **Chatbot dengan model sungguhan.** Memakai kuota dan API key Anda.
   ```
   .venv\Scripts\python backend\tests\uji_langsung_pembimbing.py E F "Soal cerita"
   ```
   Lalu coba panel misi: salah 1 kali, salah 2 kali, dan setelah benar. Perhatikan apakah bantuan bertambah bertahap dan jawaban akhir tidak disebut.
2. **HP sungguhan** lewat Wi-Fi yang sama: misi 1–4, Latihan Bertahap, Hasilku, dan mode gelap.
3. **HP bersama:** siswa A main, tekan "Ganti nama", lalu siswa B main.
4. **Halaman guru** dengan PIN baru.
5. **Kalimat konten:** periksa kalimat aktivitas RMT (`rmt_misi.json`), soal latihan bertahap, dan instruksi mediasi chatbot sebelum dipakai siswa.

## 6. Belum selesai atau di luar Tahap 2
- Konfirmasi dosen: tahapan RMT, kategori skor, ambang remedial dan fading.
- Instrumen pretest dan posttest, angket beban kognitif final, persetujuan etika, validasi ahli. Ini dokumen penelitian, bukan kode.
- Ekspor data RMT dan latihan untuk analisis. Saat ini data RMT hanya ada di SQLite, dan latihan bertahap tidak dicatat.
- Tombol "Cek langkahku" (F-10), generator variasi 4 misi (F-13), tabel "Diketahui" dan soal variasi di layar transendensi.
- Versi `web-statis` belum memiliki fitur Tahap 2.
