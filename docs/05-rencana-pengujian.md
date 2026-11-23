# 05 — Rencana Pengujian

Pengujian terdiri dari **(A) pengujian teknis** (apakah aplikasi bekerja benar) dan **(B) uji coba dengan siswa** (apakah aplikasi benar-benar mengurangi beban kognitif dan membantu literasi matematika).

## A. Pengujian teknis

### A1. Unit test Python (pytest) — wajib lulus sebelum setiap rilis

| File | Yang diuji | Contoh kasus |
|---|---|---|
| `test_parser_angka.py` | Format angka Indonesia | `"1,8"→1.8`, `"1.200"→1200`, `"Rp300.000"→300000`, `"1/3"→0.333…`, `"abc"→None`, `" 42 "→42`, `"1.5"→1.5` (titik tanpa 3 digit = desimal) |
| `test_rumus.py` | Luas, keliling, jenis segitiga | `luas(12,7)==42`; (3,4,5) = siku-siku; (5,5,5) = sama sisi |
| `test_penilai.py` | Periksa langkah & skor rubrik | Semua kunci 4 misi kisi-kisi; skor 0 saat petunjuk 3 dibuka; skor 6 bila semua benar |
| `test_diagnosis.py` | Pola kesalahan | 2400 di Misi 1 → `LUPA_SETENGAH`; 3,6 di Misi 4 → `LUPA_SETENGAH`; 28 sebagai bunga → `TERTUKAR_BAGIAN`; Rp75.000 → `LUPA_JUMLAH_BENDA` |
| `test_generator.py` | Variasi soal | 1.000 variasi acak: semua hasil bilangan bulat/desimal 1 angka, kunci konsisten dengan rumus |
| `test_api.py` | Endpoint Flask | `GET /api/misi/1` **tidak** mengandung kata `kunci`/`petunjuk`; `/api/periksa` mengembalikan format yang benar |

### A2. Uji tampilan & perangkat (manual, checklist)

| Perangkat / kondisi | Cek |
|---|---|
| HP Android 360×800, Chrome | Semua tombol ≥ 44 px, tidak ada scroll horizontal, gambar terbaca |
| HP layar kecil 320 px | Teks tidak terpotong |
| Laptop 1280 px, Chrome & Firefox | Tata letak dua kolom |
| Mode gelap sistem | Kontras teks & warna alas/tinggi tetap jelas |
| `prefers-reduced-motion` aktif | Tidak ada animasi |
| HP & laptop di Wi-Fi yang sama, tanpa internet | Aplikasi bisa diakses lewat IP laptop |
| Mode privat browser | Aplikasi tetap jalan walau `localStorage` gagal |
| Drag-and-drop dengan jari | Pilah Informasi bisa dipakai di layar sentuh |

### A2b. Uji tampilan otomatis (Edge headless, Tahap 2)

Skrip ada di `backend/tests/e2e/` dan dijalankan manual pada server uji dengan database sementara. Hasil terakhir dicatat di [15-status-tahap2.md](15-status-tahap2.md).

| Skrip | Isi |
|---|---|
| `uji_rmt_misi.mjs` | Layar RMT misi 1–2, lewati, skor tetap, konten RMT gagal dimuat |
| `uji_cognitive_load.mjs` | Fading naik/tetap/turun, petunjuk, penjelasan diri, remedial, panel Pembimbing, mode gelap |
| `uji_misi_1_4.mjs` | Semua layar RMT misi 1–4 di HP dan laptop, remedial, HP bersama (butuh `SEGIPINTAR_MISI_BEBAS=1`) |

### A3. Uji kepatuhan desain (sebelum uji coba siswa)
Periksa setiap layar terhadap 9 aturan desain di [CLAUDE.md](../CLAUDE.md). Satu layar = satu baris checklist.

## B. Uji coba dengan siswa

Diturunkan dari kolom **"Cara menguji fitur"** pada matriks analisis laporan wawancara.

### B1. Desain uji coba

- **Peserta:** disarankan 5–10 siswa kelas VIII (termasuk S01 bila memungkinkan).
- **Alur (±60 menit):**
  1. Pretest singkat (2 soal mirip kisi-kisi, kertas) — 10 menit
  2. Belajar + Latihan di aplikasi — 20 menit
  3. Misi 1–4 di aplikasi — 20 menit
  4. Angket beban kognitif + wawancara singkat — 10 menit
- **Data otomatis** dari database: skor per tahapan, jumlah percobaan, tingkat petunjuk, kode diagnosis.

### B2. Pengujian per fitur

| Fitur | Cara menguji (dari laporan wawancara) | Indikator berhasil |
|---|---|---|
| F-01/F-02 Segitiga interaktif & Tunjuk Tingginya | Minta siswa menunjukkan alas & tinggi pada beberapa bentuk segitiga | ≥ 80% benar, termasuk segitiga tumpul |
| F-03 Panduan langkah | Amati apakah siswa dapat mengikuti urutan penyelesaian secara mandiri | Siswa menuliskan diketahui → ditanyakan → rumus → hitung pada posttest kertas |
| F-04 Pengingat operasi hitung | Uji latihan dan amati kesalahan hitung | Penurunan kode `SALAH_HITUNG` dari misi awal ke misi akhir |
| F-05 Pilah Informasi | Minta siswa menjelaskan arti angka dan informasi pada soal | Siswa dapat menyebutkan kegunaan setiap angka |
| F-06/F-07 Penyajian & tempo | Amati pemahaman setelah memakai gambar & kontrol tempo | Siswa menyatakan tidak terburu-buru; tombol Ulangi dipakai |
| F-08 Tampilan sederhana | Minta siswa menilai kejelasan tampilan; amati fokus | Skor angket "tampilan mengganggu" rendah |
| F-09 Contoh bertahap | Bandingkan kemampuan menjelaskan langkah sebelum & sesudah melihat contoh | Penjelasan sesudah lebih lengkap |
| F-10 Cek ulang | Amati apakah siswa memeriksa rumus & hasil secara mandiri | Tombol "Cek langkahku" dipakai |
| F-11/F-12 Petunjuk & jelaskan ke teman | Catat tingkat bantuan dan kemampuan menjelaskan kembali | Rata-rata tingkat petunjuk turun dari Misi 1 ke Misi 4 |
| F-13 Variasi soal | Beri soal dengan cerita berbeda; amati pemilihan strategi | Skor variasi ≈ skor misi asli |
| F-14 Diagnosis kesalahan | Wawancarai siswa tentang manfaat umpan balik | Siswa berkata umpan balik membantu menemukan kesalahan |
| F-15 Misi | Skor rubrik per indikator | Rata-rata per indikator dibandingkan dengan pretest |

### B3. Angket beban kognitif (skala 1–9, adaptasi Paas / Leppink)

Diisi setelah sesi. Kalimat disederhanakan untuk siswa SMP.

| No | Pernyataan | Jenis beban |
|---|---|---|
| 1 | Materi segitiga di aplikasi ini terasa sulit. | IL |
| 2 | Soal-soal di aplikasi ini rumit. | IL |
| 3 | Tampilan aplikasi membuat saya bingung. | EL |
| 4 | Penjelasan di aplikasi tidak jelas. | EL |
| 5 | Warna atau gerakan di aplikasi mengganggu saya. | EL |
| 6 | Aplikasi ini membantu saya lebih paham cara mencari luas segitiga. | GL |
| 7 | Saya jadi lebih paham cara menyelesaikan soal cerita segitiga. | GL |
| 8 | Seberapa besar usaha yang kamu keluarkan untuk memahami materi? (1 = sangat kecil, 9 = sangat besar) | Usaha mental |

**Target:** skor EL rendah (≤ 3), skor GL tinggi (≥ 7).

### B4. Pertanyaan wawancara pasca-uji coba
1. Bagian mana yang paling membantu kamu? Mengapa?
2. Apakah ada tampilan yang membuatmu bingung atau tidak fokus?
3. Apakah petunjuknya membantu? Petunjuk tingkat berapa yang paling sering kamu buka?
4. Ketika jawabanmu salah, apakah kamu tahu bagian mana yang salah?
5. Coba jelaskan cara mengerjakan Misi 2 kepada saya seperti kepada temanmu.
