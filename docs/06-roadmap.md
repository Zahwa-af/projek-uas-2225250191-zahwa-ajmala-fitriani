# 06 — Roadmap Pengerjaan

Tandai `[x]` setiap tugas yang selesai. ID fitur (F-xx) merujuk ke [01-analisis-kebutuhan.md](01-analisis-kebutuhan.md).

## Tahap 0 — Perencanaan ✅
- [x] Analisis kebutuhan dari wawancara S01
- [x] Kisi-kisi soal mathematical literacy (4 indikator)
- [x] Dokumen CLAUDE.md, README.md, desain, arsitektur, game, pengujian, roadmap
- [ ] Konfirmasi keputusan terbuka (lihat bagian bawah) dengan dosen

## Tahap 1 — Fondasi Python (logika murni) ✅
- [x] `requirements.txt`, `pyproject.toml`, struktur folder, virtualenv
- [x] `segitiga/parser_angka.py` + test (format angka Indonesia, pecahan, Rp, satuan)
- [x] `segitiga/rumus.py` + test
- [x] `data/soal/misi.json` — 4 misi kisi-kisi lengkap (kunci, petunjuk 3 tingkat, pengecoh, umpan balik per opsi)
- [x] `segitiga/bank_soal.py` — memuat, memvalidasi, menyaring field rahasia
- [x] `segitiga/penilai.py` + test (pilihan, angka, rumus, pilah; skor rubrik; bintang; kategori)
- [x] `segitiga/diagnosis.py` + test (F-14)

## Tahap 2 — API Flask & database ✅
- [x] `db.py` skema SQLite
- [x] `app.py` + route sesi, misi, periksa, petunjuk, selesai, refleksi, progres, latihan, guru
- [x] `test_api.py` — kunci jawaban tidak bocor, alur misi penuh, 3× salah → petunjuk otomatis
- [x] Server di `0.0.0.0`, alamat untuk HP dicetak saat start

## Tahap 3 — Kerangka frontend (JavaScript) ✅
- [x] `index.html`, `tokens.css`, `dasar.css`, `komponen.css` (mobile-first, mode gelap)
- [x] `main.js` router hash, `api.js`, `state.js`, `dom.js`
- [x] Halaman Beranda (nama panggilan + kode kelas)
- [x] Komponen `segitiga-svg.js` + `geometri.js`

## Tahap 4 — Game Misi Segitiga (F-15) ✅
- [x] Komponen isian (`langkah.js`): `pilihan`, `angka`, `rumus`, `pilah`
- [x] `pilah-info.js` (ketuk-lalu-taruh + seret, sentuh & mouse)
- [x] Petunjuk 3 tingkat (F-11) & umpan balik diagnosis
- [x] Daftar misi (terbuka berurutan) + alur Misi 1–4, cerita per kalimat
- [x] Ringkasan langkah, "Jelaskan ke temanmu" (F-12), skor ⭐ & lencana
- [x] Halaman Hasilku (F-16)

## Tahap 5 — Materi Belajar & Latihan (sebagian besar ✅)
- [x] Segitiga interaktif dapat digeser + pilih alas AB/BC/CA (F-01)
- [x] Materi 5 topik, satu konsep per layar, Kembali/Ulangi/Lanjut (F-06, F-07)
- [x] Animasi konsep: tinggi turun tegak lurus; segitiga = ½ persegi panjang
- [x] Mini-game Tunjuk Tingginya (F-02) — lancip, siku-siku, tumpul
- [x] Mini-game Pilah Informasi (F-05) — 3 soal dengan angka pengecoh
- [x] Contoh bertahap soal cerita (F-09) + fading: Soal Cerita Bertahap tingkat 1–4 (Tahap 2C)
- [x] Panel "Ingat lagi" operasi hitung, muncul saat salah hitung (F-04)
- [ ] Tombol "Cek langkahku" (F-10)

## Tahap 6 — Variasi & guru
- [ ] `generator_soal.py`: variasi 4 misi (F-13) — saat ini baru generator Tunjuk Tingginya
- [ ] Mode Latihan Ulang
- [x] Rekap guru per kode kelas (PIN lewat `SEGIPINTAR_PIN_GURU`)
- [x] `manifest.webmanifest` (pasang di layar utama HP)

## Tahap 7 — Pengujian & uji coba
- [x] Uji otomatis: 134 tes pytest lulus; ruff & black bersih
- [x] Uji browser headless (HP 360 px & laptop 1280 px, mode gelap): tanpa galat JS, tanpa scroll horizontal
- [ ] Checklist A2 di HP sungguhan (Android) lewat Wi-Fi
- [ ] Uji coba dengan 5–10 siswa
- [ ] Analisis data (skor, petunjuk, diagnosis, angket)
- [ ] Revisi berdasarkan temuan

## Tahap 8 — Integrasi RMT (rincian: [13-rencana-implementasi-tahap2.md](13-rencana-implementasi-tahap2.md))
- [x] Tahap 1 — fondasi RMT (pemetaan tahap & fase kesalahan, log pembimbing)
- [x] Tahap 2A — backend aktivitas RMT: `rmt_misi.json`, `aktivitas_rmt.py`, `/api/rmt/*`, tabel `aktivitas_rmt`
- [x] Tahap 2B — frontend: tujuan & makna, Tebak dulu, Susun rencana, Tata informasi, Cek hasil, Di mana lagi?, refleksi dengan kalimat pembuka; semua bisa dilewati, skor tetap 6/6
- [x] Tahap 2C — Cognitive Load: Soal Cerita Bertahap (fading), remedial adaptif dari diagnosis aplikasi, layar Bandingkan keliling–luas, panel Pembimbing tertutup bawaan ([14-cognitive-load-tahap2c.md](14-cognitive-load-tahap2c.md)). Setara rencana 2G di dokumen 13; rencana 2C–2E lama sudah tercakup di 2B. ⚠️ Belum berdasarkan hasil uji coba instrumen.
- [x] Tahap 2F — chatbot misi dengan mediasi RMT: tingkat bantuan 0–3 dari server, fokus tahap/fase, prinsip MLE; jawaban akhir tetap tidak disebut ([15-status-tahap2.md](15-status-tahap2.md))
- [x] Perbaikan audit: HP bersama, refleksi disamarkan, rate limit endpoint baru, remedial percobaan terakhir, `web-statis`
- [ ] Uji langsung oleh mahasiswa: chatbot dengan model sungguhan, HP sungguhan, halaman guru ([15](15-status-tahap2.md) §5)

## Keputusan terbuka (perlu dikonfirmasi)
1. **Skor & petunjuk:** apakah petunjuk tingkat 2 mengurangi skor rubrik? (Implementasi saat ini: tidak; hanya tingkat 3 yang membuat skor tahap 0.)
2. **Urutan misi:** saat ini terbuka berurutan. Guru bisa membuka semua dengan `SEGIPINTAR_MISI_BEBAS=1`.
3. **Misi 4 tahap 6:** kunci dipakai "Kain minimal 1,8 m² sudah cukup, jadi 3,6 m² berlebih" — sesuaikan bila dosen ingin rumusan lain.
4. **Nama aplikasi:** "SegiPintar" adalah nama sementara.
5. **Kategori di Hasilku** dihitung dari total 24 walau baru sebagian misi selesai.
