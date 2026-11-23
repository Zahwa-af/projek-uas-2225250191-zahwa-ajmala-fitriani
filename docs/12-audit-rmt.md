# 12 — Audit Penerapan RMT dan Cognitive Load di SegiPintar

> **Tanggal:** 18 November 2026 · **Status:** audit, **belum ada perubahan kode**.
> **Rujukan:** ringkasan *Rigorous Mathematical Thinking: Conceptual Formation in the Mathematics Classroom* (Kinard & Kozulin), 15 halaman. Nomor halaman mengikuti PDF yang dianalisis di [07-analisis-rmt.md](07-analisis-rmt.md).
> **Catatan sumber:** file `referensi_rmt/Rigorous Mathematical Thinking.pdf` di proyek berupa hasil pindai (tanpa teks) dan tidak bisa dibaca otomatis di laptop ini. Judul dan jumlah halamannya (15) sama dengan PDF yang dulu dibaca lengkap dari lampiran chat. Jika isinya berbeda, audit ini perlu diperbarui.
> **Cognitive Load Theory** tidak dibahas di PDF RMT. Rujukannya: Sweller (1988); Sweller, van Merriënboer & Paas (1998).
> **Penanda:** ✅ sudah sesuai · 🟡 sebagian · ❌ belum ada

---

## 1. Peta fitur yang diaudit

| Bagian | Fitur yang ada |
|---|---|
| Belajar | 5 topik (jenis segitiga, alas & tinggi + segitiga interaktif, keliling, luas dari persegi panjang, langkah soal cerita), satu konsep per layar, Kembali/Ulangi/Lanjut |
| Latihan | Tunjuk Tingginya (lancip/siku/tumpul), Pilah Informasi (dengan angka pengecoh) |
| Misi | 4 misi kisi-kisi Mathematical Literacy; cerita per kalimat → langkah per layar → ringkasan → "Jelaskan ke temanmu" → skor rubrik, ⭐, lencana; petunjuk 3 tingkat; diagnosis kesalahan (Python); "Ingat lagi" saat salah hitung |
| Pembimbing AI | **Misi:** panel di setiap langkah, tidak memberi jawaban langkah yang dinilai, dijaga pengaman server. **Beranda (Tanya Pembimbing):** menjawab langsung sampai hasil akhir (keputusan peneliti 18 Nov) |
| Hasil & guru | Hasilku (skor, kategori, lencana), rekap kelas ber-PIN |
| Data penelitian | Setiap percobaan, kode kesalahan, tingkat petunjuk, refleksi, percakapan AI (kode anonim). Kolom `tahap_rmt`, `fase_kognitif`, `tingkat_bantuan` **sudah ada tetapi selalu kosong** |

---

## 2. Audit komponen RMT

### A1. Fungsi kognitif berorientasi matematika — Input → Elaborasi → Output [Dok. hal. 9–11]

| Fungsi (dokumen) | Bukti di aplikasi | Status |
|---|---|---|
| **Input:** persepsi jelas dan terorganisasi, akurasi mengumpulkan data | Pilah Informasi; langkah "Diketahui" (pilah) di Misi 1–3; Tunjuk Tingginya (persepsi tinggi pada segitiga tumpul) | ✅ |
| **Elaborasi:** hubungan bagian-keseluruhan, sebab-akibat, penalaran | Asal rumus ½ (persegi panjang dibagi dua); Misi 3 (⅓ bagian, sisa); Misi 1 (membandingkan dua luas) | 🟡 Ada, tetapi siswa umumnya **memilih**, bukan menyusun penalaran |
| **Output:** komunikasi jelas, ketepatan simbol, **menghindari coba-coba** | Cek satuan (cm vs cm²); "Jelaskan ke temanmu" | 🟡 / ❌ Soal pilihan 3 opsi bisa ditebak dan **tetap mendapat skor penuh** ([10-audit](10-audit-mathematical-literacy.md) §3.4). Ini bertentangan langsung dengan "menghindari trial-and-error" [hal. 10] |
| **Diagnosis fase yang bermasalah** [hal. 12] | Kode diagnosis Python sudah ada, tetapi **tidak dipetakan** ke Input/Elaborasi/Output; kolom `fase_kognitif` kosong | ❌ |

### A2. Alat psikologis spesifik matematika [Dok. hal. 3, 7, 11]

| Alat (dokumen) | Bukti | Status |
|---|---|---|
| Tanda dan simbol | ½, ×, cm², s₁ konsisten; chatbot memakai simbol rapi | ✅ |
| Organizer grafis/simbolik (tabel, garis bilangan, koordinat) | Segitiga SVG dengan kotak-kotak (mirip koordinat) yang bisa digeser; arsir ⅓ di Misi 3 | 🟡 **Tabel** sebagai alat berpikir (misalnya tabel Diketahui/Ditanyakan, tabel perbandingan Desain A/B) belum ada |
| Rumus dan persamaan | Isian rumus `½ × ☐ × ☐`; pilih model | 🟡 Rumus disodorkan sebagai pilihan; siswa belum **menyusun** sendiri |
| Bahasa matematika | Istilah konsisten (alas, tinggi); refleksi tertulis | 🟡 Penjelasan tertulis siswa opsional dan tidak mendapat umpan balik |

### A3. Mediated Learning Experience (MLE) [Dok. hal. 9, 11]

| Kriteria | Bukti | Status |
|---|---|---|
| **Intensionalitas** (mengarahkan perhatian ke tujuan) | Judul tahap per langkah ("Diketahui", "Hitung"); instruksi satu kalimat | 🟡 Belum ada pernyataan **tujuan belajar** di awal misi atau materi |
| **Resiprositas** (siswa aktif merespons) | Periksa → umpan balik yang menunjuk kesalahan; petunjuk bertahap; chatbot misi bertanya balik | ✅ di misi · ⚠️ **Chatbot beranda** kini menjawab langsung (keputusan 18 Nov). Ini sengaja **tidak** memediasi, sehingga resiprositasnya rendah |
| **Makna** (alasan dan pentingnya) | Penjelasan asal ½; konteks nyata sekolah; penjelasan Misi 4 ("Dika menghitung luas persegi panjang") | 🟡 Tidak konsisten di semua langkah; tidak ada "mengapa ini penting" |
| **Transendensi** (melampaui soal ke prinsip umum) | Ringkasan langkah; refleksi | ❌ Belum ada langkah yang meminta siswa menerapkan cara yang sama di konteks lain. Generator variasi soal (F-13) belum dibuat |

### A4. Konsep sehari-hari → konsep ilmiah [Dok. hal. 8, 11–12]

| Bukti | Status |
|---|---|
| Konteks sehari-hari (bendera, kanopi, taman, papan) dibawa ke model matematika | ✅ |
| Belajar "Luas": dari persegi panjang (yang sudah dikenal) ke rumus segitiga | ✅ |
| **Menggali intuisi siswa dulu** (misalnya "Menurutmu, bendera mana yang butuh kain lebih banyak?") lalu membandingkannya dengan hasil perhitungan | ❌ Belum ada. Langsung masuk ke langkah formal |

### A5. Representasi → Manipulasi → Validasi [Dok. hal. 14]

| Tahap | Bukti | Status |
|---|---|---|
| Representasi | Pilah informasi, pilih model (M2-3), isian rumus (M2-4, M3-2a, M3-3a) | 🟡 Kebanyakan memilih representasi yang disediakan |
| Manipulasi | Isian angka dan rumus, diperiksa Python | ✅ |
| Validasi | Cek satuan otomatis; Misi 4 (menilai hitungan Dika) | 🟡 Siswa **tidak diminta memeriksa kewajaran hasilnya sendiri** (misalnya "apakah luas segitiga lebih kecil dari alas × tinggi?"). Fitur "Cek langkahku" (F-10) belum ada |

### A6. Analisis tugas → Perencanaan tindakan → Refleksi [Dok. hal. 8]

| Tahap | Bukti | Status |
|---|---|---|
| Analisis tugas | Langkah Diketahui/Ditanyakan; Belajar topik 5 | ✅ |
| **Perencanaan tindakan** | Urutan langkah **ditentukan aplikasi**; siswa tidak pernah menyusun rencana | ❌ |
| Refleksi | Ringkasan + "Jelaskan ke temanmu" (opsional, tanpa umpan balik, tidak dianalisis) | 🟡 |

### A7. Asesmen dinamis [Dok. hal. 8, 10]

| Format | Bukti | Status |
|---|---|---|
| *Cake* (petunjuk bertahap saat tes) | Petunjuk 3 tingkat + pencatatan tingkat bantuan per langkah | ✅ (datanya sudah bisa dipakai untuk "potensi belajar") |
| *Sandwich* (pre-test → intervensi → post-test) | Tidak ada pretest/posttest di aplikasi | ❌ |

---

## 3. Audit Cognitive Load

| Jenis | Sudah sesuai ✅ | Belum / risiko |
|---|---|---|
| **Intrinsic** | Segmentasi satu langkah per layar; urutan materi sederhana → kompleks; pengingat prasyarat "Ingat lagi" (IL03); misi berurutan | Tingkat kesulitan tidak menyesuaikan kemampuan siswa; belum ada jalur remedial otomatis berdasarkan kesalahan berulang |
| **Extraneous** | Palet warna terbatas; label menempel pada gambar; cerita per kalimat; tanpa timer atau animasi dekoratif; tampilan chat rapi | ⚠️ Panel chatbot di setiap layar langkah misi **menambah elemen layar** (risiko perhatian terbagi). ⚠️ Jawaban chatbot beranda bisa sampai ±200 kata |
| **Germane** | Contoh bertahap (Belajar topik 5); ringkasan; refleksi; petunjuk bertahap; diagnosis yang menjelaskan sebab | *Fading* (contoh → setengah → mandiri) belum lengkap; variasi soal untuk transfer belum ada; refleksi tanpa umpan balik |

---

## 4. Ringkasan hasil audit

### 4.1 Sudah sesuai
1. Fase **Input** terlatih lewat Pilah Informasi, Tunjuk Tingginya, dan langkah Diketahui/Ditanyakan.
2. **Analisis tugas** dan **manipulasi** sudah menjadi bagian setiap misi.
3. **Alat psikologis** visual dan simbol konsisten (segitiga SVG interaktif, simbol ½ × cm²).
4. **Asesmen dinamis format *cake*:** petunjuk 3 tingkat beserta pencatatan tingkat bantuan.
5. **Resiprositas** di misi: umpan balik diagnosis dan chatbot misi yang bertanya balik.
6. **Cognitive load:** segmentasi, pengurangan beban penyajian, contoh bertahap.

### 4.2 Belum sesuai (perlu diperbaiki)
1. **Coba-coba mendapat skor penuh** di soal pilihan ganda. Ini bertentangan dengan fungsi kognitif Output [hal. 10].
2. **Kolom data RMT** (`tahap_rmt`, `fase_kognitif`, `tingkat_bantuan`) selalu kosong; `TAHAPAN_RMT` di prompt kosong.
3. **Chatbot beranda menjawab langsung** (keputusan 18 Nov). Ini bertentangan dengan prinsip mediasi RMT (pertanyaan terpimpin, *mediated questioning* [hal. 12]) dan resiprositas MLE. Perlu keputusan apakah beranda dianggap "bantuan referensi" di luar intervensi RMT.
4. **Alasan dan penjelasan** di Misi 1 dan 4 diukur dengan pilihan ganda, belum dengan bahasa matematika siswa sendiri.

### 4.3 Perlu ditambahkan
1. **Tujuan dan makna** di awal setiap misi (Intensionalitas + Makna).
2. **Langkah Perencanaan:** siswa mengurutkan langkah penyelesaian sebelum menghitung.
3. **Langkah Validasi:** siswa memeriksa kewajaran hasil.
4. **Langkah Transendensi:** "Di mana lagi cara ini bisa dipakai?" dan variasi soal dengan konteks berbeda.
5. **Prediksi intuitif** (konsep sehari-hari) sebelum perhitungan formal.
6. **Organizer tabel** sebagai alat berpikir (Diketahui/Ditanyakan, perbandingan).
7. **Refleksi bermediasi:** umpan balik atas penjelasan siswa.
8. **Pretest dan posttest** (format *sandwich*).
9. **Pemetaan otomatis kesalahan → fase kognitif** di data penelitian dan rekap guru.

---

## 5. Rencana implementasi bertahap (menunggu persetujuan)

Prinsip: **soal, kunci, dan skor rubrik kisi-kisi tidak diubah tanpa persetujuan.** Tambahan RMT dibuat sebagai langkah **tanpa skor** (skor 0) atau sebagai lapisan data, sehingga skor Mathematical Literacy tetap sebanding.

| Tahap | Isi | Komponen teori | Mengubah skor? | Butuh keputusan dosen? |
|---|---|---|---|---|
| **1. Fondasi data RMT** | Metadata `tahap_rmt` per langkah misi (analisis tugas / representasi / manipulasi / validasi / refleksi); pemetaan kode kesalahan → fase Input/Elaborasi/Output; isi kolom data; tampilkan di rekap guru | A1, A5, A6 (diagnosis [hal. 12]) | Tidak | Ya: konfirmasi pemetaan (misalnya `SALAH_HITUNG` masuk Elaborasi atau Output) |
| **2. MLE di misi** | Layar pembuka "Tujuan misi ini" dan "Mengapa ini penting"; layar transendensi setelah ringkasan | Intensionalitas, Makna, Transendensi | Tidak | Tidak (isi teks perlu ditinjau) |
| **3. Siklus RMT di misi** | Langkah tanpa skor: **Perencanaan** (mengurutkan langkah) sebelum menghitung dan **Validasi** (cek kewajaran) setelah menghitung | A5, A6 | Tidak | Ya: setuju langkah tambahan |
| **4. Konsep sehari-hari → ilmiah** | Layar "Tebak dulu" (prediksi intuitif) di awal misi dan materi, lalu dibandingkan dengan hasil | A4 | Tidak | Tidak |
| **5. Validitas skor** | Atasi coba-coba di pilihan ganda (opsi a/b/c dari audit 10) | A1 Output | **Ya** | **Ya** |
| **6. Chatbot sesuai RMT** | Isi `TAHAPAN_RMT` di chatbot misi (pertanyaan terpimpin per fase); putuskan peran chatbot beranda | MLE, A1–A6 | Tidak | **Ya** |
| **7. Germane load lanjutan** | *Fading* contoh bertahap; generator variasi soal (transfer); umpan balik refleksi | GL, Transendensi | Tidak | Tidak |
| **8. Asesmen *sandwich*** | Pretest & posttest tanpa bantuan | A7 | Terpisah dari misi | Ya: instrumen dari peneliti |

Setiap tahap: unit test, uji tampilan HP & laptop, dan pembaruan dokumen. Tahap 1 sebaiknya dikerjakan pertama karena tidak mengubah tampilan dan langsung menambah data penelitian.

---

## 6. Keputusan yang diperlukan
1. **Peran chatbot beranda:** tetap menjawab langsung (di luar intervensi RMT), atau diberi mode RMT?
2. **Pemetaan kesalahan → fase kognitif:** setuju dengan usulan di [07-analisis-rmt.md](07-analisis-rmt.md) §7.4?
3. **Langkah tanpa skor** (Perencanaan, Validasi, Transendensi) boleh ditambahkan ke misi?
4. **Penanganan coba-coba** di pilihan ganda (a/b/c)?
5. **File referensi:** apakah `referensi_rmt/Rigorous Mathematical Thinking.pdf` sama dengan PDF yang dulu dilampirkan di chat?
