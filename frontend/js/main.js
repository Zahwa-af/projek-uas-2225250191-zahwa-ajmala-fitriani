// Router berbasis hash: #/, #/belajar/1/2, #/latihan, #/misi/3, #/hasil, #/guru

import { api } from "./api.js";
import { el, kotakUmpan } from "./dom.js";
import { halamanBeranda } from "./halaman/beranda.js";
import { halamanDaftarBelajar, halamanTopik } from "./halaman/belajar.js";
import { halamanGuru } from "./halaman/guru.js";
import { halamanHasil } from "./halaman/hasil.js";
import { halamanDaftarLatihan, halamanLatihanPilah, halamanLatihanTinggi } from "./halaman/latihan.js";
import { halamanDaftarMisi, halamanMisi } from "./halaman/misi.js";
import { ambilSesi, hapusSesi } from "./state.js";

const app = document.getElementById("app");
const namaSiswa = document.getElementById("nama-siswa");

// [pola, halaman, butuh sesi?]
const RUTE = [
  [/^\/?$/, (w) => halamanBeranda(w, jalankan), false],
  [/^\/belajar$/, halamanDaftarBelajar, true],
  [/^\/belajar\/(\d+)(?:\/(\d+))?$/, halamanTopik, true],
  [/^\/latihan$/, halamanDaftarLatihan, true],
  [/^\/latihan\/tinggi$/, halamanLatihanTinggi, true],
  [/^\/latihan\/pilah$/, halamanLatihanPilah, true],
  [/^\/misi$/, halamanDaftarMisi, true],
  [/^\/misi\/(\d+)$/, halamanMisi, true],
  [/^\/hasil$/, halamanHasil, true],
  [/^\/guru$/, halamanGuru, false],
];

let nomorNavigasi = 0;

async function jalankan() {
  const jalur = location.hash.replace(/^#/, "") || "/";
  const cocok = RUTE.map(([pola, fn, sesi]) => [jalur.match(pola), fn, sesi]).find(([m]) => m);
  const sesi = ambilSesi();
  namaSiswa.textContent = sesi ? sesi.nama_panggilan : "";

  if (!cocok || (cocok[2] && !sesi)) {
    if (jalur !== "/") {
      location.hash = "#/";
      return;
    }
  }
  const [m, halaman] = cocok;

  // Setiap navigasi punya wadah sendiri, agar halaman lama yang masih memuat tidak menimpa.
  const saya = ++nomorNavigasi;
  const wadah = el("div");
  app.replaceChildren(wadah);
  window.scrollTo(0, 0);
  try {
    await halaman(wadah, ...m.slice(1).filter((x) => x !== undefined));
  } catch (e) {
    if (saya !== nomorNavigasi) return;
    wadah.replaceChildren(
      el("h1", {}, "Ada kendala"),
      kotakUmpan("salah", e.message),
      el("p", {}, el("a", { href: "#/" }, "← Kembali ke beranda")),
    );
  }
  if (saya === nomorNavigasi && !app.contains(document.activeElement)) {
    wadah.querySelector("h1")?.focus({ preventScroll: true });
  }
}

async function mulai() {
  const sesi = ambilSesi();
  if (sesi) {
    try {
      await api.cekSesi(sesi.sesi_id);
    } catch (e) {
      if (e.status === 404) hapusSesi(); // database direset → minta nama lagi
    }
  }
  window.addEventListener("hashchange", jalankan);
  jalankan();
}

mulai();
