# CLAUDE.md — Panduan Kerja untuk Claude Code

File ini dibaca oleh Claude Code setiap sesi. Isinya aturan **yang wajib diikuti** saat menulis kode untuk proyek ini.

## Ringkasan proyek

**SegiPintar** adalah aplikasi web (dibuka di smartphone dan browser) untuk belajar **bangun datar segitiga** (kelas VII–VIII SMP).
Tujuannya **mengurangi beban kognitif (cognitive load)** siswa supaya kemampuan **mathematical literacy** mereka meningkat.
Desain didasarkan pada wawancara analisis kebutuhan dengan siswa S01 (lihat [docs/01-analisis-kebutuhan.md](docs/01-analisis-kebutuhan.md)).

- **Backend:** Python 3.11+ dengan Flask. Semua logika penilaian, diagnosis kesalahan, dan pembuatan variasi soal ada di Python.
- **Frontend:** HTML + CSS + **JavaScript murni (vanilla, ES modules)**, tanpa framework dan tanpa build step.
- **Database:** SQLite (file lokal), diakses lewat modul `sqlite3` bawaan Python.
- **Bahasa antarmuka:** Bahasa Indonesia yang sederhana dan ramah siswa SMP.

## Dokumen perencanaan (baca sebelum mengerjakan fitur)

| Dokumen | Isi |
|---|---|
| [README.md](README.md) | Gambaran umum, cara menjalankan |
| [docs/01-analisis-kebutuhan.md](docs/01-analisis-kebutuhan.md) | Temuan wawancara → kebutuhan fitur (kode IL/EL/GL/DS) |
| [docs/02-desain.md](docs/02-desain.md) | Prinsip desain UI/UX berbasis Cognitive Load Theory |
| [docs/03-arsitektur.md](docs/03-arsitektur.md) | Struktur folder, pembagian tugas Python vs JavaScript, API, database |
| [docs/04-game-dan-soal.md](docs/04-game-dan-soal.md) | Desain game "Misi Segitiga", 4 soal kisi-kisi, rubrik, diagnosis kesalahan |
| [docs/05-rencana-pengujian.md](docs/05-rencana-pengujian.md) | Pengujian otomatis dan uji coba dengan siswa |
| [docs/06-roadmap.md](docs/06-roadmap.md) | Tahapan pengerjaan dan checklist |

## Aturan desain yang TIDAK boleh dilanggar

Aturan ini berasal langsung dari wawancara siswa. Setiap pelanggaran menambah beban kognitif yang tidak perlu (extraneous load).

1. **Satu langkah per layar.** Jangan menampilkan seluruh soal + seluruh langkah sekaligus. (IL02, EL01)
2. **Gambar selalu dekat dengan teks yang menjelaskannya.** Label alas/tinggi ditulis langsung pada gambar, bukan di legenda terpisah. (EL02, GL01)
3. **Warna terbatas.** Hanya pakai token warna di `frontend/css/tokens.css`. Jangan menambah warna baru tanpa memperbarui [docs/02-desain.md](docs/02-desain.md). (EL03, DS03)
4. **Warna konsisten untuk makna yang sama:** alas = biru, tinggi = oranye (garis putus-putus), sisi lain = abu-abu. Jangan pernah dipertukarkan.
5. **Animasi hanya jika menjelaskan materi** (misalnya garis tinggi "jatuh" tegak lurus ke alas). Tidak ada animasi dekoratif, confetti, latar bergerak, atau maskot beranimasi. Hormati `prefers-reduced-motion`. (EL03, DS03)
6. **Siswa yang mengatur tempo.** Tidak ada auto-advance dan tidak ada timer di mode belajar. Selalu sediakan tombol **Ulangi** dan **Lanjut**. (EL04)
7. **Petunjuk bertahap, bukan jawaban langsung.** Petunjuk level 1 → 2 → 3; jawaban lengkap hanya di level terakhir dan selalu disertai cara penyelesaiannya. (GL03)
8. **Umpan balik harus menunjuk bagian yang salah** (langkah mana, dan kemungkinan penyebabnya), bukan hanya "Salah". (DS02, IL05)
9. **Teks pendek.** Paragraf maksimal ±3 kalimat; satu instruksi per kalimat.

## Aturan kode

### Pembagian tanggung jawab
- **Python = sumber kebenaran.** Kunci jawaban, rubrik skor, toleransi angka, dan diagnosis kesalahan **hanya** ada di backend. Jangan pernah mengirim kunci jawaban ke browser sebelum siswa menjawab atau meminta petunjuk level 3.
- **JavaScript = tampilan dan interaksi.** Menggambar segitiga (SVG), navigasi antar-langkah, drag-and-drop, memanggil API, menyimpan progres sementara di `localStorage`.

### Python
- Format kode: `black` + `ruff`. Type hints di semua fungsi publik.
- Nama variabel/fungsi domain boleh Bahasa Indonesia agar dekat dengan istilah matematika (`luas_segitiga`, `alas`, `tinggi`), tetapi konsisten dalam satu modul.
- Logika matematika murni (di `backend/segitiga/`) **tidak boleh** mengimpor Flask — supaya mudah diuji dengan `pytest`.
- Setiap fungsi penilai/diagnosis wajib punya unit test, termasuk kasus kesalahan umum (lupa ½, salah pilih tinggi, salah satuan).

### JavaScript
- ES modules (`<script type="module">`), tanpa jQuery, tanpa framework, tanpa bundler.
- Semua gambar segitiga dibuat dengan **SVG** (bukan `<canvas>`) agar tajam di semua ukuran layar dan bisa diberi label teks yang dapat dibaca screen reader.
- Panggilan ke server hanya lewat `frontend/js/api.js`.
- Semua `localStorage` dibungkus `try/catch` (bisa gagal di mode privat).

### Angka format Indonesia (penting!)
Siswa akan mengetik angka dengan format Indonesia. Parser di `backend/segitiga/parser_angka.py` harus menerima:
- `1,8` → 1.8 (koma = desimal)
- `1.200` → 1200 (titik + tepat 3 digit = ribuan)
- `Rp300.000`, `300000`, `300.000` → 300000
- `1200 cm²`, `1200 cm2`, `1200` → 1200 (satuan dicek terpisah bila langkah memintanya)
- Pecahan `1/3` → 0.3333…

### Data siswa
Pengguna adalah anak di bawah umur. Simpan data seminimal mungkin: nama panggilan + kode kelas. Tidak ada email, nomor HP, atau foto.

## Perintah umum

```bash
# Menyiapkan lingkungan (sekali saja)
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Menjalankan aplikasi (bisa diakses HP di jaringan Wi-Fi yang sama)
python backend/app.py            # http://localhost:5000

# Tes
pytest backend/tests -q
ruff check backend && black --check backend
```

## Definisi "selesai" untuk setiap fitur
- [ ] Sesuai aturan desain di atas (cek ulang 9 poin).
- [ ] Tampil baik di layar 360 px (HP) dan 1280 px (laptop).
- [ ] Unit test Python lulus.
- [ ] Teks antarmuka berbahasa Indonesia dan sudah dibaca ulang.
- [ ] Checklist di [docs/06-roadmap.md](docs/06-roadmap.md) diperbarui.
