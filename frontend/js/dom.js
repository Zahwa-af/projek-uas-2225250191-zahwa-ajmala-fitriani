// Pembuat elemen DOM yang aman: teks selalu lewat textContent (bukan innerHTML).

const SVG_NS = "http://www.w3.org/2000/svg";

function terapkan(node, attrs) {
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k.startsWith("on") && typeof v === "function") {
      node.addEventListener(k.slice(2), v);
    } else {
      node.setAttribute(k, v === true ? "" : String(v));
    }
  }
}

function tambahAnak(node, anak) {
  for (const a of anak.flat(Infinity)) {
    if (a === null || a === undefined || a === false) continue;
    node.append(a instanceof Node ? a : document.createTextNode(String(a)));
  }
}

export function el(tag, attrs = {}, ...anak) {
  const node = document.createElement(tag);
  terapkan(node, attrs);
  tambahAnak(node, anak);
  return node;
}

export function svgEl(tag, attrs = {}, ...anak) {
  const node = document.createElementNS(SVG_NS, tag);
  terapkan(node, attrs);
  tambahAnak(node, anak);
  return node;
}

/** Format angka Indonesia: 1200 → "1.200", 1.8 → "1,8". */
export function fmt(n, maks = 2) {
  return Number(n).toLocaleString("id-ID", { maximumFractionDigits: maks });
}

/** Ganti isi wadah. null/false dilewati (replaceChildren asli mengubah null menjadi teks "null"). */
export function gantiIsi(wadah, ...anak) {
  wadah.replaceChildren(...anak.flat(Infinity).filter((a) => a !== null && a !== undefined && a !== false));
}

export function bintangTeks(n) {
  return el(
    "span",
    { class: "bintang", "aria-label": `${n} dari 3 bintang` },
    "★".repeat(n) + "☆".repeat(3 - n),
  );
}

export function barBawah(kiri, ...kanan) {
  return el("div", { class: "bar-bawah" }, kiri, el("div", { class: "kanan" }, ...kanan));
}

export function tombol(teks, onclick, utama = false, attrs = {}) {
  return el(
    "button",
    { type: "button", class: utama ? "tombol tombol-utama" : "tombol", onclick, ...attrs },
    teks,
  );
}

export function kotakUmpan(jenis, teks) {
  const ikon = { benar: "✓", salah: "!", info: "i" }[jenis];
  return el(
    "div",
    { class: `umpan umpan-${jenis}`, role: "status", tabindex: "-1" },
    el("span", { class: "ikon", "aria-hidden": "true" }, ikon),
    el("span", {}, teks),
  );
}
