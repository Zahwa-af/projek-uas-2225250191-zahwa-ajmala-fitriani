# 03 — Arsitektur Teknis (Python + JavaScript)

## 1. Gambaran umum

```
 ┌──────────────── Browser (HP / laptop) ────────────────┐
 │  HTML + CSS + JavaScript (ES modules)                 │
 │  • gambar segitiga SVG interaktif                     │
 │  • alur langkah, petunjuk, drag-and-drop              │
 │  • progres sementara di localStorage                  │
 └───────────────┬───────────────────────────────────────┘
                 │  fetch() JSON  (/api/...)
 ┌───────────────▼───────────────────────────────────────┐
 │  Python 3.11 + Flask   (backend/app.py)               │
 │  • menyajikan file frontend                           │
 │  • REST API                                           │
 │        │                                              │
 │  ┌─────▼──────── backend/segitiga/ (logika murni) ──┐ │
 │  │ rumus · parser_angka · penilai · diagnosis ·     │ │
 │  │ generator_soal · bank_soal                       │ │
 │  └──────────────────────────────────────────────────┘ │
 │        │                                              │
 │  SQLite (backend/data/segipintar.db)                  │
 └───────────────────────────────────────────────────────┘
```

## 2. Pembagian peran Python vs JavaScript

| Tugas | Python | JavaScript |
|---|:-:|:-:|
| Menyimpan bank soal & kunci jawaban | ✔ | |
| Memeriksa jawaban per langkah | ✔ | |
| Mendiagnosis jenis kesalahan (lupa ½, salah tinggi, dll.) | ✔ | |
| Menghitung skor rubrik per tahapan | ✔ | |
| Membuat variasi soal (angka & konteks acak) | ✔ | |
| Menyimpan progres & skor (SQLite) | ✔ | |
| Rekap untuk guru | ✔ | |
| Menggambar segitiga SVG & menghitung posisi garis tinggi | | ✔ |
| Menggeser titik sudut (pointer events) | | ✔ |
| Drag-and-drop "Pilah Informasi" | | ✔ |
| Navigasi langkah, tombol Ulangi/Lanjut, membuka petunjuk | | ✔ |
| Menyimpan progres sementara (offline sesaat) | | ✔ |

**Alasan:** kunci jawaban tidak dikirim ke browser, sehingga siswa tidak bisa "mengintip" lewat DevTools, dan logika penilaian cukup diuji sekali dengan pytest.

**Catatan geometri:** perhitungan *posisi* kaki garis tinggi untuk gambar dilakukan di JS (proyeksi titik ke garis) karena dibutuhkan setiap kali titik digeser. Rumus luas/keliling untuk *penilaian* tetap di Python.

## 3. Struktur folder

```
projek uas awa/
├── CLAUDE.md
├── README.md
├── requirements.txt              flask, pytest, ruff, black
├── docs/
├── backend/
│   ├── app.py                    Flask app + registrasi route
│   ├── api/
│   │   ├── umum.py               koneksi DB, galat API, status langkah
│   │   ├── routes_soal.py        /api/misi, /api/latihan
│   │   ├── routes_periksa.py     /api/periksa, /api/petunjuk
│   │   ├── routes_progres.py     /api/sesi, /api/progres, /api/remedial, /api/guru
│   │   ├── routes_rmt.py         /api/rmt/* (aktivitas RMT, tanpa skor) — Tahap 2A
│   │   ├── routes_asisten.py     /api/asisten/* (Pembimbing AI beranda & misi)
│   │   └── keamanan.py           batas laju per IP, header keamanan, kunci PIN
│   ├── asisten/                  klien OpenRouter/DeepSeek, prompt, mediasi RMT, pengaman, anonim
│   ├── segitiga/                 ← TIDAK boleh impor Flask
│   │   ├── rumus.py              luas(), keliling(), jenis_segitiga()
│   │   ├── parser_angka.py       "1.200" → 1200, "1,8" → 1.8, "Rp300.000" → 300000
│   │   ├── penilai.py            periksa_langkah(), hitung_skor_rubrik()
│   │   ├── diagnosis.py          deteksi pola kesalahan umum
│   │   ├── generator_soal.py     variasi soal dengan struktur sama
│   │   ├── rmt.py                label tahap RMT & fase kesalahan (Tahap 1)
│   │   ├── aktivitas_rmt.py      konten & pemeriksa aktivitas RMT (Tahap 2A)
│   │   ├── fading.py             Soal Cerita Bertahap + aturan fading (Tahap 2C)
│   │   ├── remedial.py           saran penguatan dari kesalahan siswa (Tahap 2C)
│   │   └── bank_soal.py          memuat & memvalidasi data/soal/*.json
│   ├── data/
│   │   ├── soal/
│   │   │   ├── misi.json         4 misi kisi-kisi
│   │   │   ├── latihan.json      soal latihan & contoh bertahap
│   │   │   ├── rmt_misi.json     konten aktivitas RMT 4 misi (tanpa skor)
│   │   │   └── konteks.json      cerita untuk generator variasi
│   │   └── segipintar.db         (dibuat otomatis, tidak di-commit)
│   ├── db.py                     koneksi & skema SQLite
│   └── tests/
│       ├── test_parser_angka.py
│       ├── test_rumus.py
│       ├── test_penilai.py
│       ├── test_diagnosis.py
│       └── test_api.py
└── frontend/
    ├── index.html                kerangka SPA sederhana
    ├── manifest.webmanifest      agar bisa "Tambah ke layar utama" di HP
    ├── css/
    │   ├── tokens.css            warna, ukuran (lihat 02-desain.md)
    │   ├── dasar.css
    │   └── komponen.css
    └── js/
        ├── main.js               router berbasis hash (#/belajar, #/misi/2)
        ├── api.js                semua fetch ke backend
        ├── dom.js                pembuat elemen aman (textContent), tombol, kotak umpan balik
        ├── state.js              progres + localStorage (try/catch)
        ├── segitiga-svg.js       komponen gambar segitiga (statis & interaktif)
        ├── geometri.js           proyeksi titik, jarak, sudut (untuk menggambar)
        ├── langkah.js            Kartu Langkah + petunjuk + umpan balik
        ├── pilah-info.js         drag-and-drop Diketahui/Ditanyakan
        ├── aktivitas-rmt.js      tampilan aktivitas RMT
        ├── urutkan.js            komponen urutkan kartu (tombol ↑/↓)
        ├── remedial.js           kartu saran penguatan
        ├── halaman/
        │   ├── beranda.js
        │   ├── belajar.js
        │   ├── latihan.js
        │   ├── misi.js           + layar RMT, panel Pembimbing (tertutup bawaan)
        │   ├── latihan-bertahap.js  Soal Cerita Bertahap (fading)
        │   ├── hasil.js
        │   └── guru.js
        └── teks.js               semua kalimat UI (mudah diedit tanpa menyentuh logika)
```

## 4. API

Semua respons JSON. Prefix `/api`.

| Method | Endpoint | Fungsi |
|---|---|---|
| POST | `/api/sesi` | Mulai sesi: `{nama_panggilan, kode_kelas}` → `{sesi_id}` |
| GET | `/api/sesi/<sesi_id>` | Cek sesi masih ada |
| GET | `/api/misi?sesi_id=` | Daftar 4 misi + status (terbuka/selesai, skor terbaik, ⭐) |
| GET | `/api/misi/<id>` | Isi misi **tanpa kunci jawaban**: cerita, gambar, daftar langkah |
| POST | `/api/misi/<id>/mulai` | `{sesi_id}` → `{main_id}` (satu kali main) |
| POST | `/api/periksa` | `{main_id, langkah, jawaban}` → hasil + diagnosis (lihat contoh) |
| POST | `/api/petunjuk` | `{main_id, langkah}` → petunjuk tingkat berikutnya (server yang menentukan tingkat) |
| POST | `/api/misi/selesai` | `{main_id}` → skor rubrik, rincian per tahap, ⭐, lencana, ringkasan |
| POST | `/api/refleksi` | `{main_id, teks}` simpan "Jelaskan ke temanmu" |
| GET | `/api/progres/<sesi_id>` | Skor terbaik per misi, total, kategori, lencana |
| GET | `/api/latihan/pilah` · POST `/api/latihan/pilah/periksa` | Latihan Pilah Informasi |
| GET | `/api/latihan/tinggi` · POST `/api/latihan/tinggi/periksa` | Latihan Tunjuk Tingginya (soal dibuat ulang dari `seed`) |
| POST | `/api/guru` | `{kode_kelas, pin}` → rekap kelas |

### API Tahap 2 (RMT dan Cognitive Load)

| Metode | Jalur | Fungsi |
|---|---|---|
| GET | `/api/rmt/misi/<id>` | Konten aktivitas RMT satu misi **tanpa kunci** (tujuan, makna, 6 aktivitas) |
| POST | `/api/rmt/respons` | `{main_id, aktivitas, jawaban}` atau `{…, dilewati: true}` → umpan balik; disimpan di `aktivitas_rmt` dengan kode anonim. Maks. 50 percobaan per aktivitas per main misi. |
| GET | `/api/latihan/bertahap?tingkat=` | Soal Cerita Bertahap tingkat 1–4 (tanpa kunci) |
| POST | `/api/latihan/bertahap/periksa` · `/petunjuk` · `/selesai` | Periksa isian, petunjuk 1–3, keputusan tingkat berikutnya (fading). Tidak disimpan. |
| GET | `/api/remedial/<sesi_id>[?main_id=]` | Saran penguatan dari kesalahan siswa sendiri (hanya membaca). Tanpa `main_id`: percobaan terakhir tiap misi. |
| POST | `/api/asisten/pesan` | Chatbot misi; sejak Tahap 2F memakai mediasi RMT dan `tingkat_bantuan` 0–3 dari server |

Batas laju per IP: `/api/asisten/` (30/10 menit), `/api/sesi` (30/jam), POST `/api/rmt/` dan `/api/latihan/` (900/10 menit, longgar karena satu kelas bisa berbagi IP). `/api/periksa` sengaja tidak dibatasi agar alur berskor tidak pernah terblokir.

Status percobaan dan petunjuk disimpan **di server** (bukan dipercaya dari browser): 3 kali salah otomatis membuka petunjuk tingkat 3; jawaban kosong/tidak terbaca tidak dihitung sebagai percobaan.

### Contoh `/api/periksa`

Permintaan:
```json
{
  "main_id": "9f2c41d0a7b3e815",
  "langkah": "3",
  "jawaban": { "nilai": "3,6", "satuan": "m²" }
}
```

Respons:
```json
{
  "benar": false,
  "kode_diagnosis": "LUPA_SETENGAH",
  "umpan_balik": "Itu sama dengan hasil Dika. Jangan lupa dikali ½.",
  "boleh_lanjut": false,
  "tingkat_petunjuk": 0,
  "petunjuk_baru": []
}
```

## 5. Skema database (SQLite)

> Skema di bawah adalah **rancangan awal**. Skema yang berlaku ada di [backend/db.py](../backend/db.py): tabel `sesi`, `main_misi`, `jawaban_langkah`, `petunjuk_dibuka`, `refleksi`, `percakapan_asisten`, `percakapan_beranda`, dan `aktivitas_rmt` (Tahap 2A). Tahap 2C dan 2F tidak menambah tabel.

```sql
CREATE TABLE sesi (
  id            TEXT PRIMARY KEY,         -- uuid4 pendek
  nama_panggilan TEXT NOT NULL,
  kode_kelas    TEXT NOT NULL,
  dibuat        TEXT NOT NULL             -- ISO 8601
);

CREATE TABLE jawaban_langkah (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  sesi_id       TEXT NOT NULL REFERENCES sesi(id),
  misi_id       INTEGER NOT NULL,
  langkah       INTEGER NOT NULL,
  percobaan_ke  INTEGER NOT NULL,
  jawaban       TEXT NOT NULL,            -- JSON mentah dari siswa
  benar         INTEGER NOT NULL,         -- 0/1
  kode_diagnosis TEXT,
  tingkat_petunjuk INTEGER NOT NULL DEFAULT 0,
  waktu         TEXT NOT NULL
);

CREATE TABLE skor_misi (
  sesi_id       TEXT NOT NULL REFERENCES sesi(id),
  misi_id       INTEGER NOT NULL,
  skor_rubrik   INTEGER NOT NULL,         -- 0..6
  rincian       TEXT NOT NULL,            -- JSON skor per tahapan
  bintang       INTEGER NOT NULL,         -- 0..3
  PRIMARY KEY (sesi_id, misi_id)
);

CREATE TABLE refleksi (
  sesi_id TEXT, misi_id INTEGER, teks TEXT, waktu TEXT
);
```

Data `jawaban_langkah` dan `tingkat_petunjuk` sekaligus menjadi **data penelitian** untuk uji coba (berapa banyak bantuan yang dibutuhkan siswa — sesuai "cara menguji fitur" pada laporan wawancara).

## 6. Modul Python inti (rancangan fungsi)

```python
# segitiga/rumus.py
def luas_segitiga(alas: float, tinggi: float) -> float: ...
def keliling_segitiga(a: float, b: float, c: float) -> float: ...
def jenis_menurut_sisi(a, b, c) -> str: ...      # "sama sisi" | "sama kaki" | "sembarang"
def jenis_menurut_sudut(a, b, c) -> str: ...     # "lancip" | "siku-siku" | "tumpul"

# segitiga/parser_angka.py
def parse_angka(teks: str) -> float | None: ...   # format Indonesia, pecahan, "Rp"
def parse_satuan(teks: str) -> str | None: ...    # "cm2"/"cm²" → "cm²"

# segitiga/penilai.py
def periksa_langkah(definisi_langkah: dict, jawaban: dict) -> HasilPeriksa: ...
def hitung_skor_rubrik(riwayat: list[HasilPeriksa], rubrik: dict) -> SkorMisi: ...

# segitiga/diagnosis.py
def diagnosis_luas(jawaban: float, alas: float, tinggi: float, sisi_lain: list[float]) -> str | None: ...

# segitiga/generator_soal.py
def buat_variasi(misi_id: int, seed: int | None = None) -> dict: ...
```

## 7. Akses dari HP tanpa internet (NF-03)

Server Flask dijalankan dengan `host="0.0.0.0"` di laptop guru. HP siswa yang tersambung ke Wi-Fi/hotspot yang sama membuka `http://<IP-laptop>:5000`. Ini menghindari masalah kuota dan sinyal di kelas.

Pilihan deploy online (opsional, setelah UAS): PythonAnywhere atau Render (paket gratis).

## 8. Keamanan & privasi

- Tidak ada password siswa; sesi diidentifikasi `sesi_id` acak yang disimpan di `localStorage`. Siapa pun yang tahu `sesi_id` dapat membaca progres sesi itu, jadi `sesi_id` siswa lain tidak boleh tertinggal di perangkat: "Ganti nama" menghapus sesi dan data tingkat latihan.
- Teks bebas siswa (refleksi, respons RMT, pesan chatbot) disamarkan sebelum disimpan: nama panggilan, email, dan nomor HP diganti penanda.
- Halaman guru dilindungi PIN yang diatur lewat variabel lingkungan `SEGIPINTAR_PIN_GURU`.
- Semua input siswa diperlakukan sebagai teks; ditampilkan dengan `textContent` (bukan `innerHTML`) untuk mencegah XSS.
- Query SQLite selalu memakai parameter (`?`), tidak pernah f-string.
