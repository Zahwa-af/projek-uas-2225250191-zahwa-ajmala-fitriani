# 09 — Checklist Dokumen Penelitian

> **Tanggal pemeriksaan:** 18 November 2026
> **Cakupan:** folder `docs/` dan seluruh repo, termasuk mencari file PDF, Word, Excel, dan CSV.
> **Prinsip:** tidak ada data penelitian yang dibuat-buat. Tahapan RMT **belum final** sampai dikonfirmasi dosen.

**Status:** ✅ ada dan lengkap · 🟡 ada sebagian · ❌ belum ada · ⚠️ isinya rancangan atau asumsi penulis, **bukan** data atau ketentuan resmi

---

## 1. Ringkasan kondisi

| Temuan | Keterangan |
|---|---|
| Dokumen di repo | 7 file Markdown: `01` sampai `07`. **Belum ada file `08-…`.** |
| File sumber asli (PDF/Word/Excel) | **Tidak ada satu pun di repo.** Folder `docs/penelitian/` belum dibuat. |
| Asal isi dokumen | Tiga PDF dikirim lewat chat (laporan wawancara S01, kisi-kisi soal, ringkasan RMT), lalu isinya dipindahkan ke `01`, `04`, dan `07`. File aslinya tidak tersimpan di proyek. |
| Belum di-commit ke git | `docs/07-analisis-rmt.md`, `docs/09-…` (file ini), folder `web-statis/`, perubahan `README.md` |

---

## 2. Pemeriksaan per jenis dokumen

### 2.1 Dokumen RMT — 🟡 sebagian

| Item | Status | Lokasi / keterangan |
|---|---|---|
| File PDF ringkasan RMT (Kinard & Kozulin, Bab 1–6 + Simpulan, 15 hal.) | 🟡 | Hanya dari lampiran chat, **belum disimpan di repo** |
| Analisis RMT | ✅ | [07-analisis-rmt.md](07-analisis-rmt.md) |
| **Penetapan tahapan RMT oleh dosen** | ❌ | PDF tidak memuat satu daftar "tahapan RMT". Ada beberapa kerangka berurutan (Input–Elaborasi–Output; Analisis Tugas–Perencanaan–Refleksi; Representasi–Manipulasi–Validasi). **Belum dipilih.** Lihat Q1 di dokumen 07. |
| Halaman 6 PDF (poin "Komunikasi yang Presisi") | 🟡 | Terpotong |
| Definisi Representasi, Manipulasi, Validasi | ❌ | Tidak dijelaskan di PDF |
| Buku asli atau bab lengkap tentang format pelajaran RMT | ❌ | PDF hanya menyebut topik, tingkat kelas, dan alokasi waktu (hal. 13) |

### 2.2 Instrumen Mathematical Literacy — 🟡 sebagian

| Item | Status | Lokasi / keterangan |
|---|---|---|
| Kisi-kisi 4 soal (4 indikator, skor maksimum 6 per soal) | 🟡 | Isinya ada di [04-game-dan-soal.md](04-game-dan-soal.md) dan `backend/data/soal/misi.json`. **File PDF asli tidak ada di repo.** |
| Definisi operasional Mathematical Literacy dan sumbernya | ❌ | Dokumen 07 merujuk PISA sebagai asumsi. Belum dikonfirmasi. |
| Hasil validasi instrumen (validasi ahli, uji keterbacaan) | ❌ | Belum ada |
| Instrumen pretest dan posttest | ❌ | [05-rencana-pengujian.md](05-rencana-pengujian.md) menyebut "pretest 2 soal mirip kisi-kisi", tetapi soalnya **belum dibuat** |

### 2.3 Rubrik penilaian — 🟡 sebagian

| Item | Status | Keterangan |
|---|---|---|
| Skor per tahapan (dari kisi-kisi) | ✅ | Sesuai kisi-kisi dan sudah dipakai di aplikasi |
| **Kategori total skor** (Sangat baik ≥ 20, Baik ≥ 15, Cukup ≥ 10, Perlu bimbingan < 10) | ⚠️ | **Ditentukan penulis, bukan dari instrumen.** Perlu pedoman resmi dari dosen sebelum dipakai di laporan penelitian. |
| Aturan skor aplikasi (petunjuk tingkat 3 membuat skor tahap 0; Misi 1 tahap 1 dipecah 0,5 + 0,5) | ⚠️ | Keputusan desain aplikasi. Belum dikonfirmasi dosen. Lihat keputusan terbuka di [06-roadmap.md](06-roadmap.md). |
| Bintang dan lencana | ⚠️ | Hanya elemen motivasi game, **bukan** alat ukur penelitian |

### 2.4 Hasil wawancara Cognitive Load — 🟡 sebagian

| Item | Status | Keterangan |
|---|---|---|
| Laporan wawancara informan S01 (kelas VIII-A, 5 November 2026) | 🟡 | Isinya ada di [01-analisis-kebutuhan.md](01-analisis-kebutuhan.md). **File asli tidak ada di repo.** |
| Pedoman atau protokol wawancara (daftar pertanyaan) | ❌ | Yang ada hanya kode pertanyaan (K, IL, EL, GL, DS) di laporan |
| Respons tugas pemicu | ❌ | Laporan S01 menyatakan respons ini "tidak dicantumkan" |
| Informan lain selain S01 | ❌ | Baru 1 informan |
| Bukti persetujuan wawancara | ❌ | Laporan hanya mencatat durasi 40 menit |

### 2.5 Hasil uji coba siswa — ❌ belum ada

| Item | Status | Keterangan |
|---|---|---|
| Data uji coba aplikasi | ❌ | **Belum ada uji coba.** Satu-satunya data di database lokal berasal dari pengujian teknis (sesi uji bernama "Zahra"), **bukan data siswa**. |
| Angket beban kognitif | ⚠️ | Draf 8 butir di [05-rencana-pengujian.md](05-rencana-pengujian.md), diadaptasi penulis dari Paas/Leppink. Belum divalidasi dan sumbernya belum dicantumkan lengkap. |
| Target keberhasilan (misalnya ≥ 80% benar, skor EL ≤ 3, skor GL ≥ 7) | ⚠️ | Ditentukan penulis. Perlu ditetapkan oleh peneliti dan dosen. |
| Pedoman wawancara pasca-uji coba | ⚠️ | Draf 5 pertanyaan di dokumen 05 |

### 2.6 Dokumen pendukung lain — ❌ belum ada

| Item | Status | Keterangan |
|---|---|---|
| Persetujuan etika / *informed consent* (siswa, orang tua, sekolah) | ❌ | Wajib sebelum uji coba, terutama karena teks siswa akan dikirim ke DeepSeek |
| Kebijakan pengelolaan data percakapan AI | ❌ | Yang ada baru keputusan lisan: kode anonim, tanpa identitas |
| Lembar validasi ahli materi dan ahli media untuk aplikasi | ❌ | |
| Daftar referensi teori (RMT, PISA, Cognitive Load Theory) | 🟡 | Referensi tercantum di dokumen 07, tetapi belum dikonfirmasi peneliti |

### 2.7 Dokumen teknis aplikasi — ✅ (bukan data penelitian)
[02-desain.md](02-desain.md), [03-arsitektur.md](03-arsitektur.md), [06-roadmap.md](06-roadmap.md), dan [CLAUDE.md](../CLAUDE.md) sudah ada. Isinya rancangan aplikasi, bukan data penelitian.

---

## 3. Daftar dokumen yang perlu disiapkan peneliti

### Prioritas 1 — sebelum pengembangan chatbot
- [ ] **Salin file sumber asli ke `docs/penelitian/`:** laporan wawancara S01, kisi-kisi soal, ringkasan RMT
- [ ] **Keputusan dosen tentang tahapan RMT** yang dipakai (jawaban Q1–Q5 di [07-analisis-rmt.md](07-analisis-rmt.md))
- [ ] Halaman 6 PDF RMT versi lengkap (jika ada)
- [ ] Sumber definisi Mathematical Literacy dan Cognitive Load Theory yang dipakai di proposal

### Prioritas 2 — sebelum uji coba
- [ ] Pedoman kategori skor Mathematical Literacy dari dosen atau literatur, untuk menggantikan kategori buatan penulis
- [ ] Konfirmasi aturan skor aplikasi (petunjuk tingkat 3, pembagian 0,5 di Misi 1)
- [ ] Instrumen pretest dan posttest
- [ ] Angket beban kognitif final beserta sumbernya
- [ ] Hasil validasi instrumen dan aplikasi (ahli materi dan ahli media)
- [ ] Formulir persetujuan (siswa, orang tua, sekolah), termasuk penjelasan penggunaan AI (DeepSeek)
- [ ] Pedoman wawancara pasca-uji coba (final)

### Prioritas 3 — dari lapangan (tidak bisa dibuat oleh penulis)
- [ ] Data uji coba siswa: skor, log aplikasi, angket, wawancara
- [ ] Data wawancara tambahan (informan selain S01), jika direncanakan

---

## 4. Rekomendasi urutan pengerjaan

| No | Pekerjaan | Pelaku | Bergantung pada |
|---|---|---|---|
| 1 | Simpan file sumber asli di `docs/penelitian/`, lalu commit dokumen yang belum di-commit | Peneliti (dibantu Claude untuk commit) | — |
| 2 | Konsultasi dosen: tahapan RMT, kategori skor, aturan skor | Peneliti dan dosen | Dokumen 07 dan 09 |
| 3 | Rancangan teknis chatbot **yang tidak bergantung pada tahapan RMT**: `.env`, `.gitignore`, klien DeepSeek dengan mock, endpoint, pencatatan data anonim | Claude, **setelah Anda izinkan** | — (bisa paralel dengan langkah 2) |
| 4 | Instruksi model dan alur percakapan sesuai tahapan RMT final | Claude | Langkah 2 |
| 5 | Panel "Tanya Pembimbing" di langkah Misi | Claude | Langkah 3 dan 4 |
| 6 | Finalisasi instrumen (pretest, posttest, angket) dan persetujuan etika | Peneliti dan dosen | Langkah 2 |
| 7 | Validasi ahli, lalu revisi aplikasi | Validator, peneliti, dan Claude | Langkah 5 dan 6 |
| 8 | Uji coba terbatas dengan siswa, lalu kumpulkan data | Peneliti | Langkah 6 dan 7 |
| 9 | Analisis data dan revisi berdasarkan temuan | Peneliti, dibantu Claude untuk olah data | Langkah 8 |

Langkah 3 bisa dikerjakan sambil menunggu dosen, karena tidak memuat isi RMT. Tetapi sesuai instruksi, integrasi DeepSeek **belum** dimulai sampai ada izin.

---

## 5. Pertanyaan untuk peneliti
1. Nomor dokumen **08** sengaja dikosongkan atau akan diisi dokumen lain?
2. Apakah kategori skor, aturan skor, dan target keberhasilan yang selama ini ditulis penulis ditandai ⚠️ di dokumen lama? Atau cukup dicatat di checklist ini? Dokumen lama **tidak diubah** sesuai instruksi.
