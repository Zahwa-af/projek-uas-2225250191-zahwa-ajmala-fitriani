// Format balasan Pembimbing AI agar mudah dibaca: Markdown sederhana + rumus matematika.
//
// KEAMANAN: semua teks dimasukkan lewat textContent / createElement (dari dom.js).
// Tidak ada innerHTML, jadi HTML atau skrip di balasan AI tampil sebagai teks biasa.
//
// Yang didukung:
//  - Paragraf (baris kosong), baris baru, judul (#), daftar (- * • dan 1. 2.)
//  - **tebal**, *miring*, `kode`
//  - Rumus: $...$, $$...$$, \( ... \), \[ ... \], serta perintah LaTeX yang umum
//    (\frac, \times, \cdot, \sqrt, \text, \pi, \leq, ...)
//  - Pangkat x^2 / x^{10} → superscript, indeks s_1 / s_{12} → subscript
//  - Satuan cm2 / m2 → cm² / m², dan " x " di antara bilangan atau kata → " × "

import { el } from "./dom.js";

// ------------------------------------------------------------------ rumus LaTeX → teks
const PECAHAN_UNICODE = { "1/2": "½", "1/3": "⅓", "2/3": "⅔", "1/4": "¼", "3/4": "¾" };

const SIMBOL_LATEX = [
  ["times", "×"], ["cdot", "·"], ["div", "÷"], ["pi", "π"], ["leq", "≤"], ["le", "≤"],
  ["geq", "≥"], ["ge", "≥"], ["neq", "≠"], ["ne", "≠"], ["approx", "≈"], ["pm", "±"],
  ["circ", "°"], ["degree", "°"], ["angle", "∠"], ["triangle", "△"], ["perp", "⊥"],
  ["Rightarrow", "⇒"], ["rightarrow", "→"], ["to", "→"], ["quad", " "], ["qquad", " "],
];

function pecahan(atas, bawah) {
  const a = atas.trim();
  const b = bawah.trim();
  if (PECAHAN_UNICODE[`${a}/${b}`]) return PECAHAN_UNICODE[`${a}/${b}`];
  const bungkus = (x) => (/^[\w.,²³]+$/.test(x) ? x : `(${x})`);
  return `${bungkus(a)}/${bungkus(b)}`;
}

function latexKeTeks(s) {
  let t = s;
  for (let i = 0; i < 4; i++) {
    t = t.replace(/\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g, (_, a, b) => pecahan(a, b));
  }
  t = t.replace(/\\sqrt\s*\{([^{}]*)\}/g, "√($1)");
  t = t.replace(/\\(?:text|mathrm|mathbf|textbf|operatorname|mbox)\s*\{([^{}]*)\}/g, "$1");
  t = t.replace(/\\(?:left|right)(?![a-zA-Z])/g, "");
  t = t.replace(/\\[,;:! ]/g, " ").replace(/\\%/g, "%");
  for (const [nama, simbol] of SIMBOL_LATEX) {
    t = t.replace(new RegExp(`\\\\${nama}(?![a-zA-Z])`, "g"), simbol);
  }
  t = t.replace(/\\([a-zA-Z]+)/g, "$1"); // perintah lain: tampilkan namanya saja
  return t.replace(/\s{2,}/g, " ");
}

// ------------------------------------------------------------------ teks biasa → node
// Catatan: regex di file ini sengaja TIDAK memakai lookbehind (?<=...) karena Safari
// iOS < 16.4 tidak mendukungnya; satu regex gagal bisa membuat seluruh aplikasi tidak termuat.

function rapikanTeks(s) {
  let t = s;
  if (t.includes("\\")) t = latexKeTeks(t);
  // " x " → " × " bila ada angka di salah satu sisi ("6 x 4") atau baris berupa rumus
  // ("L = ½ x (alas x tinggi)"). Kalimat biasa seperti "nilai x dan y" tidak diubah.
  const rumus = t.includes("=");
  const kali = /([\p{L}\d)½⅓⅔¼¾²³]+)\s[xX]\s([\p{L}\d(½⅓⅔¼¾]+)/gu;
  for (let i = 0; i < 3; i++) {
    const baru = t.replace(kali, (cocok, a, b) =>
      rumus || /[\d)½⅓⅔¼¾²³]$/.test(a) || /^[\d(½⅓⅔¼¾]/.test(b) ? `${a} × ${b}` : cocok,
    );
    if (baru === t) break;
    t = baru;
  }
  // "6*4" atau "alas * tinggi" → tanda kali (bintang untuk format tebal/miring sudah diproses)
  t = t.replace(/([\w)])\s?\*\s?(?=[\w(])/g, "$1 × ");
  // satuan luas/volume: "36 cm2" → "36 cm²"
  t = t.replace(/(\d\s?)(mm|cm|dm|km|m)([23])(?!\d)/g, (_, a, u, p) => a + u + (p === "2" ? "²" : "³"));
  return t;
}

/** Tambahkan teks ke `induk`, mengubah x^2 menjadi <sup> dan s_1 menjadi <sub>. */
function tambahTeksMatematika(induk, teks) {
  // 1,2 = pangkat · 3+4 dan 5+6 = (huruf sebelum) + indeks
  const pola = /\^\{([^{}]+)\}|\^(-?[\p{L}\d]+(?:[.,]\d+)?)|([\p{L})])_\{([^{}]+)\}|([\p{L})])_(\d+|[a-z](?!\p{L}))/gu;
  let akhir = 0;
  for (const m of teks.matchAll(pola)) {
    const sebelum = m[3] ?? m[5] ?? "";
    const awal = m.index;
    if (awal > akhir || sebelum) induk.append(teks.slice(akhir, awal) + sebelum);
    const atas = m[1] ?? m[2];
    if (atas !== undefined) induk.append(el("sup", {}, atas));
    else induk.append(el("sub", {}, m[4] ?? m[6]));
    akhir = awal + m[0].length;
  }
  if (akhir < teks.length) induk.append(teks.slice(akhir));
}

function elRumus(isi, blok = false) {
  // Nama kelas "chat-mat" (bukan "rumus") agar tidak bentrok dengan komponen isian rumus misi.
  const span = el("span", { class: blok ? "chat-mat chat-mat-blok" : "chat-mat" });
  tambahTeksMatematika(span, rapikanTeks(latexKeTeks(isi.trim())));
  return span;
}

// ------------------------------------------------------------------ format dalam baris
const POLA_INLINE = new RegExp(
  [
    String.raw`\$\$([\s\S]+?)\$\$`, // 1 rumus $$..$$
    String.raw`\\\[([\s\S]+?)\\\]`, // 2 rumus \[..\]
    String.raw`\\\(([\s\S]+?)\\\)`, // 3 rumus \(..\)
    String.raw`\$([^$\s][^$\n]*?)\$`, // 4 rumus $..$
    "`([^`\\n]+)`", // 5 kode
    String.raw`\*\*([^*\n]+?)\*\*`, // 6 tebal
    String.raw`__([^_\n]+?)__`, // 7 tebal
    String.raw`(^|[^\w*])\*([^*\s][^*\n]*?)\*(?![\w*])`, // 8 awalan, 9 miring
    String.raw`(^|[^\w])_([^_\s][^_\n]*?)_(?!\w)`, // 10 awalan, 11 miring
  ].join("|"),
  "g",
);

function tambahInline(induk, teks) {
  let akhir = 0;
  for (const m of teks.matchAll(POLA_INLINE)) {
    const awalan = m[8] ?? m[10] ?? ""; // karakter sebelum *miring* ikut dicocokkan
    const sebelum = teks.slice(akhir, m.index) + awalan;
    if (sebelum) tambahTeksMatematika(induk, rapikanTeks(sebelum));
    const rumus = m[1] ?? m[2] ?? m[3] ?? m[4];
    if (rumus !== undefined) induk.append(elRumus(rumus));
    else if (m[5] !== undefined) induk.append(el("code", {}, m[5]));
    else if (m[6] !== undefined || m[7] !== undefined) {
      const b = el("strong");
      tambahInline(b, m[6] ?? m[7]);
      induk.append(b);
    } else {
      const i = el("em");
      tambahInline(i, m[9] ?? m[11]);
      induk.append(i);
    }
    akhir = m.index + m[0].length;
  }
  if (akhir < teks.length) tambahTeksMatematika(induk, rapikanTeks(teks.slice(akhir)));
}

// ------------------------------------------------------------------ blok
const POLA_DAFTAR = /^\s*([-*•+])\s+(.*)$/;
const POLA_DAFTAR_ANGKA = /^\s*(\d+)[.)]\s+(.*)$/;
const POLA_JUDUL = /^\s*#{1,6}\s+(.*)$/;
const POLA_RUMUS_BLOK = /^\s*(?:\$\$([\s\S]+)\$\$|\\\[([\s\S]+)\\\])\s*$/;

/** Ubah teks balasan AI menjadi daftar elemen DOM yang aman. */
export function formatPesan(teks) {
  // Rumus blok yang ditulis beberapa baris digabung menjadi satu baris.
  const bersih = String(teks ?? "")
    .replace(/\r\n?/g, "\n")
    .replace(/\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]/g, (m) => m.replace(/\n+/g, " "))
    .trim();

  const hasil = [];
  let paragraf = null;
  let daftar = null;

  const tutup = () => {
    paragraf = null;
    daftar = null;
  };

  for (const baris of bersih.split("\n")) {
    if (!baris.trim() || /^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(baris)) {
      tutup();
      continue;
    }

    const rumusBlok = baris.match(POLA_RUMUS_BLOK);
    const judul = baris.match(POLA_JUDUL);
    const butir = baris.match(POLA_DAFTAR);
    const butirAngka = baris.match(POLA_DAFTAR_ANGKA);

    if (rumusBlok) {
      tutup();
      hasil.push(el("p", { class: "chat-rumus" }, elRumus(rumusBlok[1] ?? rumusBlok[2], true)));
    } else if (judul) {
      tutup();
      const p = el("p", { class: "chat-judul" });
      tambahInline(p, judul[1].replace(/\*\*/g, ""));
      hasil.push(p);
    } else if (butir || butirAngka) {
      const tag = butir ? "ul" : "ol";
      if (!daftar || daftar.tagName.toLowerCase() !== tag) {
        paragraf = null;
        daftar = el(tag);
        if (butirAngka && butirAngka[1] !== "1") daftar.setAttribute("start", butirAngka[1]);
        hasil.push(daftar);
      }
      const li = el("li");
      tambahInline(li, (butir ?? butirAngka)[2]);
      daftar.append(li);
    } else if (daftar && /^\s{2,}\S/.test(baris)) {
      // baris lanjutan dari butir daftar sebelumnya
      const li = daftar.lastElementChild;
      li.append(el("br"));
      tambahInline(li, baris.trim());
    } else {
      daftar = null;
      if (paragraf) {
        paragraf.append(el("br"));
      } else {
        paragraf = el("p");
        hasil.push(paragraf);
      }
      tambahInline(paragraf, baris.trim());
    }
  }
  return hasil;
}

/** Satu gelembung chat. Pesan siswa ditampilkan apa adanya; balasan AI diformat. */
export function elPesanChat(peran, teks) {
  const dariSiswa = peran === "siswa";
  const isi = dariSiswa
    ? el("p", { class: "chat-teks-polos" }, String(teks ?? ""))
    : formatPesan(teks);
  return el(
    "div",
    { class: `chat-pesan ${dariSiswa ? "chat-siswa" : "chat-asisten"}` },
    el("span", { class: "chat-label" }, dariSiswa ? "Kamu" : "Pembimbing AI"),
    el("div", { class: "chat-isi" }, isi),
  );
}
