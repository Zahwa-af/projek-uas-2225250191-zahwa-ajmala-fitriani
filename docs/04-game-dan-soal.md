# 04 — Game "Misi Segitiga" dan Bank Soal

Game ini menguji dan melatih **mathematical literacy** siswa pada materi segitiga, berdasarkan **Kisi-kisi Soal Mathematical Literacy** (4 soal, masing-masing skor maksimum 6).

## 1. Konsep game

**Cerita bingkai:** Siswa menjadi **anggota Panitia Sekolah** yang membantu menyelesaikan 4 masalah nyata di sekolah. Satu cerita yang konsisten (lingkungan sekolah) mengurangi beban memahami konteks baru di setiap soal (EL05).

| Misi | Judul | Indikator literasi (kisi-kisi) | Konteks | Lencana |
|---|---|---|---|---|
| 1 | Bendera Kelas | Mathematical Reasoning | Memilih desain bendera | 🧭 Penalar |
| 2 | Kanopi Sekolah | Formulating Situations Mathematically | Kain kanopi & biaya | 🧩 Perumus |
| 3 | Taman Sekolah | Employing Concepts, Facts, and Procedures | Bagian bunga & rumput | 🧮 Penghitung |
| 4 | Papan Informasi | Interpreting, Applying, and Evaluating | Memeriksa hitungan teman | 🔍 Pemeriksa |

### Elemen game (dipilih agar tidak menambah beban kognitif)

| Dipakai | Tidak dipakai (dan alasannya) |
|---|---|
| Daftar misi sederhana dengan status ✓ | Peta petualangan beranimasi (EL03) |
| 0–3 ⭐ per misi | Papan peringkat antar-siswa (menambah tekanan, bukan pemahaman) |
| Lencana per indikator literasi | Timer / hitung mundur (EL04) |
| Progres "Langkah 3 dari 6" | Nyawa/hati yang habis (siswa harus boleh salah untuk belajar) |
| Bisa mengulang misi dengan **variasi soal** | Suara/musik otomatis (EL03) |

### Alur satu misi

```
Baca cerita (dipotong per kalimat, gambar di atas)
   ▼
Langkah 1 … Langkah N   ← satu langkah per layar
   │   ├─ jawab → [Periksa]
   │   │     ├─ benar  → ✓ + penjelasan singkat → [Lanjut]
   │   │     └─ salah  → umpan balik yang menunjuk kesalahan → coba lagi
   │   └─ [💡 Petunjuk] tingkat 1 → 2 → 3
   ▼
Ringkasan langkah (semua langkah tampil berurutan — membangun skema, GL01)
   ▼
"Jelaskan ke temanmu" (opsional, GL04)
   ▼
Skor rubrik + ⭐ + lencana
```

Siswa **tidak bisa lanjut ke langkah berikutnya** sebelum langkahnya benar atau petunjuk tingkat 3 dibuka. Dengan begitu setiap langkah berikutnya selalu berangkat dari hasil yang benar (tidak ada kesalahan berantai).

## 2. Aturan skor

### Skor rubrik (mengikuti kisi-kisi, maks 6 per misi, total 24)

| Kondisi pada satu tahapan | Skor tahapan |
|---|---|
| Benar tanpa petunjuk atau dengan petunjuk tingkat 1–2, pada percobaan 1–3 | **Penuh** (sesuai rubrik) |
| Petunjuk tingkat 3 dibuka (cara lengkap ditampilkan) | **0** |
| Salah 3 kali → petunjuk tingkat 3 terbuka otomatis | **0** |

Tahapan bernilai 2 dipecah menjadi 2 isian bernilai masing-masing 1 (lihat tabel per misi).
Misi 1 tahap 1 (skor 1) dipecah menjadi langkah 1a (pilah, 0,5) dan 1b (pilihan, 0,5), sehingga skor Misi 1 bisa bernilai x,5.

> **Keputusan yang perlu dikonfirmasi pembimbing/dosen:** apakah petunjuk tingkat 2 (rumus diberikan) sebaiknya mengurangi skor? Rancangan ini **tidak** menguranginya agar siswa tidak takut meminta bantuan (GL03), tetapi penggunaan petunjuk tetap dicatat dan memengaruhi ⭐.

### Bintang (⭐) — motivasi, bukan nilai

| ⭐ | Syarat |
|---|---|
| ⭐⭐⭐ | Skor 6/6 dan memakai petunjuk paling banyak 1 kali |
| ⭐⭐ | Skor ≥ 4 |
| ⭐ | Misi selesai |

### Kategori literasi (untuk laporan)

| Total skor (24) | Kategori |
|---|---|
| 20–24 | Sangat baik |
| 15–19 | Baik |
| 10–14 | Cukup |
| < 10 | Perlu bimbingan |

## 3. Jenis langkah (komponen interaksi)

| Tipe | Tampilan | Contoh penggunaan |
|---|---|---|
| `pilah` | Angka dari cerita diseret ke kotak berlabel | Diketahui / ditanyakan / tidak dipakai |
| `pilihan` | 2–4 tombol pilihan besar | Memilih rumus, keputusan, alasan |
| `angka` | Isian angka + pilihan satuan | Menghitung luas, biaya |
| `rumus` | Kalimat rumpang `½ × ☐ × ☐` | Substitusi nilai ke rumus |
| `teks_bebas` | Kotak teks (tidak dinilai otomatis) | "Jelaskan ke temanmu" |

## 4. Rincian 4 misi

Angka di bawah adalah **versi asli kisi-kisi** (dipakai pada mode Misi untuk pengukuran). Mode **Latihan Ulang** memakai variasi dari generator (bagian 6).

---

### Misi 1 — Bendera Kelas (Mathematical Reasoning)

**Cerita (ditampilkan per kalimat):**
> Panitia kelas akan membuat bendera berbentuk segitiga.
> Desain A: alas 60 cm, tinggi 40 cm.
> Desain B: alas 80 cm, tinggi 30 cm.
> Kain hanya cukup untuk satu bendera dengan luas paling besar.
> Desain mana yang sebaiknya dipilih?

**Gambar:** dua segitiga berdampingan, skala proporsional, label alas (biru) & tinggi (oranye) langsung pada gambar.

| Tahap | Skor | Tipe | Tugas siswa | Kunci |
|---|---|---|---|---|
| 1 | 1 | `pilah` + `pilihan` | Seret 60, 40, 80, 30 ke tabel (A-alas, A-tinggi, B-alas, B-tinggi), lalu pilih: "Yang harus dibandingkan adalah…" | Tabel benar **dan** "luas kedua bendera" |
| 2a | 1 | `angka` | Luas Desain A | 1.200 cm² |
| 2b | 1 | `angka` | Luas Desain B | 1.200 cm² |
| 3 | 1 | `pilihan` | A > B / A < B / **A = B** | A = B |
| 4 | 1 | `pilihan` | Pilih A saja / B saja / **keduanya bisa dipilih** | Keduanya bisa dipilih |
| 5 | 1 | `pilihan` (+ `teks_bebas` opsional) | Alasan yang paling tepat | "Hasil kali alas dan tinggi sama (60 × 40 = 80 × 30 = 2.400), jadi luasnya sama" |

Pengecoh tahap 5: "Karena alas B lebih panjang", "Karena tinggi A lebih tinggi", "Karena keduanya berbentuk segitiga".

**Petunjuk tahap 2a:**
1. "Luas segitiga memakai alas dan tinggi. Mana alas dan tinggi Desain A pada gambar?"
2. "Rumusnya L = ½ × alas × tinggi."
3. "L = ½ × 60 × 40 = ½ × 2.400 = 1.200 cm²."

---

### Misi 2 — Kanopi Sekolah (Formulating Situations Mathematically)

**Cerita:**
> Sekolah akan memasang kain penutup pada kanopi berbentuk segitiga.
> Satu kanopi: alas 3 m, tinggi 2 m.
> Ada 4 kanopi yang ukurannya sama.
> Harga kain Rp25.000 setiap 1 m².
> Berapa luas seluruh kain dan berapa biayanya?

| Tahap | Skor | Tipe | Tugas siswa | Kunci |
|---|---|---|---|---|
| 1 | 1 | `pilah` | Seret 3 m, 2 m, 4, Rp25.000 ke label: alas / tinggi / jumlah kanopi / harga per m² | Sesuai |
| 2 | 1 | `pilihan` (pilih 2) | Apa yang ditanyakan? | Luas kain 4 kanopi **dan** total biaya |
| 3 | 1 | `pilihan` | Model luas satu kanopi | L = ½ × alas × tinggi |
| 4 | 1 | `rumus` + `angka` | Luas satu kanopi | ½ × 3 × 2 = 3 m² |
| 5 | 1 | `angka` | Luas seluruh kain | 4 × 3 = 12 m² |
| 6 | 1 | `angka` | Biaya | 12 × 25.000 = Rp300.000 |

Pengecoh tahap 2: "Keliling kanopi", "Jumlah kanopi". Pengecoh tahap 3: `alas × tinggi`, `alas + tinggi + sisi`, `½ × (alas + tinggi)`.

**Petunjuk tahap 6:**
1. "Kamu sudah tahu luas seluruh kain. Setiap 1 m² harganya berapa?"
2. "Biaya = luas seluruh kain × harga per m²."
3. "Biaya = 12 × Rp25.000 = Rp300.000."

---

### Misi 3 — Taman Sekolah (Employing Concepts, Facts, and Procedures)

**Cerita:**
> Taman sekolah berbentuk segitiga dengan alas 12 m dan tinggi 7 m.
> ⅓ bagian taman ditanami bunga.
> Sisanya ditanami rumput.
> Berapa luas bagian bunga dan bagian rumput?

**Gambar:** segitiga taman; setelah tahap 3 benar, ⅓ bagian diarsir (visual pecahan, membantu IL03).

| Tahap | Skor | Tipe | Tugas siswa | Kunci |
|---|---|---|---|---|
| 1 | 1 | `pilah` | Seret 12 m, 7 m, ⅓ ke: alas / tinggi / bagian bunga | Sesuai |
| 2a | 1 | `rumus` | Substitusi: L = ½ × ☐ × ☐ | ½ × 12 × 7 |
| 2b | 1 | `angka` | Luas seluruh taman | 42 m² |
| 3a | 1 | `rumus` | Luas bunga = ☐ × ☐ | ⅓ × 42 |
| 3b | 1 | `angka` | Luas bunga | 14 m² |
| 4 | 1 | `angka` | Luas rumput | 28 m² (dari 42 − 14, atau ⅔ × 42 — keduanya diterima) |

---

### Misi 4 — Papan Informasi (Interpreting, Applying, and Evaluating)

**Cerita:**
> Papan informasi berbentuk segitiga: alas 2,4 m, tinggi 1,5 m.
> Dika menghitung luasnya: 2,4 × 1,5 = 3,6 m².
> Dika berkata kain 3,6 m² sudah pas untuk menutup satu sisi papan.
> Apakah kamu setuju dengan perhitungan Dika?

(Nama "Dika" fiktif; menghindari kata "seorang siswa" yang abstrak.)

| Tahap | Skor | Tipe | Tugas siswa | Kunci |
|---|---|---|---|---|
| 1 | 1 | `pilihan` | Apa yang dilakukan Dika? | Mengalikan alas dan tinggi: 2,4 × 1,5 = 3,6 |
| 2 | 1 | `pilihan` | Rumus luas segitiga yang benar | ½ × alas × tinggi (bukan alas × tinggi) |
| 3 | 1 | `angka` | Luas yang benar | 1,8 m² |
| 4 | 1 | `pilihan` | Hubungan 3,6 dengan 1,8 | 3,6 adalah **2 kali** luas sebenarnya karena ½ tidak dipakai |
| 5 | 1 | `pilihan` | Setuju dengan perhitungan Dika? | **Tidak setuju** |
| 6 | 1 | `pilihan` | Kesimpulan | Kain minimal **1,8 m²** untuk satu sisi (tanpa memperhitungkan lipatan/potongan) |

> **Catatan untuk guru:** kain 3,6 m² sebenarnya *cukup* (bahkan berlebih 2 kali). Yang keliru adalah **perhitungan luasnya**. Pilihan tahap 6 dirancang agar siswa membedakan "cukup" dengan "luas yang tepat", misalnya pengecoh: "Kain 3,6 m² kurang".

**Gambar khusus tahap 4:** persegi panjang 2,4 × 1,5 dibagi diagonal menjadi 2 segitiga → memperlihatkan mengapa 3,6 = 2 × 1,8 (animasi konsep yang diizinkan).

---

## 5. Diagnosis kesalahan (F-14)

Python membandingkan jawaban salah dengan pola kesalahan umum. Umpan balik selalu menunjuk **di langkah mana** dan **kemungkinan penyebab**.

| Kode | Pola terdeteksi | Contoh | Umpan balik |
|---|---|---|---|
| `LUPA_SETENGAH` | jawaban = alas × tinggi | Misi 1: 2.400; Misi 4: 3,6 | "Hasilmu 2 kali lebih besar. Sudahkah kamu mengalikan dengan ½?" |
| `PAKAI_KELILING` | jawaban = jumlah sisi | — | "Itu cara menghitung keliling. Yang ditanya luas." |
| `JUMLAH_BUKAN_KALI` | jawaban = alas + tinggi atau ½(alas + tinggi) | Misi 3: 19 atau 9,5 | "Pada rumus luas, alas dan tinggi **dikalikan**, bukan dijumlahkan." |
| `SALAH_TINGGI` | memakai sisi miring sebagai tinggi | (soal latihan dengan sisi miring) | "Tinggi harus **tegak lurus** dengan alas. Lihat garis oranye." |
| `LUPA_JUMLAH_BENDA` | hasil untuk 1 benda padahal diminta semua | Misi 2: 3 m² atau Rp75.000 | "Itu untuk 1 kanopi. Ada berapa kanopi?" |
| `TERTUKAR_BAGIAN` | menjawab bagian yang lain | Misi 3: bunga = 28 | "Itu luas bagian rumput. Bunga hanya ⅓ bagian." |
| `SALAH_SATUAN` | angka benar, satuan salah | 1.200 cm | "Angkamu benar! Satuan luas memakai pangkat dua: cm²." |
| `SALAH_HITUNG` | rumus benar, hasil meleset (selisih kecil) | ½ × 12 × 7 = 48 | "Rumusmu sudah benar. Coba hitung ulang perkaliannya." + tombol **Ingat lagi** (IL03) |
| `SALAH_DESIMAL` | posisi koma bergeser (×10 / ÷10) | 18 untuk 1,8 | "Perhatikan letak koma pada 2,4 dan 1,5." |
| `TIDAK_DIKENALI` | — | — | Umpan balik umum + saran membuka petunjuk |

**Toleransi angka:** selisih relatif ≤ 0,5% dianggap benar (mengatasi pembulatan ⅓). Satuan dinilai hanya jika langkah memintanya; jika angka benar tetapi satuan salah, siswa diberi kesempatan memperbaiki satuan tanpa mengulang hitungan.

## 6. Generator variasi soal (F-13, GL05)

Mode **Latihan Ulang** membuat soal dengan **struktur langkah sama** tetapi **konteks dan angka berbeda**, supaya siswa belajar mengenali "cara penyelesaiannya masih sama" (GL05).

| Misi | Konteks pengganti | Aturan angka |
|---|---|---|
| 1 | bendera, layang-layang, papan nama, potongan karton | alas × tinggi genap; **50% luas sama, 50% berbeda** (agar siswa tidak menghafal "pasti sama") |
| 2 | kanopi, atap tenda, rambu, hiasan dinding | luas satu benda bilangan bulat; jumlah 2–6; harga kelipatan Rp5.000 |
| 3 | taman, kebun, lapangan, kolam | luas habis dibagi penyebut pecahan (½, ⅓, ¼, ⅕) |
| 4 | papan, spanduk, layar | alas & tinggi desimal satu angka di belakang koma; kesalahan teman bisa `LUPA_SETENGAH` atau `JUMLAH_BUKAN_KALI` |

Tingkat lanjut (opsional): menambahkan **satu angka pengecoh** di cerita (misalnya "sekolah memiliki 18 kelas") untuk melatih Pilah Informasi (EL05). Hanya dipakai setelah siswa menyelesaikan misi asli.

## 7. Format data soal (`backend/data/soal/misi.json`)

```json
{
  "id": 3,
  "judul": "Taman Sekolah",
  "indikator": "Employing Mathematical Concepts, Facts, and Procedures",
  "lencana": "Penghitung",
  "cerita": [
    "Taman sekolah berbentuk segitiga dengan alas 12 m dan tinggi 7 m.",
    "⅓ bagian taman ditanami bunga.",
    "Sisanya ditanami rumput.",
    "Berapa luas bagian bunga dan bagian rumput?"
  ],
  "gambar": { "jenis": "segitiga", "alas": 12, "tinggi": 7, "satuan": "m" },
  "langkah": [
    {
      "no": "2b",
      "tahap": 2,
      "skor": 1,
      "tipe": "angka",
      "instruksi": "Hitung luas seluruh taman.",
      "kunci": { "nilai": 42, "satuan": "m²" },
      "konteks_diagnosis": { "alas": 12, "tinggi": 7 },
      "petunjuk": [
        "Luas segitiga memakai alas dan tinggi.",
        "L = ½ × alas × tinggi.",
        "L = ½ × 12 × 7 = ½ × 84 = 42 m²."
      ],
      "penjelasan_benar": "Tepat! ½ × 12 × 7 = 42 m²."
    }
  ]
}
```

Field `kunci`, `konteks_diagnosis`, dan `petunjuk` **tidak pernah** dikirim oleh `GET /api/misi/<id>`. Petunjuk dikirim satu per satu lewat `POST /api/petunjuk`.

## 8. Mini-game pemanasan (Latihan, tidak masuk skor rubrik)

| Mini-game | Tujuan | Mekanik |
|---|---|---|
| **Tunjuk Tingginya** (F-02) | IL01 | Segitiga acak (lancip, siku-siku, tumpul) dengan alas tertentu; siswa mengetuk garis tinggi yang benar di antara 3 garis. Pada segitiga tumpul, tinggi jatuh di **perpanjangan alas** — kasus yang sering membingungkan. |
| **Pilah Informasi** (F-05) | EL05, IL04 | Cerita pendek; siswa menyeret setiap angka ke Diketahui / Ditanyakan / Tidak dipakai. |
| **Contoh Bertahap** (F-09) | GL01 | 3 soal serupa: (1) semua langkah terisi, siswa hanya membaca + Lanjut; (2) langkah terakhir kosong; (3) semua langkah kosong. |
