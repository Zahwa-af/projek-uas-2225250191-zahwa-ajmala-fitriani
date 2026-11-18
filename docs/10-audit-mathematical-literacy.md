# 10 — Audit Fitur Mathematical Literacy

> **Tanggal:** 18 November 2026 · **Status:** hasil pemeriksaan. **Tidak ada skor, soal, rubrik, atau kode yang diubah.**
> **Yang diperiksa:** isi `backend/data/soal/misi.json` (bank soal yang dipakai aplikasi), aturan skor di `backend/segitiga/penilai.py`, dan alur di `frontend/js/halaman/misi.js`. Semuanya dibandingkan dengan kisi-kisi soal dari peneliti (isinya tercatat di [04-game-dan-soal.md](04-game-dan-soal.md)).
> **Penanda:** ✅ sesuai · ⚠️ perlu keputusan peneliti/dosen · ❌ masalah yang sebaiknya diperbaiki

---

## 1. Ringkasan temuan

| No | Temuan | Tingkat |
|---|---|---|
| 1 | Keempat misi sudah sesuai urutan dan indikator kisi-kisi. Semua **kunci jawaban angka cocok** dengan kisi-kisi. Skor maksimum tiap misi 6. | ✅ |
| 2 | **Soal pilihan dengan 3 opsi selalu bisa dijawab benar dengan coba-coba dan tetap mendapat skor penuh**, karena batas percobaannya 3 kali. Ini terjadi di 4 langkah (Misi 1 langkah 3 dan 4, Misi 4 langkah 5 dan 6). | ❌ |
| 3 | **Indikator Reasoning (Misi 1) dan Interpreting (Misi 4) sebagian besar diukur dengan pilihan ganda.** Kisi-kisi meminta siswa *menjelaskan* alasan, bukan memilih alasan. | ⚠️ |
| 4 | **Ada tiga kalimat soal yang berbeda dari kisi-kisi.** Paling penting: Misi 4 "sudah **cukup**" diubah menjadi "sudah **pas**". | ⚠️ |
| 5 | Di 8 langkah, petunjuk **tingkat 2 sudah praktis memberi jawaban**, padahal tingkat 2 tidak mengurangi skor. | ⚠️ |
| 6 | Petunjuk 3 tingkat tersedia di semua langkah, tetapi **isinya sama untuk semua siswa**. Yang menyesuaikan dengan kesalahan siswa baru umpan balik diagnosis. | ⚠️ (celah ini bisa diisi chatbot) |
| 7 | Langkah-langkah misi **memandu siswa tahap demi tahap**. Akibatnya skor misi mengukur kemampuan **dengan bantuan**, bukan kemampuan mandiri seperti pada tes kisi-kisi. | ⚠️ (desain penelitian) |

---

## 2. Kesesuaian misi dengan indikator Mathematical Literacy

| Misi | Indikator (kisi-kisi) | Konteks | Kesesuaian | Catatan |
|---|---|---|---|---|
| 1 Bendera Kelas | Mathematical Reasoning | Membandingkan dua desain | ✅ urutan tahap · ⚠️ cara mengukur | 3,5 dari 6 poin berasal dari soal pilihan ganda. Alasan matematis (tahap 5) dipilih dari 4 opsi, padahal kisi-kisi meminta "**Jelaskan** alasan matematis Anda". |
| 2 Kanopi Sekolah | Formulating Situations Mathematically | Luas kain dan biaya | ✅ urutan tahap · ⚠️ cara mengukur | Kisi-kisi meminta "**Buatlah model matematika**". Di aplikasi, model dipilih dari 4 opsi rumus (tahap 3), dan model biaya total tidak diminta. Angka di langkah Diketahui sudah disiapkan, tanpa angka pengecoh. |
| 3 Taman Sekolah | Employing Concepts, Facts, Procedures | Bagian bunga dan rumput | ✅ | Hampir seluruhnya isian angka dan rumus. Paling sesuai dengan indikatornya. |
| 4 Papan Informasi | Interpreting, Applying, Evaluating | Memeriksa hitungan teman | ✅ urutan tahap · ⚠️ cara mengukur | 5 dari 6 poin berasal dari pilihan ganda. Menafsirkan dan menilai hasil lebih banyak berupa *mengenali* pilihan yang benar daripada *menyusun* penilaian sendiri. |

Komposisi jenis langkah per misi:

| Misi | Pilah | Pilihan ganda | Rumus | Angka | Poin dari pilihan ganda |
|---|---|---|---|---|---|
| 1 | 1 | 4 | 0 | 2 | 3,5 / 6 |
| 2 | 1 | 2 | 1 | 2 | 2 / 6 |
| 3 | 1 | 0 | 2 | 3 | 0 / 6 |
| 4 | 0 | 5 | 0 | 1 | 5 / 6 |

---

## 3. Kesesuaian soal, kisi-kisi, dan rubrik

### 3.1 Kunci jawaban — ✅ semua cocok
1.200 cm² (A dan B) · 3 m², 12 m², Rp300.000 · 42 m², 14 m², 28 m² · 1,8 m². Semua sama dengan kisi-kisi dan sudah diuji otomatis (135 tes lulus).

### 3.2 Pembagian skor per tahap

| Misi | Rubrik kisi-kisi | Di aplikasi | Status |
|---|---|---|---|
| 1 | T1=1, T2=2, T3–T5=1 | T1 dipecah 1a (0,5) + 1b (0,5); T2 dipecah 2a (A) + 2b (B) | ⚠️ T1 dipecah 0,5 + 0,5 adalah keputusan penulis |
| 2 | T1–T6 = 1 | Sama, 6 langkah | ✅ |
| 3 | T1=1, T2=2, T3=2, T4=1 | T2 = 2a (substitusi) + 2b (hasil); T3 = 3a (model) + 3b (hasil) | ⚠️ Kisi-kisi tidak menjelaskan cara memberi skor 1 dari 2. Pembagian "model 1 + hasil 1" adalah asumsi penulis. |
| 4 | T1–T6 = 1 | Sama, 6 langkah | ✅ |

### 3.3 Kalimat soal yang berbeda dari kisi-kisi — ⚠️

| Misi | Kisi-kisi | Aplikasi | Dampak |
|---|---|---|---|
| 1 | "Desain mana yang sebaiknya dipilih? **Jelaskan alasan matematis anda.**" | Kalimat "Jelaskan…" dihilangkan dari cerita. Diganti langkah 5 berbentuk pilihan ganda. | Tuntutan menjelaskan turun menjadi memilih |
| 2 | "**Buatlah model matematika** untuk menentukan luas seluruh kain dan biaya yang diperlukan, kemudian selesaikan." | "Berapa luas seluruh kain dan berapa biayanya?" | Perintah membuat model hilang dari soal |
| 4 | "Seorang siswa… menyimpulkan bahwa kain seluas 3,6 m² **sudah cukup**…" | "**Dika** berkata kain 3,6 m² **sudah pas**…" | **Maknanya berubah.** Kain 3,6 m² memang *cukup* (malah berlebih). Kata "pas" membuat jawaban "tidak setuju" menjadi lebih jelas, tetapi mengubah soal asli. Nama "Dika" hanya perubahan gaya. |

Kesimpulan kisi-kisi Misi 2 tahap 6 ("Jadi, diperlukan 12 m² kain dengan biaya Rp300.000") hanya muncul sebagai penjelasan setelah benar. Siswa tidak diminta menuliskannya.

### 3.4 Aturan skor aplikasi dan validitasnya

Aturan sekarang ([penilai.py:184](../backend/segitiga/penilai.py#L184)): skor penuh jika benar **tanpa** membuka petunjuk tingkat 3. Setelah 3 kali salah, petunjuk tingkat 3 terbuka otomatis dan skor langkah menjadi 0 ([penilai.py:12-13](../backend/segitiga/penilai.py#L12-L13)).

| Jenis langkah | Akibat aturan di atas | Status |
|---|---|---|
| **Pilihan ganda 3 opsi** (M1-3, M1-4, M4-5, M4-6) | Paling banyak 2 kali salah sebelum benar, jadi **coba-coba selalu mendapat skor penuh** | ❌ |
| Pilihan ganda 4 opsi | Peluang skor penuh dengan menebak acak: 75% | ❌ |
| Pilah | Umpan balik menyebut item yang salah, sehingga percobaan kedua hampir pasti benar | ⚠️ |
| Rumus | Umpan balik menyebut kotak yang salah | ⚠️ |
| Angka | Diagnosis menunjuk penyebab, tetapi tidak memberi angka | ✅ |

Hal ini bertentangan dengan RMT yang menekankan **menghindari coba-coba** ([07-analisis-rmt.md](07-analisis-rmt.md), Dok. hal. 10).
**Kabar baiknya:** setiap percobaan sudah tercatat di tabel `jawaban_langkah` (kolom `percobaan_ke`), jadi **skor yang lebih ketat bisa dihitung ulang** tanpa mengubah aplikasi. Misalnya: skor penuh hanya jika benar pada percobaan pertama.

### 3.5 Kategori skor — ⚠️
Kategori Sangat baik / Baik / Cukup / Perlu bimbingan ([penilai.py:216](../backend/segitiga/penilai.py#L216)) **dibuat penulis**, tidak berasal dari kisi-kisi. Lihat dokumen 09.

---

## 4. Audit petunjuk bertahap

**Yang sudah baik ✅**
- Setiap langkah punya tepat 3 tingkat petunjuk, dan ini dicek otomatis saat bank soal dimuat.
- Polanya konsisten: tingkat 1 mengarahkan perhatian, tingkat 2 memberi rumus atau arah, tingkat 3 memberi cara lengkap. Pola ini kira-kira sejalan dengan fase Input → Elaborasi → Output (RMT).
- Umpan balik saat salah sudah menyesuaikan dengan kesalahan. Ada 28 umpan balik khusus per opsi, 16 pola kesalahan angka atau isian, dan diagnosis umum (lupa ½, menjumlah alih-alih mengalikan, salah satuan, dan lainnya).

**Masalah ⚠️**

| Masalah | Langkah yang terdampak |
|---|---|
| **Petunjuk tingkat 2 praktis memberi jawaban** tanpa mengurangi skor | M1-3 (menyebut kedua luas), M1-4 ("luasnya sama"), M2-2 (mengutip pertanyaan), M3-1 (menyebut alas), M3-2a (menyebut 12 dan 7), M4-1 (menyebut perkaliannya), M4-4 ("1,8 × 2"), M4-5 ("…memang benar. Tetapi rumus…") |
| **Petunjuk tidak menyesuaikan dengan kesalahan siswa.** Siswa yang lupa ½ dan siswa yang salah memilih tinggi menerima petunjuk yang sama. | Semua langkah |
| Petunjuk ditulis penulis dan **belum divalidasi ahli** | Semua langkah |
| Tidak ada petunjuk untuk *proses berpikir* (misalnya "bagaimana kamu tahu itu tingginya?"). Yang ada hanya petunjuk menuju jawaban. | Semua langkah |

---

## 5. Bagian aplikasi yang perlu diintegrasikan dengan chatbot DeepSeek

| Bagian | Lokasi | Rencana integrasi (setelah disetujui) |
|---|---|---|
| **Layar langkah misi** | [misi.js:161](../frontend/js/halaman/misi.js#L161) `layarLangkah` | Tambah tombol dan panel "Tanya Pembimbing" di dekat petunjuk ([misi.js:174](../frontend/js/halaman/misi.js#L174)). Panel otomatis membawa konteks: misi, langkah, instruksi, kesalahan terakhir. |
| Pemeriksaan jawaban | [misi.js:242](../frontend/js/halaman/misi.js#L242) dan [routes_periksa.py:59](../backend/api/routes_periksa.py#L59) | Kode diagnosis terakhir dikirim ke chatbot sebagai **fakta dari Python**. Chatbot tidak menilai sendiri. |
| Petunjuk bawaan | [routes_periksa.py:133](../backend/api/routes_periksa.py#L133) | Tetap ada. Chatbot menjadi jalur bantuan **tambahan** yang tidak mengubah skor. Batas antara keduanya perlu diputuskan (lihat 7.2). |
| Refleksi "Jelaskan ke temanmu" | [misi.js:339](../frontend/js/halaman/misi.js#L339) dan [routes_periksa.py:217](../backend/api/routes_periksa.py#L217) | Kandidat untuk umpan balik chatbot atas penjelasan siswa (tahap Refleksi RMT, germane load) |
| Status langkah dan sesi | [umum.py:54-61](../backend/api/umum.py#L54-L61) `ambil_main`, `status_langkah` | Dipakai ulang untuk memastikan chatbot hanya melayani misi yang sedang aktif |
| Kode anonim | Tabel `sesi` ([db.py:9](../backend/db.py#L9)) | `sesi.id` (acak) dipakai sebagai kode anonim. `nama_panggilan` **tidak** dikirim ke DeepSeek. |
| Database | [db.py](../backend/db.py) | Tabel baru untuk percakapan: pesan, tingkat bantuan, fase kognitif, kode kesalahan |
| Rekap guru | [routes_progres.py:64](../backend/api/routes_progres.py#L64) | Tambah kolom pemakaian AI: jumlah pertanyaan dan tingkat bantuan |
| Vercel | [index.py](../index.py), [vercel.json](../vercel.json) | Atur batas waktu fungsi dan pasang `DEEPSEEK_API_KEY` di Environment Variables |
| **Tidak diintegrasikan** | `web-statis/`, halaman Belajar dan Latihan | Sesuai keputusan. Belajar dan Latihan bisa menjadi tahap berikutnya. |

---

## 6. Daftar fitur

### 6.1 Sudah siap ✅
- 4 misi sesuai urutan indikator dan tahapan kisi-kisi; kunci jawaban benar
- Skor rubrik per tahap dihitung di server; kunci jawaban tidak dikirim ke browser
- Diagnosis kesalahan dengan pesan yang menunjuk penyebab
- Petunjuk 3 tingkat di semua langkah
- **Pencatatan data sudah lengkap untuk penelitian:** setiap percobaan, kode kesalahan, tingkat petunjuk yang dibuka, dan refleksi
- Ringkasan langkah dan "Jelaskan ke temanmu"
- Rekap guru per kelas

### 6.2 Perlu perbaikan atau keputusan (tidak akan diubah tanpa persetujuan)

| Prioritas | Item | Pilihan perbaikan |
|---|---|---|
| **Tinggi** | ❌ Coba-coba mendapat skor penuh pada soal pilihan ganda | (a) skor penuh hanya pada percobaan pertama, sebagian pada percobaan kedua · (b) tambah opsi · (c) biarkan di aplikasi, tetapi hitung ulang skor ketat dari log untuk analisis |
| **Tinggi** | ⚠️ Kalimat Misi 4 "pas" vs kisi-kisi "cukup" | Kembalikan ke kalimat kisi-kisi dan sesuaikan opsi tahap 5–6, **atau** kisi-kisi direvisi peneliti |
| **Tinggi** | ⚠️ Reasoning dan Interpreting diukur dengan pilihan ganda | Tambah isian penjelasan bebas (dinilai manual oleh peneliti, bisa dibantu chatbot untuk umpan balik saja, bukan untuk menilai) |
| Sedang | ⚠️ Perintah "Buatlah model matematika" (Misi 2) hilang | Kembalikan ke kalimat soal dan pertimbangkan langkah menyusun model biaya |
| Sedang | ⚠️ Petunjuk tingkat 2 memberi jawaban di 8 langkah | Tulis ulang petunjuknya, atau jadikan tingkat 2 sebagai pengurang skor |
| Sedang | ⚠️ Pembagian skor 0,5 + 0,5 dan "model 1 + hasil 1" | Konfirmasi dosen |
| Sedang | ⚠️ Kategori skor buatan penulis | Ganti dengan pedoman resmi |
| Sedang | ⚠️ Petunjuk tidak menyesuaikan dengan kesalahan siswa | Diisi oleh chatbot, berdasarkan kode diagnosis |
| Desain penelitian | ⚠️ Misi bersifat terbimbing, jadi tidak mengukur kemampuan mandiri | Gunakan **pretest dan posttest tanpa bantuan** (kisi-kisi asli) sebagai alat ukur Mathematical Literacy. Misi dipakai sebagai media belajar. |

---

## 7. Keputusan yang diperlukan dari peneliti

1. **Soal pilihan ganda dan coba-coba:** pilih (a), (b), atau (c) di tabel 6.2.
2. **Hubungan chatbot dengan petunjuk bawaan:** apakah tombol chatbot muncul sejak awal, atau setelah siswa salah sekali, atau setelah membuka petunjuk tingkat 1?
3. **Kalimat soal Misi 1, 2, dan 4:** kembali ke kisi-kisi asli, atau kisi-kisi yang direvisi?
4. **Alat ukur Mathematical Literacy:** skor misi di aplikasi, atau pretest dan posttest terpisah? Ini memengaruhi desain penelitian.
