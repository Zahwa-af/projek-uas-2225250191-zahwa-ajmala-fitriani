# 14 — Cognitive Load (Tahap 2C): fading dan remedial adaptif

> **Tanggal:** 19 November 2026 · **Status:** sudah diimplementasikan, belum di-commit.
>
> ⚠️ **Keterangan penelitian.** Implementasi ini disusun dari:
> - analisis kebutuhan (wawancara S01, [01-analisis-kebutuhan.md](01-analisis-kebutuhan.md));
> - kisi-kisi dan rubrik ([04-game-dan-soal.md](04-game-dan-soal.md));
> - diagnosis kesalahan yang sudah ada di aplikasi.
>
> Implementasi ini **belum** berdasarkan analisis hasil uji coba instrumen Mathematical Literacy, karena data uji coba belum tersedia di proyek (lihat [09](09-checklist-dokumen-penelitian.md) bagian 2.5). Ambang dan aturan di bawah perlu ditinjau ulang setelah data uji coba ada.

**Penomoran:** "Tahap 2C" di dokumen ini adalah tahap Cognitive Load yang diminta peneliti. Isinya setara dengan rencana **2G** di [13-rencana-implementasi-tahap2.md](13-rencana-implementasi-tahap2.md). Rencana 2C–2E lama di dokumen 13 (Planning, Validasi, Transendensi) sudah dikerjakan bersama Tahap 2B.

## 1. Yang tidak diubah
- **Penilaian:** soal, kunci, rubrik, dan bobot skor (`misi.json`, `penilai.py`, `diagnosis.py`) tidak diubah. Dijaga oleh tes sidik jari.
- **Alur:** alur RMT dari Tahap 2B dan perilaku chatbot (prompt dan backend) tetap.
- **Database:** tidak ada tabel atau kolom baru, dan tidak ada data yang dihapus.

## 2. Penerapan per jenis beban

| Jenis | Penerapan | Dasar |
|---|---|---|
| Intrinsic | Soal Cerita Bertahap: 1 isian per layar. Tingkat 1–2 memakai angka kecil tanpa pengecoh. Tingkat 3–4 memakai angka lebih besar ditambah sisi miring sebagai informasi pengecoh. | IL02, IL04, IL01 |
| Extraneous | Panel Pembimbing AI di misi **tertutup secara bawaan** dan terbuka bila diketuk atau sudah ada percakapan. Saran remedial paling banyak 2 sekaligus. Label tombol tetap (Kembali / Periksa / Lanjut / Selesai). | EL01, EL03, DS03 |
| Germane | Contoh hampir lengkap lalu bantuan dipudarkan. Penjelasan diri: siswa menulis dulu, baru membandingkan. Layar **Bandingkan keliling dan luas** (Belajar 4/5). Ajakan "jelaskan" di layar rumus luas. | GL01, GL04, GL05, K03 |

## 3. Fading — Soal Cerita Bertahap (`#/latihan/bertahap`, tanpa skor)

| Tingkat | Yang sudah ditampilkan | Yang diisi siswa |
|---|---|---|
| 0 (materi Belajar 5) | Contoh lengkap 5 langkah | — |
| 1 Contoh hampir lengkap | Diketahui, Ditanyakan, Rumus, Hitung luas satu | Luas semua benda |
| 2 Lengkapi hitungan | Diketahui, Ditanyakan, Rumus | Luas satu, luas semua |
| 3 Sedikit bantuan | Diketahui (gambar tanpa angka, ada pengecoh) | Luas satu, luas semua |
| 4 Mandiri | — | Luas satu, luas semua |

**Aturan** (`backend/segitiga/fading.py`, `tingkat_berikut`):
- **Naik:** benar tanpa salah dan tanpa petunjuk → naik **satu** tingkat.
- **Turun:** membuka petunjuk ke-3 atau salah ≥ 3 kali dalam satu soal → turun satu tingkat.
- **Tetap:** kondisi lainnya.

**Bantuan tidak pernah hilang seluruhnya.** Di setiap tingkat, petunjuk 1–3 tetap tersedia dan tautan "Lihat lagi contoh lengkap" selalu ada. Tingkat terakhir disimpan di `localStorage` perangkat. Penjelasan diri siswa tidak dikirim ke server.

## 4. Remedial adaptif (`backend/segitiga/remedial.py`, `GET /api/remedial/<sesi_id>`)

**Data:** hanya data milik siswa itu sendiri:
- jawaban salah dan kode diagnosisnya (`jawaban_langkah`);
- petunjuk ke-3 yang terbuka (`petunjuk_dibuka`).

Endpoint ini hanya membaca. Skor dan jawaban tidak diubah.

**Pemetaan kode ke area:**

| Kode | Area |
|---|---|
| `SALAH_TINGGI` | Alas & tinggi |
| `LUPA_SETENGAH`, `JUMLAH_BUKAN_KALI`, `RUMUS_SALAH` | Rumus luas |
| `PAKAI_KELILING` | Luas vs keliling |
| `PILAH_SALAH`, `KURANG_LENGKAP`, `TERTUKAR_BAGIAN`, `LUPA_JUMLAH_BENDA` | Memilah informasi |
| `SALAH_SATUAN`, `SATUAN_KOSONG` | Satuan |
| `SALAH_HITUNG`, `SALAH_DESIMAL` | Operasi hitung (beserta "Ingat lagi") |

Kode umum (`PILIHAN_SALAH`, `TIDAK_DIKENALI`) dan petunjuk ke-3 dipetakan lewat fase RMT langkahnya (Tahap 1):
- Input → Memilah informasi
- Elaborasi → Rumus luas
- Output → Menafsirkan hasil

**Ambang:**
- Sebuah area disarankan bila bobotnya ≥ 2. Satu jawaban salah dan satu petunjuk ke-3 masing-masing berbobot 1.
- Paling banyak 2 area ditampilkan, diurutkan dari bobot terbesar.
- `KOSONG` dan `FORMAT_ANGKA` tidak dihitung sebagai kesulitan.

**Tempat tampil:**
- **Layar hasil misi:** hanya kesalahan pada main misi itu.
- **Hasilku:** semua misi.

Setiap saran berisi tautan ke materi atau latihan yang sesuai.

## 4b. Perbaikan setelah audit (19 November 2026)
- **Tingkat latihan:** disimpan hanya untuk siswa yang sedang masuk. "Ganti nama" menghapusnya, jadi HP bersama tidak meninggalkan `sesi_id` siswa lain.
- **Remedial di Hasilku:** hanya memakai percobaan terakhir tiap misi yang berisi jawaban, sehingga saran hilang setelah siswa berhasil saat mengulang.
- **Batas laju:** POST `/api/latihan/` dan `/api/rmt/` dibatasi per IP.
- **Layar Bandingkan keliling dan luas:** memakai warna alas biru dan tinggi oranye.

## 5. Yang perlu ditinjau peneliti/dosen
1. Ambang remedial (bobot ≥ 2) dan aturan naik/turun tingkat fading. Sesuaikan setelah ada data uji coba.
2. Pemetaan kode diagnosis ke area materi.
3. Kalimat soal Soal Cerita Bertahap dan pertanyaan penjelasan diri.
4. Apakah data latihan bertahap perlu dicatat untuk penelitian. Saat ini tidak dicatat, jadi tidak ada perubahan database.
