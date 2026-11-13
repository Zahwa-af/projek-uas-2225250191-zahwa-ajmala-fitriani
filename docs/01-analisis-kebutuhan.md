# 01 — Analisis Kebutuhan

Sumber: *Laporan Hasil Wawancara Analisis Kebutuhan: Materi Bangun Datar Segitiga* (informan S01, kelas VIII-A, 5 November 2026, durasi 40 menit, pewawancara Zahwa Ajmala Fitriani).

## 1. Kerangka teori: Cognitive Load Theory (CLT)

| Kode | Jenis beban | Arti | Strategi aplikasi |
|---|---|---|---|
| **IL** | Intrinsic Load | Kerumitan bawaan materi (banyak unsur yang harus diolah bersamaan) | **Kelola**: pecah materi jadi langkah kecil, urutkan dari sederhana ke kompleks, ingatkan prasyarat |
| **EL** | Extraneous Load | Beban akibat cara penyajian yang buruk | **Kurangi**: tampilan sederhana, gambar dekat teks, tempo diatur siswa, tanpa distraksi |
| **GL** | Germane Load | Usaha mental untuk membangun skema/pemahaman | **Dorong**: contoh soal bertahap, refleksi, menjelaskan ulang, variasi konteks |
| **DS** | Desain (usulan siswa) | Masukan langsung siswa tentang aplikasi | Diterjemahkan menjadi fitur |
| **K** | Konteks | Pengalaman belajar sebelumnya | Titik awal materi |

## 2. Temuan kunci

### Konteks (K)
- Materi segitiga dipelajari di kelas VII semester 2; siswa ingat **jenis-jenis segitiga** (K01).
- Pembelajaran di kelas: guru menjelaskan di papan tulis, menggambar segitiga, memberi contoh, siswa mencatat dan latihan (K02).
- Siswa lebih yakin pada **keliling**; ragu pada **luas** dan **soal cerita** (K03).

### Intrinsic Load (IL)
| Kode | Temuan |
|---|---|
| IL01 | Sulit menentukan **mana alas dan mana tinggi** |
| IL02 | Langkah penyelesaian: diketahui → ditanyakan → pilih rumus |
| IL03 | Prasyarat: perkalian, pembagian, penjumlahan |
| IL04 | Luas/keliling biasa masih bisa; **soal cerita membingungkan** |
| IL05 | Kesalahan karena **salah memilih rumus** atau **salah hitung** |

### Extraneous Load (EL)
| Kode | Temuan |
|---|---|
| EL01 | Bingung jika **soal panjang** |
| EL02 | **Gambar** lebih mudah dipahami daripada tulisan saja |
| EL03 | **Warna terlalu banyak / animasi ramai** membuat tidak fokus |
| EL04 | Penjelasan **terlalu cepat** menyulitkan |
| EL05 | Sulit memahami maksud cerita dan **kegunaan setiap angka** |

### Germane Load (GL)
| Kode | Temuan |
|---|---|
| GL01 | Paling mudah paham jika ada **gambar + contoh cara menghitung** |
| GL02 | Siswa biasa **mengecek ulang** rumus dan hitungan |
| GL03 | Lebih suka **petunjuk satu per satu**, bukan langsung jawaban |
| GL04 | Pernah **menjelaskan kepada teman** |
| GL05 | Mengenali apakah **cara penyelesaian soal baru masih sama** |

### Usulan desain siswa (DS)
| Kode | Usulan |
|---|---|
| DS01 | Ada gambar segitiga, penjelasan rumus, contoh soal + cara mengerjakan, bisa dilihat lagi |
| DS02 | Rumus & cara mencari alas-tinggi dijelaskan pelan-pelan; latihan mandiri; aplikasi **tahu bagian mana yang salah** |
| DS03 | Jangan terlalu banyak tulisan, warna, dan animasi yang tidak berkaitan dengan materi |

## 3. Matriks kebutuhan → fitur

Setiap fitur diberi ID (F-xx) yang dipakai di roadmap dan rencana pengujian.

| ID | Bukti | Kebutuhan | Fitur aplikasi | Prioritas |
|---|---|---|---|---|
| F-01 | IL01, DS02 | Mengenali alas & tinggi pada berbagai bentuk segitiga | **Segitiga Interaktif** (SVG): titik sudut dapat digeser; alas biru, tinggi oranye putus-putus; pilih sisi mana pun sebagai alas dan tinggi menyesuaikan | Wajib |
| F-02 | IL01 | Latihan menunjuk alas & tinggi | Mini-game **"Tunjuk Tingginya"**: siswa mengetuk garis yang merupakan tinggi | Wajib |
| F-03 | IL02, IL04 | Urutan langkah penyelesaian | **Panduan 4 langkah** tetap: Diketahui → Ditanyakan → Rumus → Hitung (+ Simpulkan) | Wajib |
| F-04 | IL03 | Prasyarat operasi hitung | Tombol **"Ingat lagi"** berisi pengingat singkat perkalian/pembagian/pecahan/desimal, muncul bila terdeteksi salah hitung | Sedang |
| F-05 | IL04, EL05 | Memilah informasi soal cerita | Mini-game **"Pilah Informasi"**: seret angka ke kotak Diketahui / Ditanyakan / Tidak dipakai | Wajib |
| F-06 | EL01, EL04 | Soal panjang & tempo | Soal dipecah per kalimat; **satu langkah per layar**; tombol **Ulangi** dan **Lanjut**; tanpa timer di mode belajar | Wajib |
| F-07 | EL02, GL01 | Gambar dekat teks | Setiap soal/langkah menampilkan gambar segitiga dengan label langsung pada gambar | Wajib |
| F-08 | EL03, DS03 | Tampilan tidak ramai | Palet warna terbatas, animasi hanya yang menjelaskan konsep, mode kurangi gerak | Wajib |
| F-09 | GL01, DS01 | Contoh langkah demi langkah | **Contoh soal bertahap** dengan pola *worked example → completion → mandiri* (fading) | Wajib |
| F-10 | GL02 | Mengecek ulang | Tombol **"Cek langkahku"** sebelum kirim + pertanyaan refleksi "Apakah rumusmu sesuai?" | Sedang |
| F-11 | GL03 | Petunjuk bertahap | **Petunjuk 3 tingkat** per langkah (arah → rumus → cara lengkap) | Wajib |
| F-12 | GL04 | Elaborasi | Kotak **"Jelaskan ke temanmu"** di akhir misi (jawaban bebas, disimpan untuk guru) | Sedang |
| F-13 | GL05 | Transfer ke konteks baru | **Generator variasi soal** (Python): struktur sama, cerita & angka berbeda | Sedang |
| F-14 | DS02, IL05 | Tahu bagian yang salah | **Diagnosis kesalahan** per langkah (lupa ½, salah tinggi, salah satuan, salah operasi) | Wajib |
| F-15 | Kisi-kisi | Mengukur literasi matematika | **Game "Misi Segitiga"** 4 misi sesuai indikator kisi-kisi dengan rubrik skor per tahapan | Wajib |
| F-16 | — | Laporan | **Laporan hasil** untuk siswa; rekap per kelas untuk guru | Sedang |

## 4. Kebutuhan non-fungsional

| Kode | Kebutuhan |
|---|---|
| NF-01 | Responsif: nyaman di layar 360 px (HP) sampai 1440 px (laptop) |
| NF-02 | Ringan: halaman pertama < 300 KB, tanpa framework JS |
| NF-03 | Bisa dijalankan di laptop guru dan diakses HP siswa lewat Wi-Fi yang sama (tanpa internet) |
| NF-04 | Data pribadi minimal: nama panggilan + kode kelas |
| NF-05 | Aksesibel: kontras cukup, makna tidak hanya dari warna (tinggi juga putus-putus + label), target sentuh ≥ 44 px |
| NF-06 | Bahasa Indonesia sederhana, kalimat pendek |

## 5. Keterbatasan data

- Hanya **satu informan (S01)**; temuan perlu dikonfirmasi pada uji coba dengan lebih banyak siswa (lihat [05-rencana-pengujian.md](05-rencana-pengujian.md)).
- Respons **tugas pemicu tidak tercatat** dalam laporan wawancara, sehingga diagnosis kesalahan disusun dari pernyataan siswa (IL01, IL05) dan kesalahan umum yang dikenal pada materi luas segitiga.
