// Gambar segitiga SVG. Aturan warna: alas biru, tinggi oranye putus-putus, sisi lain abu-abu.
// Label ditulis langsung pada gambar (spatial contiguity, EL02).

import { el, fmt, svgEl } from "./dom.js";
import * as G from "./geometri.js";

const PAD = 36;

const titikTeks = (daftar) => daftar.map((p) => `${p.x},${p.y}`).join(" ");

function teksUkuran(nama, nilai, satuan, tanpaAngka) {
  return tanpaAngka ? nama : `${nama} ${fmt(nilai)} ${satuan || ""}`.trim();
}

function label(p, teks, kelas, anchor = "middle") {
  return svgEl(
    "text",
    {
      x: p.x,
      y: p.y,
      class: `label ${kelas}`,
      "text-anchor": anchor,
      "dominant-baseline": "middle",
    },
    teks,
  );
}

const garis = (a, b, kelas) => svgEl("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: kelas });
const poligon = (titik, kelas) => svgEl("polygon", { points: titikTeks(titik), class: kelas });

function tandaSiku(kaki, arahA, arahB, kelas = "tanda-siku", s = 11) {
  const p1 = G.tambah(kaki, G.kali(arahA, s));
  const p2 = G.tambah(p1, G.kali(arahB, s));
  const p3 = G.tambah(kaki, G.kali(arahB, s));
  return svgEl("polyline", { points: titikTeks([p1, p2, p3]), class: kelas });
}

/**
 * Lapisan segitiga dengan alas AB dan puncak C (koordinat SVG).
 * Menggambar garis tinggi tegak lurus ke alas (atau perpanjangannya).
 */
export function lapisanSegitiga({
  A,
  B,
  C,
  teksAlas,
  teksTinggi,
  animasiTinggi = false,
  tampilTinggi = true,
  arsir = null,
}) {
  const g = svgEl("g");
  const { titik: D, t } = G.proyeksi(C, A, B);
  const arahAlas = G.satuan(G.kurang(B, A));
  const arahSiku = t < 0.5 ? arahAlas : G.kali(arahAlas, -1);

  g.append(poligon([A, B, C], "isi-segitiga"));

  if (arsir) {
    const E = G.tambah(A, G.kali(G.kurang(B, A), arsir.bagian));
    g.append(poligon([A, E, C], "arsir"), garis(C, E, "garis-perpanjangan"));
    if (arsir.label) g.append(label(G.pusatBerat(A, E, C), arsir.label, "label-kecil"));
    if (arsir.label_sisa) g.append(label(G.pusatBerat(E, B, C), arsir.label_sisa, "label-kecil"));
  }

  if (tampilTinggi && (t < 0 || t > 1)) {
    g.append(garis(t < 0 ? A : B, D, "garis-perpanjangan"));
  }

  g.append(garis(A, C, "garis-sisi"), garis(B, C, "garis-sisi"), garis(A, B, "garis-alas"));

  if (tampilTinggi && G.jarak(C, D) > 1) {
    const arahTinggi = G.satuan(G.kurang(C, D));
    g.append(
      garis(C, D, `garis-tinggi${animasiTinggi ? " anim-tinggi" : ""}`),
      tandaSiku(D, arahSiku, arahTinggi),
    );
    if (teksTinggi) {
      const p = G.tambah(G.titikTengah(C, D), G.kali(arahSiku, 8));
      const lbl = label(p, teksTinggi, "label-tinggi", arahSiku.x >= 0 ? "start" : "end");
      if (animasiTinggi) lbl.classList.add("anim-muncul");
      g.append(lbl);
    }
  }

  if (teksAlas) {
    let n = { x: -arahAlas.y, y: arahAlas.x };
    if (G.dot(n, G.kurang(C, A)) > 0) n = G.kali(n, -1);
    g.append(label(G.tambah(G.titikTengah(A, B), G.kali(n, 20)), teksAlas, "label-alas"));
  }
  return g;
}

function lebarRelatif(spec) {
  const p = spec.puncak ?? 0.35;
  return { p, min: Math.min(0, p), lebar: Math.max(1, p) - Math.min(0, p) };
}

export function ukurSkala(spec, W = 340, Hmaks = 230) {
  const { lebar } = lebarRelatif(spec);
  return Math.min((W - 2 * PAD) / (lebar * spec.alas), (Hmaks - 2 * PAD) / spec.tinggi);
}

/** Segitiga dengan alas mendatar. spec: {alas, tinggi, satuan, puncak, tanpa_angka, arsir}. */
export function svgSegitiga(spec, { W = 340, Hmaks = 230, skala = null, H = null, animasiTinggi = false } = {}) {
  const { p, min, lebar } = lebarRelatif(spec);
  const s = skala ?? ukurSkala(spec, W, Hmaks);
  const tinggiPx = spec.tinggi * s;
  const tinggiSvg = H ?? tinggiPx + 2 * PAD;
  const ox = (W - lebar * spec.alas * s) / 2 - min * spec.alas * s;
  const yb = tinggiSvg - PAD;
  const A = { x: ox, y: yb };
  const B = { x: ox + spec.alas * s, y: yb };
  const C = { x: ox + p * spec.alas * s, y: yb - tinggiPx };

  const satuan = spec.satuan || "";
  const deskripsi = spec.tanpa_angka
    ? "Segitiga dengan alas berwarna biru dan tinggi oranye putus-putus."
    : `Segitiga dengan alas ${fmt(spec.alas)} ${satuan} dan tinggi ${fmt(spec.tinggi)} ${satuan}.`;
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${tinggiSvg}`, role: "img", "aria-label": deskripsi });
  svg.append(
    lapisanSegitiga({
      A,
      B,
      C,
      teksAlas: teksUkuran("alas", spec.alas, satuan, spec.tanpa_angka),
      teksTinggi: teksUkuran("tinggi", spec.tinggi, satuan, spec.tanpa_angka),
      animasiTinggi,
      arsir: spec.arsir,
    }),
  );
  return svg;
}

function gambarDua(spec) {
  const W = 220;
  const Hmaks = 200;
  const daftar = spec.segitiga.map((s) => ({ ...s, satuan: spec.satuan, tanpa_angka: spec.tanpa_angka }));
  // Skala sama agar ukuran kedua bendera bisa dibandingkan secara visual.
  const skala = Math.min(...daftar.map((s) => ukurSkala(s, W, Hmaks)));
  const H = Math.max(...daftar.map((s) => s.tinggi * skala)) + 2 * PAD;
  return el(
    "div",
    { class: "gambar-dua" },
    daftar.map((s) =>
      el("figure", { class: "gambar" }, svgSegitiga(s, { W, skala, H }), el("figcaption", {}, s.nama)),
    ),
  );
}

/** Persegi panjang dibagi diagonal: menunjukkan segitiga = ½ persegi panjang. */
export function svgPersegiPanjangDibagi(spec, { animasi = false } = {}) {
  const W = 380;
  const kiri = 100;
  const kanan = 30;
  const s = Math.min((W - kiri - kanan) / spec.alas, 170 / spec.tinggi);
  const w = spec.alas * s;
  const h = spec.tinggi * s;
  const H = h + 2 * PAD;
  const ox = kiri;
  const yb = H - PAD;
  const P0 = { x: ox, y: yb };
  const P1 = { x: ox + w, y: yb };
  const P2 = { x: ox + w, y: yb - h };
  const P3 = { x: ox, y: yb - h };
  const satuan = spec.satuan || "";
  const svg = svgEl("svg", {
    viewBox: `0 0 ${W} ${H}`,
    role: "img",
    "aria-label": "Persegi panjang dibagi garis diagonal menjadi dua segitiga yang sama besar.",
  });
  const atas = poligon([P1, P2, P3], `arsir${animasi ? " anim-gabung" : ""}`);
  svg.append(
    poligon([P0, P1, P3], "isi-segitiga"),
    atas,
    garis(P3, P2, "garis-sisi"),
    garis(P1, P2, "garis-sisi"),
    garis(P1, P3, "garis-sisi"),
    garis(P0, P1, "garis-alas"),
    garis(P3, P0, "garis-tinggi"),
    tandaSiku(P0, { x: 1, y: 0 }, { x: 0, y: -1 }),
    label({ x: ox + w / 2, y: yb + 20 }, teksUkuran("alas", spec.alas, satuan, spec.tanpa_angka), "label-alas"),
    label({ x: ox - 8, y: yb - h / 2 }, teksUkuran("tinggi", spec.tinggi, satuan, spec.tanpa_angka), "label-tinggi", "end"),
    label(G.pusatBerat(P0, P1, P3), "segitiga", "label-kecil"),
    label(G.pusatBerat(P1, P2, P3), "segitiga", "label-kecil"),
  );
  return svg;
}

/** Segitiga kecil dari titik bebas (sumbu y ke atas), untuk jenis-jenis segitiga & keliling. */
export function svgBentuk(titik, { labelSisi = null, sikuDi = null, W = 160, H = 130, pad = 24 } = {}) {
  const xs = titik.map((p) => p.x);
  const ys = titik.map((p) => p.y);
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const lebar = Math.max(...xs) - minX || 1;
  const tinggi = Math.max(...ys) - minY || 1;
  const s = Math.min((W - 2 * pad) / lebar, (H - 2 * pad) / tinggi);
  const ox = (W - lebar * s) / 2;
  const oy = (H - tinggi * s) / 2;
  const P = titik.map((p) => ({ x: ox + (p.x - minX) * s, y: H - oy - (p.y - minY) * s }));
  const pusat = G.pusatBerat(...P);

  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, "aria-hidden": "true" });
  svg.append(poligon(P, "isi-segitiga"));
  for (let i = 0; i < 3; i++) {
    const a = P[i];
    const b = P[(i + 1) % 3];
    svg.append(garis(a, b, "garis-sisi"));
    if (labelSisi?.[i]) {
      const m = G.titikTengah(a, b);
      const keluar = G.satuan(G.kurang(m, pusat));
      svg.append(label(G.tambah(m, G.kali(keluar, 13)), labelSisi[i], "label-sisi label-kecil"));
    }
  }
  if (sikuDi !== null) {
    const v = P[sikuDi];
    const a = G.satuan(G.kurang(P[(sikuDi + 1) % 3], v));
    const b = G.satuan(G.kurang(P[(sikuDi + 2) % 3], v));
    svg.append(tandaSiku(v, a, b, "tanda-siku-netral", 10));
  }
  return svg;
}

/** Pembungkus: pilih gambar sesuai spec.tipe. */
export function gambar(spec, opsi = {}) {
  if (!spec) return null;
  if (spec.tipe === "dua_segitiga") return gambarDua(spec);
  const isi =
    spec.tipe === "persegi_panjang_dibagi"
      ? svgPersegiPanjangDibagi(spec, opsi)
      : svgSegitiga(spec, opsi);
  return el("figure", { class: "gambar" }, isi, spec.judul ? el("figcaption", {}, spec.judul) : null);
}

/**
 * Segitiga interaktif (F-01): titik sudut dapat digeser di atas kotak-kotak,
 * siswa memilih sisi mana yang menjadi alas, tinggi menyesuaikan.
 */
export function segitigaInteraktif() {
  const U = 30;
  const KOLOM = 12;
  const BARIS = 8;
  const P = 22;
  const W = KOLOM * U + 2 * P;
  const H = BARIS * U + 2 * P;
  const titik = { A: { x: 1, y: 7 }, B: { x: 9, y: 7 }, C: { x: 4, y: 2 } };
  let alas = ["A", "B"];
  let aktif = null;

  const keSvg = (q) => ({ x: P + q.x * U, y: P + q.y * U });
  const svg = svgEl("svg", {
    viewBox: `0 0 ${W} ${H}`,
    role: "img",
    "aria-label": "Segitiga interaktif. Geser titik A, B, atau C.",
  });

  const grid = svgEl("g");
  for (let i = 0; i <= KOLOM; i++) grid.append(garis(keSvg({ x: i, y: 0 }), keSvg({ x: i, y: BARIS }), "grid-kotak"));
  for (let j = 0; j <= BARIS; j++) grid.append(garis(keSvg({ x: 0, y: j }), keSvg({ x: KOLOM, y: j }), "grid-kotak"));
  const lapisan = svgEl("g");
  const lapisanTitik = svgEl("g");
  svg.append(grid, lapisan, lapisanTitik);

  const bacaan = el("p", { class: "bacaan", "aria-live": "polite" });
  const tombolAlas = {};
  const pilihAlas = el(
    "div",
    { class: "pilih-alas", role: "group", "aria-label": "Pilih sisi alas" },
    el("span", { class: "teks-redup" }, "Pilih alas:"),
    [["A", "B"], ["B", "C"], ["C", "A"]].map((pasangan) => {
      const b = el(
        "button",
        {
          type: "button",
          class: "opsi",
          onclick: () => {
            alas = pasangan;
            gambarUlang();
          },
        },
        pasangan.join(""),
      );
      tombolAlas[pasangan.join("")] = b;
      return b;
    }),
  );

  function keGrid(e) {
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const q = pt.matrixTransform(svg.getScreenCTM().inverse());
    return {
      x: Math.min(KOLOM, Math.max(0, Math.round((q.x - P) / U))),
      y: Math.min(BARIS, Math.max(0, Math.round((q.y - P) / U))),
    };
  }

  function cobaPindah(nama, q) {
    const lain = Object.entries(titik).filter(([n]) => n !== nama).map(([, v]) => v);
    if (G.luasTigaTitik(q, lain[0], lain[1]) < 0.5) return; // jangan sampai segaris
    titik[nama] = q;
    gambarUlang();
  }

  const pegangan = {};
  for (const nama of ["A", "B", "C"]) {
    const area = svgEl("circle", { r: 18, class: "pegangan", tabindex: "0", "aria-label": `Titik ${nama}. Geser atau pakai tombol panah.` });
    const titikNyata = svgEl("circle", { r: 7, class: "titik-sudut" });
    const huruf = label({ x: 0, y: 0 }, nama, "");
    area.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      aktif = nama;
      area.setPointerCapture(e.pointerId);
    });
    area.addEventListener("pointermove", (e) => {
      if (aktif === nama) cobaPindah(nama, keGrid(e));
    });
    const lepas = () => {
      aktif = null;
    };
    area.addEventListener("pointerup", lepas);
    area.addEventListener("pointercancel", lepas);
    area.addEventListener("keydown", (e) => {
      const arah = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
      if (!arah) return;
      e.preventDefault();
      const q = titik[nama];
      cobaPindah(nama, {
        x: Math.min(KOLOM, Math.max(0, q.x + arah[0])),
        y: Math.min(BARIS, Math.max(0, q.y + arah[1])),
      });
    });
    pegangan[nama] = { area, titikNyata, huruf };
    lapisanTitik.append(titikNyata, huruf, area);
  }

  function gambarUlang() {
    const [i, j] = alas;
    const k = ["A", "B", "C"].find((n) => !alas.includes(n));
    lapisan.replaceChildren(
      lapisanSegitiga({ A: keSvg(titik[i]), B: keSvg(titik[j]), C: keSvg(titik[k]), teksAlas: "alas", teksTinggi: "tinggi" }),
    );
    const pusat = G.pusatBerat(...Object.values(titik).map(keSvg));
    for (const [nama, q] of Object.entries(titik)) {
      const p = keSvg(q);
      const { area, titikNyata, huruf } = pegangan[nama];
      area.setAttribute("cx", p.x);
      area.setAttribute("cy", p.y);
      titikNyata.setAttribute("cx", p.x);
      titikNyata.setAttribute("cy", p.y);
      const keluar = G.tambah(p, G.kali(G.satuan(G.kurang(p, pusat)), 18));
      huruf.setAttribute("x", keluar.x);
      huruf.setAttribute("y", keluar.y);
    }
    for (const [nama, b] of Object.entries(tombolAlas)) {
      b.setAttribute("aria-pressed", String(nama === alas.join("")));
    }
    const a = G.jarak(titik[i], titik[j]);
    const L = G.luasTigaTitik(titik.A, titik.B, titik.C);
    const t = (2 * L) / a;
    bacaan.replaceChildren(
      el("span", {}, `Alas ${i}${j} = ${fmt(a, 1)} kotak, tinggi = ${fmt(t, 1)} kotak.`),
      el("br"),
      el("strong", {}, `Luas = ½ × alas × tinggi = ${fmt(L, 1)} kotak persegi`),
    );
  }

  gambarUlang();
  return el("div", { class: "interaktif" }, pilihAlas, el("figure", { class: "gambar" }, svg), bacaan);
}
