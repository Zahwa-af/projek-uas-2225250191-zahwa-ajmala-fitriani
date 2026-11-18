// Terjemahan JavaScript dari backend/segitiga/parser_angka.py (versi online tanpa server).
// Jika mengubah aturan, ubah versi Python dulu, lalu jalankan uji kesetaraan (web-statis/uji_kesetaraan.mjs).

export const PECAHAN_UNICODE = {
  "½": 1 / 2, "⅓": 1 / 3, "⅔": 2 / 3, "¼": 1 / 4, "¾": 3 / 4,
  "⅕": 1 / 5, "⅖": 2 / 5, "⅗": 3 / 5, "⅘": 4 / 5,
};

const SATUAN_DI_AKHIR = /(cm|mm|m)(\^?2|²)?$/;
const RIBUAN_TITIK = /^-?[1-9]\d{0,2}(\.\d{3})+$/;
const RIBUAN_KOMA = /^-?[1-9]\d{0,2}(,\d{3}){2,}$/;
const ANGKA_BIASA = /^-?\d+(\.\d+)?$/;

export const TOLERANSI_RELATIF = 0.005;

function bersihkan(teks) {
  let t = teks.trim().toLowerCase().replace(/ /g, "").replace(/−/g, "-");
  if (t.startsWith("rp")) t = t.slice(2).replace(/^\.+/, "");
  return t.replace(SATUAN_DI_AKHIR, "");
}

const hitung = (t, c) => t.split(c).length - 1;

function keAngka(t) {
  if (!t) return null;
  if (t.includes(",") && t.includes(".")) {
    t = t.lastIndexOf(",") > t.lastIndexOf(".") ? t.replace(/\./g, "").replace(",", ".") : t.replace(/,/g, "");
  } else if (t.includes(",")) {
    if (hitung(t, ",") === 1) t = t.replace(",", ".");
    else if (RIBUAN_KOMA.test(t)) t = t.replace(/,/g, "");
    else return null;
  } else if (t.includes(".")) {
    if (RIBUAN_TITIK.test(t)) t = t.replace(/\./g, "");
    else if (hitung(t, ".") > 1) return null;
  }
  if (!ANGKA_BIASA.test(t)) return null;
  return Number(t);
}

export function parseAngka(teks) {
  if (teks === null || teks === undefined || typeof teks === "boolean") return null;
  if (typeof teks === "number") return teks;
  const t = bersihkan(String(teks));
  if (t in PECAHAN_UNICODE) return PECAHAN_UNICODE[t];
  if (hitung(t, "/") === 1) {
    const [atas, bawah] = t.split("/");
    const a = keAngka(atas);
    const b = keAngka(bawah);
    if (a === null || b === null || b === 0) return null;
    return a / b;
  }
  return keAngka(t);
}

export function parseSatuan(teks) {
  if (!teks) return null;
  const t = String(teks).trim().toLowerCase().replace(/ /g, "");
  if (t === "rp") return "Rp";
  const m = t.match(/^(cm|mm|m)(\^?2|²)?$/);
  if (!m) return null;
  return m[1] + (m[2] ? "²" : "");
}

export function samakah(nilai, target, toleransi = TOLERANSI_RELATIF) {
  if (target === 0) return Math.abs(nilai) < 1e-9;
  return Math.abs(nilai - target) / Math.abs(target) <= toleransi;
}
