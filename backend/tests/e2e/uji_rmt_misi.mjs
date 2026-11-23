// Uji tampilan aktivitas RMT di halaman misi (Tahap 2B) dengan Edge headless (CDP).
// Tidak dijalankan pytest. Cara pakai (server uji harus sudah berjalan):
//
//   set PORT=5077 & set SEGIPINTAR_DB_PATH=<db sementara> & set SEGIPINTAR_ASISTEN=tiruan
//   python backend/app.py
//   node backend/tests/e2e/uji_rmt_misi.mjs <folder-kerja-sementara> [http://127.0.0.1:5077]
//
// Memeriksa: urutan layar RMT, umpan balik, "Lewati", skor tetap 6/6, tanpa melebar di 360 px,
// dan misi tetap bisa dikerjakan bila konten RMT gagal dimuat.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const DIR = process.argv[2];
const BASE = process.argv[3] || "http://127.0.0.1:5077";
if (!DIR) {
  console.error("Pakai: node uji_rmt_misi.mjs <folder-kerja-sementara> [base-url]");
  process.exit(2);
}
const SHOTS = join(DIR, "shots-rmt");
mkdirSync(SHOTS, { recursive: true });
const EDGE = process.env.EDGE || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PORT = 9334;

const edge = spawn(EDGE, [
  "--headless=new",
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${join(DIR, "edge-profil-rmt")}`,
  "--no-first-run",
  "--disable-extensions",
  "about:blank",
]);
const tidur = (ms) => new Promise((r) => setTimeout(r, ms));

for (let i = 0; i < 50; i++) {
  try {
    await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
    break;
  } catch {
    await tidur(200);
  }
}
const target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const tunggu = new Map();
const galat = [];
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && tunggu.has(m.id)) {
    tunggu.get(m.id)(m);
    tunggu.delete(m.id);
  } else if (m.method === "Runtime.exceptionThrown") {
    galat.push("EXC: " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
  } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
    galat.push("CONSOLE: " + m.params.args.map((a) => a.value ?? a.description).join(" "));
  }
});
const cmd = (method, params = {}) =>
  new Promise((r) => {
    const i = ++id;
    tunggu.set(i, r);
    ws.send(JSON.stringify({ id: i, method, params }));
  });
await cmd("Runtime.enable");
await cmd("Page.enable");
await cmd("Network.enable");

const js = async (expr) => {
  const r = await cmd("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result?.exceptionDetails) galat.push("EVAL: " + expr.slice(0, 80));
  return r.result?.result?.value;
};
const ukuran = (w, h, mobile) =>
  cmd("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile });
async function foto(nama) {
  const m = await cmd("Page.getLayoutMetrics");
  const s = m.result.cssContentSize || m.result.contentSize;
  const clip = { x: 0, y: 0, width: s.width, height: Math.min(s.height, 4000), scale: 1 };
  const r = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip });
  writeFileSync(join(SHOTS, nama + ".png"), Buffer.from(r.result.data, "base64"));
}
const pergi = async (hash, ms = 900) => {
  await js(`location.hash = ${JSON.stringify(hash)}`);
  await tidur(ms);
};
const klik = async (sel, teks = "", ms = 350) => {
  const r = await js(
    `(() => { const e = [...document.querySelectorAll(${JSON.stringify(sel)})].find(x => x.textContent.includes(${JSON.stringify(teks)}) && !x.disabled); if (!e) return false; e.click(); return true; })()`,
  );
  await tidur(ms);
  if (!r) gagal(`tidak menemukan ${sel} "${teks}"`);
  return r;
};
const klikLabel = async (awalan, ms = 150) => {
  const r = await js(
    `(() => { const e = [...document.querySelectorAll('button[aria-label]')].find(x => x.getAttribute('aria-label').startsWith(${JSON.stringify(awalan)}) && !x.disabled); if (!e) return false; e.click(); return true; })()`,
  );
  await tidur(ms);
  if (!r) gagal(`tidak menemukan tombol aria-label "${awalan}…"`);
};
const isi = (sel, nilai) =>
  js(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); e.value = ${JSON.stringify(nilai)}; e.dispatchEvent(new Event('input')); })()`);
const teks = (sel) => js(`document.querySelector(${JSON.stringify(sel)})?.textContent ?? null`);
const kelasUmpan = () => js(`document.querySelector('.umpan')?.className ?? null`);
const label = () => teks(".judul-langkah .label-tahap");

const hasil = [];
let jumlahGagal = 0;
function gagal(pesan) {
  jumlahGagal++;
  hasil.push("GAGAL  " + pesan);
}
function cek(kondisi, pesan, info = "") {
  if (kondisi) hasil.push("OK     " + pesan);
  else gagal(`${pesan} ${info}`);
}
const melebar = [];
async function cekLebar(nama, batas = 360) {
  const w = await js("document.documentElement.scrollWidth");
  if (w > batas) melebar.push(`${nama}=${w}px`);
  if (await js("/\\b(null|undefined)\\b/.test(document.body.innerText)")) gagal(`${nama}: teks "null/undefined" tampil`);
}

// ======================================================== HP 360 px — misi 1 lengkap
await ukuran(360, 800, true);
await cmd("Page.navigate", { url: BASE + "/" });
await tidur(1200);
await js("(() => { try { localStorage.clear(); } catch {} })()");
await cmd("Page.navigate", { url: BASE + "/" });
await tidur(1200);
await isi("#nama", "Uji");
await isi("#kelas", "8z");
await js(`document.querySelector('form').requestSubmit()`);
await tidur(900);

await pergi("#/misi/1", 1200);
cek((await teks(".bar-bawah"))?.includes("Mulai langkah 1") === false, "cerita: tombol 'Mulai langkah 1' diganti alur RMT");
for (let i = 0; i < 10 && !(await label()); i++) await klik(".bar-bawah .tombol", "Lanjut", 250);

// 1) Tebak dulu + tujuan & makna
cek((await label()) === "Tebak dulu", "layar pertama setelah cerita = 'Tebak dulu'", await label());
cek(!!(await teks(".kartu-tujuan")), "kartu tujuan & makna tampil di layar tebak");
cek((await teks(".posisi"))?.includes("Sebelum mengerjakan (1 dari 3)"), "posisi 'Sebelum mengerjakan (1 dari 3)'");
await cekLebar("tebak");
await foto("01-tebak");
await klik(".bar-bawah .tombol", "Kembali");
cek(!(await label()) && !!(await teks(".bar-bawah")), "Kembali dari tebak → layar cerita");
await klik(".bar-bawah .tombol", "Lanjut");
cek((await label()) === "Tebak dulu", "Lanjut dari cerita → tebak lagi");
await klik(".bar-bawah .tombol", "Simpan tebakan");
cek((await kelasUmpan())?.includes("info"), "tebakan kosong → pesan 'Pilih jawabanmu dulu'");
await klik(".opsi", "Desain A");
await klik(".bar-bawah .tombol", "Simpan tebakan", 600);
cek(!!(await teks(".umpan")) && (await teks(".bar-bawah"))?.includes("Lanjut"), "tebakan tersimpan, umpan balik + Lanjut");
await foto("02-tebak-tersimpan");
await klik(".bar-bawah .tombol", "Lanjut");

// 2) Susun rencana (urutan kartu)
cek((await label()) === "Susun rencanamu", "layar 'Susun rencanamu'", await label());
cek((await js("document.querySelectorAll('.urutan-kartu').length")) === 4, "4 kartu rencana tampil");
await cekLebar("rencana");
await foto("03-rencana-awal");
await klik(".bar-bawah .tombol", "Periksa", 600);
cek((await kelasUmpan())?.includes("salah"), "urutan awal → umpan balik salah", await kelasUmpan());
const kartuPertama = await teks(".urutan-kartu .urutan-teks");
for (let i = 0; i < 3; i++) await klikLabel(`Turunkan: ${kartuPertama}`);
cek(
  (await js("document.activeElement?.getAttribute('aria-label')"))?.startsWith("Naikkan:") ||
    (await js("document.activeElement?.closest('.urutan-kartu') !== null")),
  "fokus tetap pada kartu yang dipindah",
);
await klik(".bar-bawah .tombol", "Periksa", 600);
cek((await kelasUmpan())?.includes("benar"), "urutan benar → umpan balik benar", await kelasUmpan());
cek((await js("[...document.querySelectorAll('.urutan-geser')].every(b => b.disabled)")) === true, "kartu terkunci setelah benar");
await foto("04-rencana-benar");
await klik(".bar-bawah .tombol", "Lanjut");

// 3) Tata informasi → dilewati
cek((await label()) === "Tata informasinya", "layar 'Tata informasinya'", await label());
await cekLebar("representasi");
await klik(".bar-bawah .tombol", "Lewati", 600);
cek(!!(await js("document.querySelector('.titik-progres')")), "Lewati representasi → langkah 1 berskor", await label());

// Langkah berskor misi 1 (sama seperti sebelum RMT)
for (const [chip, zona] of [["60 cm", "Alas A"], ["40 cm", "Tinggi A"], ["80 cm", "Alas B"], ["30 cm", "Tinggi B"]]) {
  await klik(".chip", chip, 120);
  await klik(".zona-label", zona, 120);
}
await klik(".bar-bawah .tombol", "Periksa", 500);
await klik(".bar-bawah .tombol", "Lanjut");
await klik(".opsi", "Luas kedua");
await klik(".bar-bawah .tombol", "Periksa", 500);
await klik(".bar-bawah .tombol", "Lanjut");
for (let k = 0; k < 2; k++) {
  await isi(".isian-angka input", "1.200");
  await klik(".pilihan-satuan .opsi", "cm²");
  await klik(".bar-bawah .tombol", "Periksa", 500);
  await klik(".bar-bawah .tombol", "Lanjut");
}
for (const jawab of ["sama dengan", "Keduanya", "60 × 40"]) {
  await klik(".opsi", jawab);
  await klik(".bar-bawah .tombol", "Periksa", 500);
  await klik(".bar-bawah .tombol", jawab === "60 × 40" ? "Selesai" : "Lanjut", 600);
}

// 4) Cek hasilmu (sebelum misi diselesaikan)
cek((await label()) === "Cek hasilmu", "setelah langkah terakhir → 'Cek hasilmu'", await label());
cek((await teks(".posisi"))?.includes("Setelah mengerjakan"), "posisi 'Setelah mengerjakan'");
await cekLebar("validasi");
await klik(".bar-bawah .tombol", "Kembali");
cek(!!(await js("document.querySelector('.titik-progres')")), "Kembali dari cek hasil → langkah terakhir");
await klik(".bar-bawah .tombol", "Selesai", 600);
await klik(".opsi", "Ya, karena");
await klik(".bar-bawah .tombol", "Periksa", 600);
cek((await kelasUmpan())?.includes("benar"), "cek hasil benar");
await foto("05-cek-hasil");
await klik(".bar-bawah .tombol", "Lanjut", 900);

// Ringkasan → 5) Di mana lagi?
cek(!(await label()), "setelah cek hasil → ringkasan misi");
await klik(".bar-bawah .tombol", "Lanjut");
cek((await label()) === "Di mana lagi?", "ringkasan → 'Di mana lagi?'", await label());
await cekLebar("transendensi");
await klik(".opsi", "Memilih potongan");
await klik(".bar-bawah .tombol", "Periksa", 600);
cek((await kelasUmpan())?.includes("salah"), "transendensi baru 1 pilihan → umpan balik", await kelasUmpan());
await klik(".opsi", "Menentukan kebun");
await klik(".bar-bawah .tombol", "Periksa", 600);
cek((await kelasUmpan())?.includes("benar"), "transendensi 2 pilihan benar");
await foto("06-transendensi");
await klik(".bar-bawah .tombol", "Lanjut");

// 6) Refleksi dengan kalimat pembuka dari backend
cek((await js("document.querySelectorAll('.kalimat-pembuka li').length")) > 0, "refleksi: kalimat pembuka tampil");
await cekLebar("refleksi");
await foto("07-refleksi");
await isi("#refleksi", "Pertama aku hitung luas kedua desain, lalu kubandingkan.");
await klik(".bar-bawah .tombol", "Kirim", 900);
const skor = await teks(".skor-besar");
cek(skor?.startsWith("6 dari 6"), "skor misi 1 tetap 6 dari 6", skor);
await foto("08-hasil");

// ======================================================== laptop 1280 px — misi 2, semua dilewati
await ukuran(1280, 800, false);
await pergi("#/misi/2", 1200);
for (let i = 0; i < 10 && !(await label()); i++) await klik(".bar-bawah .tombol", "Lanjut", 250);
cek((await label()) === "Tebak dulu", "misi 2 (laptop): tebak dulu");
for (let i = 0; i < 3; i++) await klik(".bar-bawah .tombol", "Lewati", 500);
cek(!!(await js("document.querySelector('.titik-progres')")), "misi 2: lewati semua RMT → langkah 1");
await foto("09-laptop-misi2-langkah1");
await cekLebar("misi2-laptop", 1280);

// ======================================================== konten RMT gagal dimuat → misi tetap jalan
await ukuran(360, 800, true);
await cmd("Network.setBlockedURLs", { urls: ["*/api/rmt/*"] });
await pergi("#/misi", 600);
await pergi("#/misi/1", 1200);
let adaMulai = false;
for (let i = 0; i < 10 && !adaMulai; i++) {
  adaMulai = (await teks(".bar-bawah"))?.includes("Mulai langkah 1");
  if (!adaMulai) await klik(".bar-bawah .tombol", "Lanjut", 250);
}
cek(adaMulai, "RMT gagal dimuat → alur lama 'Mulai langkah 1' tetap ada");
await cmd("Network.setBlockedURLs", { urls: [] });

console.log(hasil.join("\n"));
console.log("\nMelebar di HP:", melebar.length ? melebar.join(", ") : "tidak ada");
console.log("Galat JS:", galat.length ? "\n" + galat.join("\n") : "tidak ada");
console.log(`\n${jumlahGagal ? "ADA " + jumlahGagal + " PEMERIKSAAN GAGAL" : "SEMUA PEMERIKSAAN LULUS"}`);
ws.close();
edge.kill();
process.exit(jumlahGagal || melebar.length || galat.length ? 1 : 0);
