// Materi belajar: satu konsep per layar, tombol Kembali / Ulangi / Lanjut (EL01, EL04).

import { barBawah, el, gantiIsi, tombol } from "../dom.js";
import { segitigaDariSisi } from "../geometri.js";
import { gambar, segitigaInteraktif, svgBentuk } from "../segitiga-svg.js";

function deret(daftar) {
  return el(
    "div",
    { class: "deret-bentuk" },
    daftar.map(([titik, opsi, nama]) =>
      el("figure", { class: "gambar" }, svgBentuk(titik, opsi), el("figcaption", {}, nama)),
    ),
  );
}

const SOAL_CONTOH =
  "Hiasan dinding berbentuk segitiga dengan alas 40 cm dan tinggi 30 cm. Ada 3 hiasan. Berapa luas kertas untuk semua hiasan?";

const LANGKAH_CONTOH = [
  ["Diketahui", "alas = 40 cm, tinggi = 30 cm, banyak hiasan = 3."],
  ["Ditanyakan", "luas kertas untuk 3 hiasan."],
  ["Rumus", "L = ½ × alas × tinggi."],
  ["Hitung", "L = ½ × 40 × 30 = ½ × 1.200 = 600 cm². Untuk 3 hiasan: 3 × 600 = 1.800 cm²."],
  ["Simpulkan", "Jadi, kertas yang dibutuhkan 1.800 cm²."],
];

function layarContoh(k) {
  return {
    judul: `Langkah ${k}: ${LANGKAH_CONTOH[k - 1][0]}`,
    teks: k === 1 ? ["Baca soalnya, lalu ikuti langkahnya satu per satu."] : [],
    gambar: () =>
      el(
        "div",
        {},
        el("p", { class: "contoh-soal" }, SOAL_CONTOH),
        gambar({ tipe: "segitiga", alas: 40, tinggi: 30, satuan: "cm", puncak: 0.4, judul: "1 hiasan (ada 3)" }),
      ),
    langkah: LANGKAH_CONTOH.slice(0, k).map(([j, t]) => `${j}: ${t}`),
  };
}

export const TOPIK = [
  {
    judul: "Jenis-jenis segitiga",
    ringkas: "Menurut sisi dan menurut sudut.",
    layar: [
      {
        judul: "Menurut panjang sisi",
        teks: [
          "Sama sisi: ketiga sisinya sama panjang.",
          "Sama kaki: dua sisinya sama panjang.",
          "Sembarang: ketiga sisinya berbeda panjang.",
        ],
        gambar: () =>
          deret([
            [segitigaDariSisi(5, 5, 5), { labelSisi: ["5", "5", "5"] }, "Sama sisi"],
            [segitigaDariSisi(5, 5, 3), { labelSisi: ["3", "5", "5"] }, "Sama kaki"],
            [segitigaDariSisi(4, 5, 6), { labelSisi: ["6", "4", "5"] }, "Sembarang"],
          ]),
      },
      {
        judul: "Menurut besar sudut",
        teks: [
          "Lancip: ketiga sudutnya kurang dari 90°.",
          "Siku-siku: ada satu sudut tepat 90° (tanda kotak kecil).",
          "Tumpul: ada satu sudut lebih dari 90°.",
        ],
        gambar: () =>
          deret([
            [segitigaDariSisi(5, 5.5, 6), {}, "Lancip"],
            [[{ x: 0, y: 0 }, { x: 4, y: 0 }, { x: 0, y: 3 }], { sikuDi: 0 }, "Siku-siku"],
            [[{ x: 0, y: 0 }, { x: 5, y: 0 }, { x: -2.5, y: 2.5 }], {}, "Tumpul"],
          ]),
      },
    ],
  },
  {
    judul: "Alas dan tinggi",
    ringkas: "Bagian terpenting untuk menghitung luas.",
    layar: [
      {
        judul: "Apa itu alas dan tinggi?",
        teks: [
          "Alas adalah sisi yang menjadi dasar segitiga.",
          "Tinggi adalah garis dari titik puncak yang tegak lurus ke alas.",
        ],
        gambar: () => gambar({ tipe: "segitiga", alas: 6, tinggi: 4, puncak: 0.35, tanpa_angka: true }, { animasiTinggi: true }),
        catatan: "Garis biru = alas. Garis oranye putus-putus = tinggi. Kotak kecil = sudut siku-siku.",
      },
      {
        judul: "Tinggi di luar segitiga",
        teks: [
          "Pada segitiga tumpul, tinggi bisa jatuh di luar segitiga.",
          "Alas diperpanjang dulu (garis abu-abu putus-putus), lalu tinggi ditarik tegak lurus.",
        ],
        gambar: () => gambar({ tipe: "segitiga", alas: 5, tinggi: 4, puncak: -0.45, tanpa_angka: true }, { animasiTinggi: true }),
      },
      {
        judul: "Tinggi pada segitiga siku-siku",
        teks: [
          "Pada segitiga siku-siku, sisi tegaknya adalah tinggi.",
          "Sisi miring bukan tinggi, karena tidak tegak lurus dengan alas.",
        ],
        gambar: () => gambar({ tipe: "segitiga", alas: 6, tinggi: 4, puncak: 0, tanpa_angka: true }, { animasiTinggi: true }),
      },
      {
        judul: "Coba sendiri",
        teks: [
          "Geser titik A, B, atau C. Lalu pilih sisi yang menjadi alas.",
          "Tinggi selalu tegak lurus dengan alas yang dipilih.",
        ],
        gambar: segitigaInteraktif,
        catatan: "Ganti alas AB, BC, dan CA. Apakah luasnya berubah?",
      },
    ],
  },
  {
    judul: "Keliling",
    ringkas: "Panjang seluruh tepi segitiga.",
    layar: [
      {
        judul: "Apa itu keliling?",
        teks: ["Keliling adalah panjang seluruh tepi segitiga.", "Caranya: jumlahkan ketiga sisinya."],
        rumus: "K = sisi 1 + sisi 2 + sisi 3",
        gambar: () =>
          el("figure", { class: "gambar" }, svgBentuk(segitigaDariSisi(5, 6, 7), { labelSisi: ["7 cm", "5 cm", "6 cm"], W: 300, H: 220, pad: 40 })),
      },
      {
        judul: "Contoh keliling",
        teks: ["Sisi-sisinya 5 cm, 6 cm, dan 7 cm."],
        langkah: ["K = 5 + 6 + 7", "K = 18 cm"],
        gambar: () =>
          el("figure", { class: "gambar" }, svgBentuk(segitigaDariSisi(5, 6, 7), { labelSisi: ["7 cm", "5 cm", "6 cm"], W: 300, H: 220, pad: 40 })),
        catatan: "Satuan keliling adalah satuan panjang: cm, bukan cm².",
      },
    ],
  },
  {
    judul: "Luas",
    ringkas: "Dari persegi panjang ke rumus ½ × alas × tinggi.",
    layar: [
      {
        judul: "Mulai dari persegi panjang",
        teks: [
          "Luas persegi panjang = alas × tinggi.",
          "Garis diagonal membagi persegi panjang menjadi 2 segitiga yang sama.",
        ],
        gambar: () => gambar({ tipe: "persegi_panjang_dibagi", alas: 6, tinggi: 4, tanpa_angka: true }, { animasi: true }),
      },
      {
        judul: "Rumus luas segitiga",
        teks: ["Satu segitiga adalah setengah dari persegi panjang.", "Jadi, luas segitiga = setengah dari alas × tinggi."],
        rumus: "L = ½ × alas × tinggi",
        gambar: () => gambar({ tipe: "segitiga", alas: 6, tinggi: 4, puncak: 0.4, tanpa_angka: true }),
      },
      {
        judul: "Contoh luas",
        teks: ["Alas 10 cm dan tinggi 6 cm."],
        langkah: ["L = ½ × alas × tinggi", "L = ½ × 10 × 6", "L = ½ × 60", "L = 30 cm²"],
        gambar: () => gambar({ tipe: "segitiga", alas: 10, tinggi: 6, satuan: "cm", puncak: 0.3 }),
      },
      {
        judul: "Hati-hati!",
        teks: [
          "Jangan lupa dikali ½. Alas × tinggi saja adalah luas persegi panjang.",
          "Satuan luas memakai pangkat dua: cm² atau m².",
        ],
        gambar: () => gambar({ tipe: "persegi_panjang_dibagi", alas: 10, tinggi: 6, satuan: "cm" }),
        catatan: "10 × 6 = 60 cm² adalah persegi panjang. Segitiganya hanya 30 cm².",
      },
    ],
  },
  {
    judul: "Langkah soal cerita",
    ringkas: "Diketahui → Ditanyakan → Rumus → Hitung → Simpulkan.",
    layar: [1, 2, 3, 4, 5].map(layarContoh),
  },
];

export function halamanDaftarBelajar(app) {
  app.append(
    el("h1", { tabindex: "-1" }, "Belajar"),
    el("p", {}, "Pilih topik. Setiap layar berisi satu konsep. Atur sendiri temponya."),
    el(
      "ol",
      { class: "menu" },
      TOPIK.map((t, i) =>
        el(
          "li",
          {},
          el(
            "a",
            { class: "kartu-menu", href: `#/belajar/${i + 1}/1` },
            el("span", { class: "nomor", "aria-hidden": "true" }, String(i + 1)),
            el("span", {}, el("strong", {}, t.judul), el("span", { class: "teks-redup" }, t.ringkas)),
          ),
        ),
      ),
    ),
    barBawah(el("a", { class: "tombol", href: "#/" }, "Beranda"), el("a", { class: "tombol tombol-utama", href: "#/belajar/1/1" }, "Mulai dari awal")),
  );
}

export function halamanTopik(app, tTeks, lTeks = "1") {
  const t = Math.min(Math.max(Number(tTeks), 1), TOPIK.length);
  const topik = TOPIK[t - 1];
  const l = Math.min(Math.max(Number(lTeks) || 1, 1), topik.layar.length);
  const layar = topik.layar[l - 1];
  const terakhirTopik = l === topik.layar.length;
  const terakhirSemua = terakhirTopik && t === TOPIK.length;

  function render() {
    gantiIsi(
      app,
      el("p", { class: "posisi" }, `${t}. ${topik.judul} · Layar ${l} dari ${topik.layar.length}`),
      el(
        "div",
        { class: "tata-langkah" },
        el("div", { class: "kolom-gambar" }, layar.gambar ? layar.gambar() : null),
        el(
          "div",
          {},
          el("h1", { tabindex: "-1" }, layar.judul),
          layar.teks.map((k) => el("p", {}, k)),
          layar.rumus ? el("p", { class: "rumus-besar" }, layar.rumus) : null,
          layar.langkah
            ? el(
                "ol",
                { class: "langkah-contoh" },
                layar.langkah.map((k, i) => el("li", { class: i === layar.langkah.length - 1 ? "baru" : null }, k)),
              )
            : null,
          layar.catatan ? el("p", { class: "teks-redup" }, layar.catatan) : null,
        ),
      ),
      barBawah(
        el("a", { class: "tombol", href: l > 1 ? `#/belajar/${t}/${l - 1}` : "#/belajar" }, "Kembali"),
        tombol("Ulangi", () => {
          render();
          app.querySelector("h1")?.focus();
        }),
        el(
          "a",
          {
            class: "tombol tombol-utama",
            href: terakhirSemua ? "#/latihan" : terakhirTopik ? `#/belajar/${t + 1}/1` : `#/belajar/${t}/${l + 1}`,
          },
          terakhirSemua ? "Ke latihan" : terakhirTopik ? "Topik berikutnya" : "Lanjut",
        ),
      ),
    );
  }
  render();
}
