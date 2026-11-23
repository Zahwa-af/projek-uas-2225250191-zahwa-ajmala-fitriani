// Uji tampilan Tahap 2C (Cognitive Load): fading Soal Cerita Bertahap, remedial adaptif,
// layar perbandingan keliling–luas, dan panel Pembimbing yang tertutup secara bawaan.
// Tidak dijalankan pytest. Server uji harus sudah berjalan (lihat uji_rmt_misi.mjs):
//
//   node backend/tests/e2e/uji_cognitive_load.mjs <folder-kerja-sementara> [http://127.0.0.1:5077]

import { mulaiBrowser } from "./cdp.mjs";

const DIR = process.argv[2];
if (!DIR) {
  console.error("Pakai: node uji_cognitive_load.mjs <folder-kerja-sementara> [base-url]");
  process.exit(2);
}
const b = await mulaiBrowser({ dir: DIR, base: process.argv[3] || "http://127.0.0.1:5077", nama: "cl" });
const { cek } = b;

// Hitung jawaban dari cerita (tes ini tidak tahu kunci server).
async function dataSoal() {
  const cerita = await b.js(`[...document.querySelectorAll('.cerita li')].map(x => x.textContent).join(' ')`);
  const angka = (re) => Number(cerita.match(re)[1]);
  const satuan = cerita.match(/alas \d+ (cm|m)\b/)[1];
  const alas = angka(/alas (\d+)/);
  const tinggi = angka(/Tingginya (\d+)/);
  const banyak = angka(/Ada (\d+)/);
  return { alas, tinggi, banyak, satuan, satu: (alas * tinggi) / 2, total: (banyak * alas * tinggi) / 2 };
}
const fmtId = (n) => n.toLocaleString("id-ID", { maximumFractionDigits: 2 });
const tingkatTampil = async () => Number((await b.teks(".posisi"))?.match(/Tingkat (\d)/)?.[1]);

async function jawab(nilai, satuan) {
  await b.isi(".isian-angka input", fmtId(nilai));
  await b.klik(".pilihan-satuan .opsi", satuan, 120);
  await b.klik(".bar-bawah .tombol", "Periksa", 500);
}
async function jawabSemuaBenar() {
  const d = await dataSoal();
  const n = await b.jumlah(".judul-langkah");
  const isian = (await b.teks(".label-tahap"))?.match(/dari (\d)/)?.[1];
  for (let k = 0; k < Number(isian); k++) {
    const instruksi = await b.teks(".judul-langkah");
    await jawab(instruksi.includes("satu") ? d.satu : d.total, `${d.satuan}²`);
    await b.klik(".bar-bawah .tombol", k === Number(isian) - 1 ? "Selesai" : "Lanjut", 600);
  }
  return n;
}

// ===================================================== HP 360 px
await b.ukuran(360, 800, true);
await b.masuk();

await b.pergi("#/latihan");
cek((await b.teks(".menu li strong")) === "Soal Cerita Bertahap", "menu latihan: Soal Cerita Bertahap paling atas");

// --- Tingkat 1: contoh hampir lengkap, isi langkah terakhir saja
await b.pergi("#/latihan/bertahap", 1200);
cek((await tingkatTampil()) === 1, "mulai di tingkat 1", await b.teks(".posisi"));
cek((await b.jumlah(".kartu-contoh li")) === 4, "tingkat 1: 4 langkah contoh sudah dikerjakan");
cek((await b.teks(".label-tahap")) === "Isian 1 dari 1", "tingkat 1: hanya 1 isian");
await b.cekLebar("bertahap-t1");
await b.foto("01-bertahap-t1");
await b.klik(".bar-bawah .tombol", "Periksa");
cek((await b.kelasUmpan())?.includes("info"), "isian kosong → pesan 'Isi jawabanmu dulu'");
await jawabSemuaBenar();
cek((await b.teks("h1")) === "Soal selesai!", "layar penjelasan diri setelah soal selesai");
cek((await b.kelasUmpan())?.includes("benar"), "benar tanpa bantuan → umpan 'bantuan dikurangi'");
cek(!(await b.teks(".kartu-tujuan")), "penjelasan pembanding belum tampil sebelum diminta");
await b.isi("#penjelasan-diri", "Karena segitiga setengah persegi panjang.");
await b.klik(".tombol", "Bandingkan penjelasanku");
cek(!!(await b.teks(".kartu-tujuan")), "penjelasan pembanding tampil setelah 'Bandingkan'");
cek((await b.js("document.querySelector('#penjelasan-diri').value"))?.startsWith("Karena"), "tulisan siswa tidak hilang");
await b.cekLebar("bertahap-refleksi");
await b.foto("02-bertahap-refleksi");
await b.klik(".bar-bawah .tombol", "Soal berikutnya", 1000);

// --- Tingkat 2: bantuan berkurang; satu kali salah → tetap
cek((await tingkatTampil()) === 2, "naik ke tingkat 2 (satu tingkat saja)", await b.teks(".posisi"));
cek((await b.jumlah(".kartu-contoh li")) === 3, "tingkat 2: 3 langkah contoh");
let d = await dataSoal();
await jawab(d.alas * d.tinggi, `${d.satuan}²`);
cek((await b.kelasUmpan())?.includes("salah") && (await b.teks(".umpan"))?.includes("½"), "lupa ½ → umpan balik menunjuk ½");
await b.foto("03-bertahap-t2-salah");
await jawab(d.satu, `${d.satuan}²`);
await b.klik(".bar-bawah .tombol", "Lanjut", 500);
cek((await b.jumlah(".kartu-contoh li")) === 4, "luas satu yang sudah benar ikut tampil di 'Sudah dikerjakan'");
await jawab(d.total, `${d.satuan}²`);
await b.klik(".bar-bawah .tombol", "Selesai", 700);
cek((await b.kelasUmpan())?.includes("info"), "ada salah → tingkat tetap");
await b.klik(".bar-bawah .tombol", "Soal berikutnya", 1000);
cek((await tingkatTampil()) === 2, "tetap di tingkat 2");
await jawabSemuaBenar();
await b.klik(".bar-bawah .tombol", "Soal berikutnya", 1000);

// --- Tingkat 3: pengecoh sisi miring; petunjuk ke-3 → bantuan ditambah lagi
cek((await tingkatTampil()) === 3, "naik ke tingkat 3");
cek((await b.teks(".cerita"))?.includes("sisi miring"), "tingkat 3: ada informasi pengecoh (sisi miring)");
cek(!(await b.js("/\\d/.test([...document.querySelectorAll('.kolom-gambar svg text')].map(t => t.textContent).join(''))")), "tingkat 3: gambar tanpa angka");
for (let k = 1; k <= 3; k++) await b.klik(".tombol-petunjuk", `petunjuk ${k}`, 400);
cek((await b.jumlah(".petunjuk-item")) === 3 && !(await b.jumlah(".tombol-petunjuk")), "petunjuk 1 → 2 → 3 bertahap");
await b.cekLebar("bertahap-t3");
await b.foto("04-bertahap-t3-petunjuk");
await jawabSemuaBenar();
cek((await b.teks(".umpan"))?.includes("lebih banyak"), "petunjuk ke-3 dibuka → bantuan ditambah");
await b.klik(".bar-bawah .tombol", "Soal berikutnya", 1000);
cek((await tingkatTampil()) === 2, "turun satu tingkat ke 2");

// tingkat tersimpan di perangkat
await b.pergi("#/latihan", 500);
await b.pergi("#/latihan/bertahap", 1200);
cek((await tingkatTampil()) === 2, "tingkat bantuan diingat saat halaman dibuka lagi");

// --- Belajar: perbandingan konsep + jalur contoh lengkap → latihan bertahap
await b.pergi("#/belajar/4/5");
cek((await b.teks("h1")) === "Bandingkan keliling dan luas", "layar Bandingkan keliling dan luas");
await b.cekLebar("belajar-bandingkan");
await b.foto("05-belajar-bandingkan");
await b.pergi("#/belajar/5/5");
cek((await b.js("document.querySelector('.bar-bawah .tombol-utama')?.getAttribute('href')")) === "#/latihan/bertahap", "contoh lengkap → 'Coba sendiri' ke latihan bertahap");

// --- Misi 1 dengan 2 kali lupa ½ → remedial "Rumus luas segitiga", skor tetap 6
await b.pergi("#/misi/1", 1200);
for (let i = 0; i < 10 && !(await b.teks(".label-tahap")); i++) await b.klik(".bar-bawah .tombol", "Lanjut", 250);
for (let i = 0; i < 3; i++) await b.klik(".bar-bawah .tombol", "Lewati", 500);
cek((await b.jumlah("details.panel-pembimbing")) === 1, "panel Pembimbing ada di langkah misi");
cek((await b.js("document.querySelector('details.panel-pembimbing').open")) === false, "panel Pembimbing tertutup secara bawaan");
await b.foto("06-misi-panel-tertutup");
await b.klik("details.panel-pembimbing summary", "Tanya Pembimbing", 300);
cek((await b.js("!!document.querySelector('details.panel-pembimbing textarea')?.offsetParent")) === true, "panel terbuka saat diketuk");
await b.klik("details.panel-pembimbing summary", "Tanya Pembimbing", 300);
for (const [chip, zona] of [["60 cm", "Alas A"], ["40 cm", "Tinggi A"], ["80 cm", "Alas B"], ["30 cm", "Tinggi B"]]) {
  await b.klik(".chip", chip, 120);
  await b.klik(".zona-label", zona, 120);
}
await b.klik(".bar-bawah .tombol", "Periksa", 500);
cek((await b.js("document.querySelector('details.panel-pembimbing').open")) === false, "panel tetap tertutup setelah render ulang");
await b.klik(".bar-bawah .tombol", "Lanjut");
await b.klik(".opsi", "Luas kedua");
await b.klik(".bar-bawah .tombol", "Periksa", 500);
await b.klik(".bar-bawah .tombol", "Lanjut");
for (let k = 0; k < 2; k++) {
  await b.isi(".isian-angka input", "2.400");
  await b.klik(".pilihan-satuan .opsi", "cm²", 120);
  await b.klik(".bar-bawah .tombol", "Periksa", 500);
}
for (let k = 0; k < 2; k++) {
  await b.isi(".isian-angka input", "1.200");
  await b.klik(".pilihan-satuan .opsi", "cm²", 120);
  await b.klik(".bar-bawah .tombol", "Periksa", 500);
  await b.klik(".bar-bawah .tombol", "Lanjut");
}
for (const j of ["sama dengan", "Keduanya", "60 × 40"]) {
  await b.klik(".opsi", j);
  await b.klik(".bar-bawah .tombol", "Periksa", 500);
  await b.klik(".bar-bawah .tombol", j === "60 × 40" ? "Selesai" : "Lanjut", 600);
}
await b.klik(".bar-bawah .tombol", "Lewati", 900); // Cek hasilmu
await b.klik(".bar-bawah .tombol", "Lanjut"); // ringkasan
await b.klik(".bar-bawah .tombol", "Lewati", 500); // Di mana lagi?
await b.klik(".bar-bawah .tombol", "Lewati", 900); // refleksi
cek((await b.teks(".skor-besar"))?.startsWith("6 dari 6"), "skor misi tetap 6 dari 6", await b.teks(".skor-besar"));
cek((await b.teks(".kartu-remedial h3")) === "Rumus luas segitiga", "remedial di hasil misi: Rumus luas segitiga", await b.teks(".kartu-remedial h3"));
cek((await b.js("[...document.querySelectorAll('.remedial-tautan a')].map(a => a.getAttribute('href')).includes('#/latihan/bertahap')")) === true, "remedial menautkan latihan bertahap");
await b.cekLebar("misi-hasil-remedial");
await b.foto("07-misi-hasil-remedial");

await b.pergi("#/hasil", 1000);
cek((await b.teks(".kartu-remedial h3")) === "Rumus luas segitiga", "Hasilku: kartu Perkuat pemahamanmu");
await b.cekLebar("hasilku");
await b.foto("08-hasilku");
await b.klik(".remedial-tautan a", "Materi rumus luas", 900);
cek((await b.teks("h1")) === "Mulai dari persegi panjang", "tautan remedial membuka materi yang tepat");

// ===================================================== laptop 1280 px
await b.ukuran(1280, 800, false);
await b.pergi("#/latihan/bertahap", 1200);
await b.cekLebar("bertahap-laptop", 1280);
await b.foto("09-laptop-bertahap");
await b.pergi("#/hasil", 1000);
await b.cekLebar("hasilku-laptop", 1280);
await b.foto("10-laptop-hasilku");

// mode gelap
await b.cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
await b.ukuran(360, 800, true);
await b.pergi("#/latihan/bertahap", 1200);
await b.foto("11-gelap-bertahap");

b.selesai();
