// Uji tampilan misi 1–4 lengkap di browser (Tahap 2): semua layar RMT + langkah berskor.
// Langkah berskor dilewati lewat petunjuk ke-3 (skor tahap 0, sesuai aturan), karena tujuan
// tes ini adalah alur, navigasi, tampilan, dan remedial — skor 6/6 sudah diuji di pytest.
// Juga memeriksa HP bersama: siswa berikutnya tidak mewarisi data tingkat siswa sebelumnya.
//
// Server uji harus berjalan dengan SEGIPINTAR_MISI_BEBAS=1 (semua misi terbuka):
//   node backend/tests/e2e/uji_misi_1_4.mjs <folder-kerja-sementara> [http://127.0.0.1:5077]

import { readFileSync } from "node:fs";
import { mulaiBrowser, tidur } from "./cdp.mjs";

const DIR = process.argv[2];
if (!DIR) {
  console.error("Pakai: node uji_misi_1_4.mjs <folder-kerja-sementara> [base-url]");
  process.exit(2);
}
const RMT = JSON.parse(readFileSync(new URL("../../data/soal/rmt_misi.json", import.meta.url), "utf-8"));
const b = await mulaiBrowser({ dir: DIR, base: process.argv[3] || "http://127.0.0.1:5077", port: 9336, nama: "misi14" });
const { cek } = b;
const label = () => b.teks(".judul-langkah .label-tahap");

async function pilihOpsi(a, ids) {
  for (const id of [].concat(ids)) await b.klik(".opsi", a.opsi.find((o) => o.id === id).teks, 150);
}

async function susunUrutan(a) {
  const target = a.kunci[0].map((id) => a.kartu.find((k) => k.id === id).teks);
  for (let i = 0; i < target.length; i++) {
    const sekarang = await b.js(`[...document.querySelectorAll('.urutan-teks')].map(x => x.textContent)`);
    for (let j = sekarang.indexOf(target[i]); j > i; j--) {
      await b.js(
        `[...document.querySelectorAll('button[aria-label]')].find(x => x.getAttribute('aria-label') === ${JSON.stringify("Naikkan: " + target[i])}).click()`,
      );
      await tidur(80);
    }
  }
}

async function misi(id, lebar) {
  const konten = RMT.find((k) => k.misi_id === id);
  const per = Object.fromEntries(konten.aktivitas.map((a) => [a.tahap, a]));
  await b.pergi(`#/misi/${id}`, 1300);
  for (let i = 0; i < 12 && !(await label()); i++) await b.klik(".bar-bawah .tombol", "Lanjut", 220);

  // Sebelum mengerjakan
  cek((await label()) === "Tebak dulu" && !!(await b.teks(".kartu-tujuan")), `misi ${id}: tujuan & tebak dulu`);
  await b.cekLebar(`m${id}-tebak`, lebar);
  await pilihOpsi(per.input, per.input.opsi[0].id);
  await b.klik(".bar-bawah .tombol", "Simpan tebakan", 600);
  await b.klik(".bar-bawah .tombol", "Lanjut");
  cek((await label()) === "Susun rencanamu", `misi ${id}: susun rencana`);
  await susunUrutan(per.perencanaan);
  await b.klik(".bar-bawah .tombol", "Periksa", 600);
  cek((await b.kelasUmpan())?.includes("benar"), `misi ${id}: urutan rencana benar`, await b.teks(".umpan"));
  await b.cekLebar(`m${id}-rencana`, lebar);
  await b.klik(".bar-bawah .tombol", "Lanjut");
  cek((await label()) === "Tata informasinya", `misi ${id}: tata informasi`);
  await pilihOpsi(per.representasi, per.representasi.kunci);
  await b.klik(".bar-bawah .tombol", "Periksa", 600);
  cek((await b.kelasUmpan())?.includes("benar"), `misi ${id}: representasi benar`);
  await b.klik(".bar-bawah .tombol", "Lanjut", 500);

  // Langkah berskor: buka petunjuk sampai cara lengkap, lalu lanjut
  let langkah = 0;
  while ((await b.jumlah(".titik-progres")) && langkah < 10) {
    langkah++;
    await b.cekLebar(`m${id}-langkah${langkah}`, lebar);
    for (let k = 0; k < 3 && (await b.jumlah(".tombol-petunjuk")); k++) await b.klik(".tombol-petunjuk", "petunjuk", 450);
    const tombolBar = await b.teks(".bar-bawah");
    await b.klik(".bar-bawah .tombol", tombolBar.includes("Selesai") ? "Selesai" : "Lanjut", 600);
  }
  cek(langkah === (id === 1 ? 7 : 6), `misi ${id}: ${langkah} langkah berskor dilalui`);

  // Setelah mengerjakan
  cek((await label()) === "Cek hasilmu", `misi ${id}: cek hasilmu`, await label());
  await pilihOpsi(per.validasi, per.validasi.kunci);
  await b.klik(".bar-bawah .tombol", "Periksa", 600);
  cek((await b.kelasUmpan())?.includes("benar"), `misi ${id}: validasi benar`);
  await b.cekLebar(`m${id}-validasi`, lebar);
  await b.klik(".bar-bawah .tombol", "Lanjut", 1000);
  cek((await b.teks("h1")) === "Ringkasan langkahmu", `misi ${id}: ringkasan`);
  await b.klik(".bar-bawah .tombol", "Lanjut");
  cek((await label()) === "Di mana lagi?", `misi ${id}: transendensi`);
  await pilihOpsi(per.transendensi, per.transendensi.kunci);
  await b.klik(".bar-bawah .tombol", "Periksa", 600);
  cek((await b.kelasUmpan())?.includes("benar"), `misi ${id}: transendensi benar`);
  await b.cekLebar(`m${id}-transendensi`, lebar);
  await b.klik(".bar-bawah .tombol", "Lanjut");
  cek((await b.jumlah(".kalimat-pembuka li")) > 0, `misi ${id}: refleksi dengan kalimat pembuka`);
  await b.isi("#refleksi", "Pertama aku membaca data, lalu memilih rumus.");
  await b.klik(".bar-bawah .tombol", "Kirim", 1000);
  cek((await b.teks("h1")) === `Misi ${id} selesai!`, `misi ${id}: layar hasil`);
  cek((await b.jumlah(".kartu-remedial h3")) > 0, `misi ${id}: saran remedial muncul (petunjuk lengkap dibuka)`);
  await b.cekLebar(`m${id}-hasil`, lebar);
  await b.foto(`misi${id}-hasil-${lebar}`);
}

// HP bersama: siswa A menyimpan tingkat latihan, lalu "Ganti nama" → siswa B.
await b.ukuran(360, 800, true);
await b.masuk("SiswaA", "8z");
const sesiA = await b.js("JSON.parse(localStorage.getItem('segipintar.sesi')).sesi_id");
await b.js(`localStorage.setItem('segipintar.tingkatBertahap', JSON.stringify({sesi_id: ${JSON.stringify(sesiA)}, tingkat: 3}))`);
await b.pergi("#/", 800);
await b.klik("a", "Ganti nama", 900);
cek((await b.js("localStorage.getItem('segipintar.tingkatBertahap')")) === null, "Ganti nama menghapus data tingkat siswa sebelumnya");
await b.isi("#nama", "SiswaB");
await b.isi("#kelas", "8z");
await b.js(`document.querySelector('form').requestSubmit()`);
await tidur(900);
await b.pergi("#/latihan/bertahap", 1200);
cek((await b.teks(".posisi"))?.includes("Tingkat 1"), "siswa B mulai dari tingkat 1 (tidak mewarisi siswa A)");
cek(!(await b.js(`JSON.stringify(localStorage)`)).includes(sesiA), "sesi_id siswa A tidak tersisa di perangkat");

await misi(1, 360);
await misi(3, 360);
await b.ukuran(1280, 800, false);
await misi(2, 1280);
await misi(4, 1280);

b.selesai();
