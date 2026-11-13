// Latihan pemanasan (tidak masuk skor rubrik): Tunjuk Tingginya (F-02) dan Pilah Informasi (F-05).

import { api } from "../api.js";
import { barBawah, el, gantiIsi, kotakUmpan, svgEl, tombol } from "../dom.js";
import * as G from "../geometri.js";
import { buatPilah } from "../pilah-info.js";

export function halamanDaftarLatihan(app) {
  const menu = [
    ["#/latihan/tinggi", "Tunjuk Tingginya", "Pilih garis yang merupakan tinggi segitiga."],
    ["#/latihan/pilah", "Pilah Informasi", "Pisahkan informasi yang dipakai dan yang tidak."],
  ];
  app.append(
    el("h1", { tabindex: "-1" }, "Latihan"),
    el("p", {}, "Latihan ini untuk pemanasan. Tidak ada skor, jadi santai saja."),
    el(
      "ol",
      { class: "menu" },
      menu.map(([href, judul, teks], i) =>
        el(
          "li",
          {},
          el(
            "a",
            { class: "kartu-menu", href },
            el("span", { class: "nomor", "aria-hidden": "true" }, String(i + 1)),
            el("span", {}, el("strong", {}, judul), el("span", { class: "teks-redup" }, teks)),
          ),
        ),
      ),
    ),
    barBawah(el("a", { class: "tombol", href: "#/" }, "Beranda"), el("a", { class: "tombol tombol-utama", href: "#/misi" }, "Ke misi")),
  );
}

// ------------------------------------------------------------------ Tunjuk Tingginya
const K = 4; // koordinat server 0–100 diperbesar agar label terbaca

const P = (q) => ({ x: q.x * K, y: q.y * K });
const garis = (a, b, kelas, attrs = {}) =>
  svgEl("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: kelas, ...attrs });
const teks = (p, isi, kelas = "") =>
  svgEl("text", { x: p.x, y: p.y, class: `label ${kelas}`, "text-anchor": "middle", "dominant-baseline": "middle" }, isi);

function svgSoalTinggi(soal, hasil, dipilih, pilih) {
  const A = P(soal.titik.A);
  const B = P(soal.titik.B);
  const C = P(soal.titik.C);
  const svg = svgEl("svg", {
    viewBox: "0 50 400 330",
    role: "img",
    "aria-label": "Segitiga dengan alas biru dan tiga garis P, Q, R dari titik puncak.",
  });
  svg.append(
    svgEl("polygon", { points: [A, B, C].map((p) => `${p.x},${p.y}`).join(" "), class: "isi-segitiga" }),
    garis(A, C, "garis-sisi"),
    garis(B, C, "garis-sisi"),
    garis(A, B, "garis-alas"),
    teks({ x: (A.x + B.x) / 2, y: A.y + 22 }, "alas", "label-alas"),
  );

  for (const k of soal.kandidat) {
    const dari = P(k.dari);
    const ke = P(k.ke);
    const salahDipilih = hasil && !hasil.benar && k.id === dipilih;
    svg.append(garis(dari, ke, salahDipilih ? "garis-salah" : "garis-kandidat"));
    const arah = G.satuan(G.kurang(ke, dari));
    const normal = { x: -arah.y, y: arah.x };
    const posisi = G.tambah(G.tambah(dari, G.kali(G.kurang(ke, dari), 0.6)), G.kali(normal, 14));
    svg.append(teks(posisi, k.id, "label-huruf"));
    if (!hasil) {
      const area = garis(dari, ke, "area-ketuk", { "aria-hidden": "true" });
      area.addEventListener("click", () => pilih(k.id));
      svg.append(area);
    }
  }

  if (hasil) {
    const kunci = soal.kandidat.find((k) => k.id === hasil.kunci);
    const atas = P(kunci.dari);
    const kaki = P(kunci.ke);
    if (kaki.x < A.x) svg.append(garis(kaki, A, "garis-perpanjangan"));
    const arahSiku = kaki.x <= A.x + 1 ? { x: 1, y: 0 } : { x: -1, y: 0 };
    svg.append(
      garis(atas, kaki, "garis-tinggi"),
      svgEl("polyline", {
        points: [
          { x: kaki.x + arahSiku.x * 12, y: kaki.y },
          { x: kaki.x + arahSiku.x * 12, y: kaki.y - 12 },
          { x: kaki.x, y: kaki.y - 12 },
        ]
          .map((p) => `${p.x},${p.y}`)
          .join(" "),
        class: "tanda-siku",
      }),
      teks({ x: atas.x + (arahSiku.x > 0 ? 34 : -34), y: (atas.y + kaki.y) / 2 }, "tinggi", "label-tinggi"),
    );
  }
  return svg;
}

export async function halamanLatihanTinggi(app) {
  const skor = { benar: 0, total: 0 };
  let soal = await api.soalTinggi();
  let hasil = null;
  let dipilih = null;
  let sibuk = false;

  async function pilih(id) {
    if (hasil || sibuk) return;
    sibuk = true;
    try {
      dipilih = id;
      hasil = await api.periksaTinggi(soal.seed, id);
      skor.total += 1;
      if (hasil.benar) skor.benar += 1;
    } catch (e) {
      hasil = null;
      app.append(kotakUmpan("info", e.message));
      sibuk = false;
      return;
    }
    sibuk = false;
    render();
    app.querySelector(".umpan")?.scrollIntoView({ block: "nearest" });
  }

  async function soalBaru() {
    soal = await api.soalTinggi();
    hasil = null;
    dipilih = null;
    render();
    window.scrollTo(0, 0);
  }

  function render() {
    gantiIsi(
      app,
      el("p", { class: "posisi" }, `Tunjuk Tingginya · Benar ${skor.benar} dari ${skor.total}`),
      el("h1", { tabindex: "-1" }, "Garis mana yang merupakan tinggi?"),
      el("p", {}, "Tinggi berangkat dari titik puncak dan tegak lurus dengan alas (garis biru)."),
      el("figure", { class: "gambar" }, svgSoalTinggi(soal, hasil, dipilih, pilih)),
      el(
        "div",
        { class: "pilih-alas", role: "group", "aria-label": "Pilih garis" },
        soal.kandidat.map((k) =>
          el(
            "button",
            {
              type: "button",
              class: "opsi",
              "aria-pressed": String(k.id === dipilih),
              disabled: Boolean(hasil),
              onclick: () => pilih(k.id),
            },
            `Garis ${k.id}`,
          ),
        ),
      ),
      hasil ? kotakUmpan(hasil.benar ? "benar" : "salah", hasil.umpan_balik) : null,
      barBawah(
        el("a", { class: "tombol", href: "#/latihan" }, "Kembali"),
        hasil ? tombol("Soal baru", soalBaru, true) : null,
      ),
    );
  }
  render();
}

// ------------------------------------------------------------------ Pilah Informasi
export async function halamanLatihanPilah(app) {
  const daftar = await api.latihanPilah();
  let i = 0;

  function tampilSoal() {
    const s = daftar[i];
    const komp = buatPilah(s);
    let umpan = null;
    let benar = false;
    let sibuk = false;

    async function periksa() {
      if (sibuk) return;
      if (komp.kosong()) {
        umpan = ["info", "Tempatkan dulu semua informasinya."];
        render();
        return;
      }
      sibuk = true;
      try {
        const r = await api.periksaPilah(s.id, komp.ambil().penempatan);
        benar = r.benar;
        umpan = [r.benar ? "benar" : "salah", r.umpan_balik];
        if (r.benar) komp.kunci();
      } catch (e) {
        umpan = ["info", e.message];
      }
      sibuk = false;
      render();
      app.querySelector(".umpan")?.scrollIntoView({ block: "nearest" });
    }

    function render() {
      const terakhir = i === daftar.length - 1;
      gantiIsi(
        app,
        el("p", { class: "posisi" }, `Pilah Informasi · Soal ${i + 1} dari ${daftar.length}`),
        el("h1", { tabindex: "-1" }, s.judul),
        el("ol", { class: "cerita" }, s.cerita.map((k) => el("li", {}, k))),
        el("p", {}, el("strong", {}, s.instruksi), " Ketuk informasi, lalu ketuk kotaknya. Bisa juga diseret."),
        komp.node,
        umpan ? kotakUmpan(umpan[0], umpan[1]) : null,
        barBawah(
          el("a", { class: "tombol", href: "#/latihan" }, "Kembali"),
          benar
            ? terakhir
              ? el("a", { class: "tombol tombol-utama", href: "#/misi" }, "Selesai, ke misi")
              : tombol(
                  "Soal berikutnya",
                  () => {
                    i += 1;
                    tampilSoal();
                    window.scrollTo(0, 0);
                  },
                  true,
                )
            : tombol("Periksa", periksa, true),
        ),
      );
    }
    render();
  }
  tampilSoal();
}
