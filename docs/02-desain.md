# 02 — Desain UI/UX

Semua keputusan desain di dokumen ini bertujuan **mengurangi extraneous load** dan **mendorong germane load**. Setiap aturan diberi kode bukti dari wawancara.

## 1. Prinsip desain (Mayer + CLT)

| Prinsip | Penerapan di SegiPintar | Bukti |
|---|---|---|
| **Segmenting** — materi dipotong jadi bagian kecil | Satu konsep / satu langkah per layar | EL01, IL02 |
| **Pacing oleh siswa** | Tombol **Ulangi** & **Lanjut**; tidak ada auto-advance; tidak ada timer di mode belajar | EL04 |
| **Multimedia** — gambar + kata lebih baik daripada kata saja | Setiap langkah punya gambar segitiga | EL02, GL01 |
| **Spatial contiguity** — teks dekat gambar | Label "alas = 12 m" ditulis di samping garis alas, bukan di legenda | EL02 |
| **Signaling** — tandai yang penting | Angka penting pada soal cerita diberi garis bawah berwarna setelah dipilah | EL05 |
| **Coherence** — buang yang tidak perlu | Tanpa maskot beranimasi, latar bergambar, musik, confetti | EL03, DS03 |
| **Worked example & fading** | Contoh lengkap → contoh dengan bagian kosong → soal mandiri | GL01, DS01 |
| **Scaffolding bertahap** | Petunjuk 3 tingkat | GL03 |
| **Self-explanation** | "Jelaskan ke temanmu" setelah misi | GL04 |
| **Variabilitas** | Variasi soal dengan konteks berbeda | GL05 |

## 2. Warna (token)

Palet sengaja dibatasi (EL03). Disimpan di `frontend/css/tokens.css`.

| Token | Terang | Gelap | Kegunaan |
|---|---|---|---|
| `--bg` | `#FAFAF7` | `#16181D` | Latar halaman |
| `--surface` | `#FFFFFF` | `#20232A` | Kartu |
| `--text` | `#1F2328` | `#E8E8E3` | Teks utama |
| `--text-muted` | `#5B616B` | `#A3A8B0` | Teks pendukung |
| `--primary` | `#2F5D8A` | `#7FA9D6` | Tombol utama, tautan |
| `--alas` | `#1F6FEB` | `#6CA4FF` | **Alas** (garis tebal) |
| `--tinggi` | `#D9730D` | `#F2A85B` | **Tinggi** (garis putus-putus) |
| `--sisi` | `#8A9099` | `#6B717A` | Sisi lain segitiga |
| `--benar` | `#2E7D4F` | `#6CC495` | Umpan balik benar (+ ikon ✓) |
| `--salah` | `#B3261E` | `#F08A82` | Umpan balik salah (+ ikon !) |
| `--primary-teks` | `#FFFFFF` | `#10141A` | Teks di atas tombol utama |
| `--isi` | `#EEF3F8` | `#252B35` | Isian bidang segitiga, latar petunjuk |
| `--garis` | `#DADDE2` | `#353A44` | Garis tepi kartu, kotak bantu (grid) |

Aturan:
- **Alas selalu biru, tinggi selalu oranye putus-putus** di seluruh aplikasi. Konsistensi ini mengurangi beban mengingat.
- Makna tidak boleh hanya dari warna: tinggi juga **putus-putus** + **simbol siku-siku** + label teks; umpan balik juga memakai ikon dan kata.
- Tidak ada gradien, bayangan tebal, atau latar bermotif.

## 3. Tipografi

- Satu keluarga huruf: **system-ui** (cepat dimuat, tanpa unduhan font).
- Ukuran dasar **18 px** di HP (siswa SMP, layar kecil); judul 22–26 px.
- Angka dan rumus: `font-variant-numeric: tabular-nums;` agar hitungan sejajar.
- Rumus ditulis dengan pecahan tumpuk sederhana (HTML/CSS), contoh: L = ½ × a × t.

## 4. Tata letak

### HP (≤ 600 px) — tampilan utama
```
┌─────────────────────────────┐
│ ← Misi 2 · Langkah 3 dari 6 │  ← progres langkah (bukan timer)
├─────────────────────────────┤
│                             │
│     [ GAMBAR SEGITIGA ]     │  ← label alas/tinggi langsung di gambar
│                             │
├─────────────────────────────┤
│ Tulis rumus luas satu       │  ← instruksi 1–2 kalimat
│ kanopi.                     │
│ ┌─────────────────────────┐ │
│ │ L = ½ × ___ × ___       │ │  ← isian
│ └─────────────────────────┘ │
│                             │
│ 💡 Petunjuk (1/3)           │
├─────────────────────────────┤
│ [ Ulangi ]      [ Periksa ] │  ← tombol di bawah, mudah dijangkau jempol
└─────────────────────────────┘
```

### Laptop (≥ 900 px)
Dua kolom: **gambar di kiri, langkah di kanan** (tetap berdekatan — spatial contiguity). Lebar konten maks 960 px.

## 5. Komponen

| Komponen | Keterangan |
|---|---|
| **Kartu Langkah** | Judul langkah, instruksi pendek, isian, tombol Periksa |
| **Segitiga SVG** | Dapat digeser (mode eksplorasi) atau statis (mode soal); label menempel pada garis |
| **Kotak Soal Cerita** | Kalimat dipisah per baris; angka dapat diketuk/diseret |
| **Zona Pilah** | 3 kotak: Diketahui / Ditanyakan / Tidak dipakai |
| **Petunjuk** | Tombol "💡 Petunjuk"; tiap ketukan membuka 1 tingkat berikutnya |
| **Umpan Balik** | Kotak di bawah isian: ✓ hijau / ! merah + kalimat yang menunjuk letak kesalahan |
| **Bilah Progres Langkah** | "Langkah 3 dari 6" + titik-titik; bukan timer |
| **Tombol Ingat Lagi** | Membuka pengingat prasyarat (IL03) dalam panel kecil yang bisa ditutup |

## 6. Animasi

Diizinkan **hanya** jika menjelaskan konsep (EL03):
- Garis tinggi "turun" dari puncak tegak lurus ke alas (±400 ms) saat pertama kali diperkenalkan.
- Segitiga menjadi setengah persegi panjang (menjelaskan asal ½ pada rumus luas).
- Angka "terbang" ke kotak Diketahui saat dipilah (±200 ms) agar siswa tahu ke mana angka pergi.

Dilarang: animasi masuk halaman, bintang berputar, confetti, latar bergerak, maskot.
Jika `prefers-reduced-motion: reduce` → semua animasi diganti perubahan langsung.

## 7. Bahasa dan penulisan

- Sapaan "kamu". Kalimat aktif, pendek (≤ 15 kata).
- Umpan balik salah **tidak menghakimi**: "Hampir! Coba cek lagi: apakah kamu sudah mengalikan dengan ½?" bukan "Salah!".
- Istilah konsisten: selalu "alas" dan "tinggi" (bukan "dasar", "a", "h" bergantian). Singkatan **a** dan **t** baru dipakai setelah dikenalkan.
- Satuan selalu ditulis: cm, m, cm², m².

## 8. Alur aplikasi (peta layar)

```
Beranda (masukkan nama panggilan + kode kelas)
   │
   ├── 1. Belajar
   │      ├── 1.1 Jenis-jenis segitiga (sisi & sudut)
   │      ├── 1.2 Alas dan tinggi  ← Segitiga Interaktif (F-01)
   │      ├── 1.3 Keliling
   │      ├── 1.4 Luas (dari setengah persegi panjang)
   │      └── 1.5 Langkah menyelesaikan soal cerita (F-03)
   │
   ├── 2. Latihan
   │      ├── Tunjuk Tingginya (F-02)
   │      ├── Pilah Informasi (F-05)
   │      └── Contoh bertahap → soal mandiri (F-09)
   │
   ├── 3. Misi Segitiga (game, F-15)  → lihat 04-game-dan-soal.md
   │
   └── 4. Hasilku (laporan, F-16)
```

Siswa boleh langsung ke bagian mana pun, tetapi Beranda **menyarankan** urutan Belajar → Latihan → Misi.
