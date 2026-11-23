# SegiPintar — Belajar Segitiga Tanpa Beban Berlebih

Aplikasi web pembelajaran **bangun datar segitiga** untuk siswa SMP yang dapat dibuka di **smartphone maupun browser laptop**.
Aplikasi dirancang berdasarkan **Cognitive Load Theory** agar siswa tidak kewalahan, sehingga energi berpikirnya dipakai untuk memahami konsep dan menyelesaikan soal **mathematical literacy**.

> Proyek UAS — Mata Kuliah Algoritma dan Pemrograman, S1 Pendidikan Matematika.

## Latar belakang

Wawancara analisis kebutuhan dengan siswa kelas VIII (kode S01, 5 November 2026) menemukan bahwa siswa:

- masih **bingung menentukan alas dan tinggi** saat menghitung luas (IL01);
- **kesulitan pada soal cerita**, terutama memilah angka mana yang dipakai (IL04, EL05);
- lebih mudah paham dengan **gambar** daripada teks saja (EL02);
- **terganggu oleh warna dan animasi yang ramai** (EL03);
- ingin **petunjuk satu per satu**, bukan langsung jawaban (GL03);
- ingin aplikasi yang **tahu bagian mana yang salah** (DS02).

Rincian lengkap ada di [docs/01-analisis-kebutuhan.md](docs/01-analisis-kebutuhan.md).

## Fitur utama

| Fitur | Masalah yang diatasi |
|---|---|
| **Segitiga Interaktif** — geser titik sudut, lihat alas (biru) dan tinggi (oranye) berubah | Menentukan alas & tinggi (IL01) |
| **Materi bertahap** — jenis segitiga, keliling, luas; satu konsep per layar dengan tombol Ulangi/Lanjut | Penjelasan terlalu cepat, teks panjang (EL01, EL04) |
| **Contoh soal langkah demi langkah** yang perlahan "dipudarkan" (worked example → fading) | Membangun skema penyelesaian (GL01) |
| **Pilah Informasi** — seret angka ke kotak *Diketahui / Ditanyakan / Tidak dipakai* | Soal cerita membingungkan (EL05) |
| **Game "Misi Segitiga"** — 4 misi literasi matematika sesuai kisi-kisi | Mengukur & melatih mathematical literacy |
| **Petunjuk 3 tingkat** dan **umpan balik per langkah** | Scaffolding & menunjuk letak kesalahan (GL03, DS02) |
| **Laporan hasil** dengan skor rubrik per tahapan | Evaluasi siswa & guru |
| **Aktivitas RMT** di setiap misi (tanpa skor): tujuan, Tebak dulu, Susun rencana, Tata informasi, Cek hasil, Di mana lagi?, refleksi terpandu | Rigorous Mathematical Thinking |
| **Soal Cerita Bertahap** — bantuan berkurang 4 tingkat (fading), naik/turun sesuai hasil siswa | Germane load, transisi dari contoh ke mandiri (GL01, GL03) |
| **Saran remedial** dari kesalahan siswa sendiri, dengan tautan ke materi/latihan | Tahu bagian mana yang salah (DS02, IL05) |
| **Pembimbing AI** (OpenRouter/DeepSeek): beranda menjawab langsung; di misi membimbing bertahap sesuai tahap RMT tanpa menyebut jawaban | Bantuan sesuai kesulitan |

## Teknologi

| Lapisan | Teknologi | Peran |
|---|---|---|
| Backend | **Python 3.11+**, Flask | API, penilaian jawaban, diagnosis kesalahan, generator variasi soal, penyimpanan progres |
| Frontend | **JavaScript** (vanilla ES modules), HTML, CSS | Tampilan, gambar segitiga SVG interaktif, alur game, drag-and-drop |
| Database | SQLite | Menyimpan progres dan skor |
| Pengujian | pytest (Python), uji manual + checklist (JS) | Menjamin penilaian benar |

Penjelasan arsitektur: [docs/03-arsitektur.md](docs/03-arsitektur.md).

## Cara menjalankan (setelah tahap coding)

```bash
# 1. Siapkan lingkungan Python
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# 2. Jalankan server
python backend/app.py

# 3. Buka di browser laptop
#    http://localhost:5000
# 4. Buka di HP (HP dan laptop harus di Wi-Fi yang sama)
#    http://<IP-laptop>:5000      contoh: http://192.168.1.10:5000
```

## Chatbot "Tanya Pembimbing" (DeepSeek) — tahap backend

Kode ada di `backend/asisten/` dan `backend/api/routes_asisten.py`. Endpoint: `GET /api/asisten/status`, `POST /api/asisten/pesan`. Panel di halaman Misi **belum dibuat**.

- API key **hanya** dibaca server dari `.env` (lokal) atau Environment Variables (Vercel). File `.env` diabaikan git.
- Mode lewat `SEGIPINTAR_ASISTEN`: `deepseek` | `tiruan` (tanpa internet, untuk mencoba) | `mati`.
- Ke DeepSeek tidak dikirim nama, sesi, atau kode siswa. Nama, email, dan nomor di pertanyaan siswa disamarkan dulu.
- Percakapan dicatat di tabel `percakapan_asisten` dengan kode anonim. Chatbot tidak mengubah skor.
- Tes memakai klien tiruan dan tidak pernah memanggil API sungguhan.

Cara mengaktifkan di laptop: salin `.env.example` menjadi `.env`, isi `DEEPSEEK_API_KEY` dan `SEGIPINTAR_RAHASIA_ANONIM`, lalu jalankan ulang `python backend/app.py`.

## Versi online (tanpa server)

Folder [web-statis/](web-statis/) berisi versi yang berjalan sepenuhnya di browser, sehingga bisa dibuka lewat link di HP tanpa laptop menyala. Tampilannya memakai `frontend/` yang sama. Hanya `js/api.js` yang diganti dengan "server mini" di browser (`web-statis/js/lokal/`), dan bank soal tetap dari `backend/data/soal/`.

- Logika penilaian di `web-statis/js/lokal/` adalah terjemahan JavaScript dari `backend/segitiga/`. Python tetap sumber utamanya.
- Setiap kali logika Python diubah, jalankan uji kesetaraan:
  `python web-statis/uji_kesetaraan.py | node web-statis/uji_kesetaraan.mjs`
- Progres siswa tersimpan di HP masing-masing (localStorage). Rekap guru hanya ada di versi server.

## Struktur folder (rencana)

```
projek uas awa/
├── CLAUDE.md                 Aturan kerja untuk Claude Code
├── README.md                 File ini
├── requirements.txt          Dependensi Python
├── docs/                     Dokumen perencanaan
├── backend/                  Kode Python (Flask + logika matematika)
│   ├── app.py
│   ├── segitiga/             Logika murni: rumus, parser angka, penilai, diagnosis, generator soal
│   ├── data/                 Bank soal (JSON) dan database SQLite
│   └── tests/                Unit test pytest
└── frontend/                 Kode JavaScript, HTML, CSS
    ├── index.html
    ├── css/
    └── js/
```

## Dokumen perencanaan

1. [Analisis Kebutuhan](docs/01-analisis-kebutuhan.md)
2. [Desain UI/UX](docs/02-desain.md)
3. [Arsitektur Teknis](docs/03-arsitektur.md)
4. [Game & Bank Soal](docs/04-game-dan-soal.md)
5. [Rencana Pengujian](docs/05-rencana-pengujian.md)
6. [Roadmap](docs/06-roadmap.md)
7. [Analisis RMT](docs/07-analisis-rmt.md)
8. [Checklist Dokumen Penelitian](docs/09-checklist-dokumen-penelitian.md)
9. [Audit Mathematical Literacy](docs/10-audit-mathematical-literacy.md)
10. [Audit RMT](docs/12-audit-rmt.md)
11. [Rencana Implementasi Tahap 2](docs/13-rencana-implementasi-tahap2.md)
12. [Cognitive Load Tahap 2C](docs/14-cognitive-load-tahap2c.md)
13. [Status Tahap 2 dan hasil pengujian](docs/15-status-tahap2.md)

## Penyusun

Zahwa Ajmala Fitriani — NIM 2225250191 — Kelas 3B
