# 13 — Rencana Implementasi Tahap 2: RMT dan Cognitive Load

> **Tanggal:** 18 November 2026 · **Status:** rancangan, **belum ada perubahan kode**.
> **Dasar:** ringkasan *Rigorous Mathematical Thinking* (Kinard & Kozulin) di [07-analisis-rmt.md](07-analisis-rmt.md) (nomor halaman = PDF), audit di [12-audit-rmt.md](12-audit-rmt.md), dan hasil Tahap 1 (commit `8b693f1`).
> **Catatan:** belum ada dokumen arahan dosen tertulis yang baru diterima. Bagian bertanda ❓ menunggu konfirmasi dosen.
> Cognitive Load Theory tidak ada di PDF RMT; rujukannya Sweller (1988) dan Sweller, van Merriënboer & Paas (1998).

---

## 0. Prinsip yang tidak boleh dilanggar

1. **Soal, kunci jawaban, dan skor rubrik tetap.** `backend/data/soal/misi.json`, `penilai.py`, dan `diagnosis.py` tidak diubah. Setiap tahap punya tes yang memastikan file ini tidak berubah.
2. **Aktivitas RMT baru = lapisan pendamping tanpa skor.** Isinya disimpan di file data terpisah (`rmt_misi.json`), dan jawabannya disimpan di tabel baru. Rincian skor di halaman hasil tidak berubah.
3. **Chatbot tetap memberi jawaban dan penjelasan lengkap** (bagian 4). Chatbot beranda tidak diubah perilakunya.
4. **Siswa yang mengatur tempo.** Setiap layar RMT baru punya tombol Lanjut dan **boleh dilewati**. Melewati layar dicatat sebagai data dan tidak memengaruhi skor.
5. **Aturan desain CLAUDE.md tetap berlaku:** satu hal per layar, teks pendek, warna dari token, animasi hanya untuk menjelaskan konsep.
6. **Setiap tahap bisa dibatalkan.** Satu tahap menjadi satu commit lokal. Tidak ada push atau deploy tanpa izin.

---

## 1. Kondisi saat ini (ringkas)

| Bagian | File utama | Yang sudah ada |
|---|---|---|
| Materi | `frontend/js/halaman/belajar.js` | 5 topik, satu konsep per layar, segitiga interaktif, contoh soal cerita bertahap |
| Latihan | `frontend/js/halaman/latihan.js`, `data/soal/latihan.json`, `segitiga/generator_soal.py` | Tunjuk Tingginya, Pilah Informasi |
| Misi | `frontend/js/halaman/misi.js`, `data/soal/misi.json`, `api/routes_periksa.py` | Cerita → langkah → ringkasan → refleksi → hasil; petunjuk 3 tingkat; diagnosis |
| Chatbot | `asisten/prompt.py`, `api/routes_asisten.py`, `halaman/asisten.js`, panel di `misi.js` | Beranda: jawab langsung. Misi: tidak menyebut jawaban langkah yang dinilai. |
| Data RMT (Tahap 1) | `segitiga/rmt.py`, `routes_progres.py`, `guru.js` | Label tahap per langkah, fase kesalahan, kolom "Fase sulit (I/E/O)" |

---

## 2. Rancangan RMT per komponen

Kolom "Wujud" menjelaskan **di mana** komponen muncul. **Baru** = belum ada dan akan dibuat. Semua aktivitas baru **tanpa skor**.

### 2.1 Fase fungsi kognitif [Dok. hal. 9–11]

| Komponen | Arti (dokumen) | Wujud di aplikasi | Status |
|---|---|---|---|
| **Input** | Mengumpulkan informasi dengan persepsi jelas dan akurat | Misi: langkah Diketahui/Ditanyakan (sudah ada). Latihan: Pilah Informasi (sudah ada). **Baru:** layar "Tebak dulu" (prediksi intuitif) di awal misi untuk mengaktifkan konsep sehari-hari [hal. 8, 11–12] | Ada + baru |
| **Elaborasi** | Mengolah: hubungan bagian-keseluruhan, sebab-akibat, penalaran | Materi Luas (setengah persegi panjang). **Baru:** pertanyaan "Mengapa?" singkat di layar Validasi (misalnya "Mengapa luas segitiga harus lebih kecil dari alas × tinggi?") | Ada + baru |
| **Output** | Menyampaikan hasil dengan jelas, simbol tepat, tanpa coba-coba | Cek satuan (sudah ada). **Baru:** kalimat kesimpulan di layar Refleksi ("Jadi, …") dengan kalimat pembuka yang disediakan | Ada + baru |

Masalah coba-coba pada soal pilihan ganda **tidak** termasuk Tahap 2, karena memperbaikinya mengubah skor. Lihat keputusan ❓D4.

### 2.2 Siklus penyelesaian masalah [Dok. hal. 8, 14]

| Komponen | Wujud di aplikasi | Status |
|---|---|---|
| **Planning (Perencanaan)** | **Baru:** layar "Susun rencanamu" setelah cerita. Siswa mengurutkan 3–4 kartu langkah, misalnya "Cari luas 1 kanopi → kalikan 4 → kalikan harga". Diperiksa server dan diberi umpan balik, tanpa skor. | Baru |
| **Representation** | Langkah pilah, pilih model, isian rumus (sudah ada). **Baru:** tabel "Diketahui" kecil di layar Rencana, sebagai organizer grafis [hal. 3] yang menampilkan data yang sudah dipilah siswa | Ada + baru |
| **Manipulation** | Langkah hitung yang ada, diperiksa Python | Ada (tidak diubah) |
| **Validation** | **Baru:** layar "Cek hasilmu" setelah langkah terakhir, sebelum ringkasan. Berisi 1–2 pertanyaan kewajaran (satuan, besar hasil). Diperiksa server, tanpa skor. | Baru |
| **Reflection** | "Jelaskan ke temanmu" (sudah ada). **Baru:** kalimat pembuka terpandu ("Pertama aku…, lalu…, jadi…") dan **umpan balik AI opsional** atas penjelasan siswa | Ada + baru |
| **Transcendence** | **Baru:** layar "Di mana lagi cara ini dipakai?" setelah ringkasan. Siswa memilih konteks lain yang memakai cara sama, lalu ditawari soal variasi tanpa skor [hal. 9] | Baru |

### 2.3 MLE [Dok. hal. 9, 11]

| Kriteria | Wujud | Status |
|---|---|---|
| **Intensionalitas** | **Baru:** layar pembuka misi "Tujuan misi ini" (1 kalimat) | Baru |
| **Resiprositas** | Periksa → umpan balik; layar Rencana dan Validasi menunggu respons siswa; chatbot misi | Ada + baru |
| **Makna** | **Baru:** satu kalimat "Mengapa ini penting" di layar pembuka (contoh: "Panitia perlu tahu luas agar tidak membeli kain berlebih") | Baru |
| **Transendensi** | Layar transendensi (2.2) | Baru |

### 2.4 Urutan layar misi setelah Tahap 2

```
Cerita (ada)
  → [BARU] Tujuan & Makna + Tebak dulu          (Intensionalitas, Makna, Input/konsep sehari-hari)
  → [BARU] Susun rencanamu + tabel Diketahui    (Planning, Representation)
  → Langkah 1..N (ada, BERSKOR, tidak diubah)   (Input/Representation/Manipulation)
  → [BARU] Cek hasilmu                           (Validation, Elaborasi)
  → Ringkasan (ada)
  → [BARU] Di mana lagi?                         (Transcendence)
  → Jelaskan ke temanmu (ada, diperkaya)         (Reflection, Output)
  → Hasil (ada)
```

Setiap layar baru berisi satu pertanyaan atau aktivitas dan boleh dilewati. Perkiraan tambahan waktu sekitar 2–4 menit per misi ❓D2.

---

## 3. Rancangan Cognitive Load

### 3.1 Prinsip per jenis beban

| Jenis | Strategi |
|---|---|
| **Intrinsic** (kerumitan materi) | Segmentasi, urutan sederhana ke kompleks, pengingat prasyarat, *fading* (contoh lengkap → setengah → mandiri), dan **saran remedial** sesuai fase yang paling sering salah (data Tahap 1) |
| **Extraneous** (beban penyajian) | Satu aktivitas per layar, label menempel pada gambar, tanpa elemen dekoratif, panel chatbot **tertutup secara bawaan** di misi, jawaban chatbot ringkas dan terstruktur |
| **Germane** (membangun skema) | Prediksi, perencanaan, validasi, penjelasan diri, transendensi dan variasi soal, umpan balik atas proses |

### 3.2 Penerapan per bagian aplikasi

| | Intrinsic | Extraneous | Germane |
|---|---|---|---|
| **Materi** | Ada: satu konsep per layar, urutan topik. **Baru:** *fading* di topik "Langkah soal cerita" (contoh lengkap → isi bagian akhir → mandiri) | Ada: label di gambar, tanpa animasi dekoratif. Tidak ada perubahan. | **Baru:** satu pertanyaan prediksi di topik Luas ("Menurutmu, luas segitiga lebih besar atau lebih kecil dari persegi panjang?") |
| **Latihan** | Ada: Pilah dan Tunjuk Tinggi bertahap. **Baru:** latihan disarankan sesuai fase sulit siswa (Input → Pilah Informasi; Elaborasi → materi Luas; Output → pengingat satuan) | Tidak ada perubahan | **Baru:** soal variasi tanpa skor dari layar Transendensi |
| **Misi** | Ada: langkah per layar, petunjuk bertahap, "Ingat lagi". Soal tetap. | **Baru:** panel chatbot diperkecil menjadi tombol "Tanya Pembimbing" yang membuka panel (mengurangi perhatian terbagi). Layar RMT baru memakai komponen yang sudah ada. | **Baru:** Rencana, Validasi, Transendensi, refleksi terpandu |
| **Chatbot** | Penjelasan bertingkat sesuai kesulitan (4.2) | Jawaban ringkas: susunan Diketahui/Rumus/Penyelesaian/Jadi, tanpa tabel. **Tidak diubah di beranda.** | Misi: pertanyaan terpimpin RMT, contoh paralel lengkap, umpan balik refleksi |

---

## 4. Chatbot: jawaban lengkap tetap tersedia

### 4.1 Chatbot beranda (Tanya Pembimbing)
**Tidak diubah.** Tetap menjawab langsung dan lengkap (instruksi dan pengaman saat ini, sudah diuji A–F). Ini sesuai keputusan peneliti 18 November.

### 4.2 Chatbot misi: mediasi RMT + jawaban lengkap yang tidak merusak skor

Tingkat bantuan ditentukan **oleh server** berdasarkan kondisi siswa, bukan oleh AI. Nilainya dicatat di kolom `tingkat_bantuan` (yang selama ini kosong).

| Tingkat | Kapan | Isi bantuan |
|---|---|---|
| 0 | Siswa bertanya konsep atau rumus | **Penjelasan lengkap** konsep atau rumus, langsung |
| 1 | Siswa salah 1 kali | Pertanyaan terpimpin sesuai **fase** kesalahan (Input: "data apa yang dipakai?"; Elaborasi: "hubungan alas dan tinggi?"; Output: "satuannya?") ditambah penjelasan konsepnya |
| 2 | Salah ≥ 2 kali, atau siswa minta "selesaikan" | **Contoh paralel yang diselesaikan lengkap** (soal serupa dengan angka berbeda, sampai "Jadi, …") |
| 3 | Langkah sudah benar, **atau** petunjuk tingkat 3 sudah dibuka (skor langkah itu sudah 0) | **Jawaban langkah itu sendiri** dijelaskan lengkap |

- Dengan tingkat 3, siswa yang benar-benar kesulitan tetap bisa mendapat jawaban lengkap, tetapi skor tetap sah: aturan yang sama dengan petunjuk tingkat 3 yang sudah ada. ❓D3
- `TAHAPAN_RMT` di `prompt.py` diisi dengan aturan per fase dan tahap di atas.
- Pengaman: penyaringan jawaban dilewati jika langkah sudah benar (sudah ada) **atau** petunjuk tingkat 3 sudah terbuka (baru).

---

## 5. Urutan implementasi bertahap

Setiap tahap mencakup:
- Tes baru.
- **Seluruh tes lama tetap lulus** (saat ini 248).
- Tes yang memastikan `misi.json`, `penilai.py`, dan `diagnosis.py` tidak berubah.
- Uji tampilan headless di HP 360 px dan laptop.
- Uji chatbot langsung (A–F) jika tahap itu menyentuh chatbot.
- Satu commit lokal setelah Anda setujui.

| Tahap | Isi | File | Pengujian khusus |
|---|---|---|---|
| **2A. Fondasi data aktivitas RMT** (tanpa tampilan) | Konten aktivitas per misi (tujuan, makna, tebak, rencana, validasi, transendensi, pembuka refleksi); pemuat dan validator; tabel baru `aktivitas_rmt`; endpoint ambil konten dan kirim jawaban | **Baru:** `backend/data/soal/rmt_misi.json`, `backend/segitiga/aktivitas_rmt.py`, `backend/api/routes_rmt.py`. **Ubah:** `backend/db.py` (tambah 1 tabel; tabel lama tidak diubah), `backend/app.py` (daftarkan route) | Validasi konten 4 misi; kunci aktivitas tidak bocor ke browser; jawaban tersimpan dengan kode anonim; skor misi tetap sama |
| **2B. Pembuka misi: Tujuan, Makna, Tebak dulu** | Layar baru setelah cerita | **Ubah:** `frontend/js/halaman/misi.js`, `frontend/js/api.js`, `frontend/css/komponen.css` (bila perlu, memakai token yang ada) | Alur misi 1–4 tetap selesai dengan skor 6/6; layar bisa dilewati; tidak ada scroll horizontal |
| **2C. Planning + tabel Diketahui** | Layar "Susun rencanamu" (urutkan kartu, ketuk atau seret) | **Baru:** `frontend/js/urutkan.js` (komponen urut). **Ubah:** `misi.js`, `aktivitas_rmt.py` (pemeriksa urutan) | Pemeriksa urutan di Python; komponen bisa dipakai dengan sentuhan; umpan balik menunjuk kartu yang salah posisi |
| **2D. Validation + Elaborasi "Mengapa?"** | Layar "Cek hasilmu" sebelum ringkasan | **Ubah:** `misi.js`, `rmt_misi.json` | Tidak mengubah status langkah atau skor; jawaban tercatat |
| **2E. Transendensi + refleksi terpandu** | Layar "Di mana lagi?" + soal variasi tanpa skor; kalimat pembuka refleksi | **Ubah:** `misi.js`, `generator_soal.py` (variasi soal luas sederhana), `routes_rmt.py` | Variasi soal benar (diperiksa Python, uji kesetaraan rumus); soal variasi tidak masuk skor |
| **2F. Chatbot misi sesuai RMT** | Isi `TAHAPAN_RMT`; tingkat bantuan 0–3 dari server; pengaman lewat pada tingkat 3; panel misi menjadi tombol yang membuka panel; umpan balik refleksi (opsional) | **Ubah:** `backend/asisten/prompt.py` (hanya bagian misi), `backend/api/routes_asisten.py`, `backend/asisten/pengaman.py`, `frontend/js/halaman/misi.js`. **Tidak diubah:** `INSTRUKSI_BERANDA` | Tes tiruan per tingkat; jawaban langkah tidak bocor pada tingkat 0–2; jawaban lengkap pada tingkat 3; **uji beranda A–F tetap lulus**; uji langsung misi baru |
| **2G. Cognitive Load adaptif + fading** | Saran remedial di Hasilku sesuai fase sulit; *fading* di materi soal cerita; prediksi di materi Luas | **Ubah:** `frontend/js/halaman/hasil.js`, `belajar.js`, `api/routes_progres.py` (data fase siswa sendiri) | Saran muncul sesuai data; materi lama tetap bisa dibuka |

> **Catatan penomoran (19 Nov 2026):** rencana 2C, 2D, dan 2E di tabel ini (Planning, Validasi, Transendensi + refleksi terpandu) sudah dikerjakan bersama **2B**. Tahap yang kemudian dikerjakan dengan nama **"Tahap 2C — Cognitive Load"** berisi rencana **2G** di atas (lihat [14-cognitive-load-tahap2c.md](14-cognitive-load-tahap2c.md)). Rencana **2F** (chatbot misi sesuai RMT) belum dikerjakan.

**Urutan dan alasannya:**
- **2A dulu**, karena tanpa tampilan dan menjadi fondasi semua tahap.
- **2B–2E** menambah layar satu per satu, masing-masing bisa diuji terpisah.
- **2F** menyentuh chatbot, jadi dikerjakan setelah aktivitasnya stabil dan diuji ketat agar kualitas jawaban tidak turun.
- **2G** terakhir, karena memakai data dari tahap sebelumnya.

**Di luar Tahap 2** (perlu keputusan terpisah): perbaikan skor coba-coba, pretest/posttest, deploy online.

---

## 6. Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Misi menjadi lebih panjang, sehingga beban dan waktu bertambah | Setiap layar baru berisi satu aktivitas singkat dan boleh dilewati; durasi diukur saat uji coba |
| Konten RMT (tujuan, rencana, validasi) kurang tepat secara pedagogis | Konten dalam file data yang mudah diedit, ditinjau peneliti/dosen sebelum dipakai |
| Kualitas jawaban chatbot menurun di 2F | `INSTRUKSI_BERANDA` tidak disentuh; uji A–F wajib lulus; uji misi baru dengan model sungguhan |
| Kuota OpenRouter (50/hari) cepat habis saat uji | Pengujian otomatis memakai klien tiruan; uji langsung hanya kasus yang perlu |
| Merusak skor | Tes hash `misi.json` dan tes skor 6/6 di setiap tahap |

---

## 7. Keputusan yang diperlukan sebelum mulai

| No | Keputusan |
|---|---|
| ❓D1 | Setuju dengan urutan layar misi di 2.4 (layar baru tanpa skor dan boleh dilewati)? |
| ❓D2 | Tambahan waktu sekitar 2–4 menit per misi dapat diterima? |
| ❓D3 | Chatbot misi boleh menjelaskan **jawaban langkah itu sendiri** setelah langkah benar atau petunjuk tingkat 3 dibuka? |
| ❓D4 | Masalah coba-coba di pilihan ganda tetap di luar Tahap 2? |
| ❓D5 | Pemetaan fase usulan (misalnya `SALAH_HITUNG` sebagai Output) tetap dipakai? |
| ❓D6 | Siapa yang meninjau isi konten aktivitas RMT (tujuan, makna, rencana, validasi) sebelum dipakai siswa? |
