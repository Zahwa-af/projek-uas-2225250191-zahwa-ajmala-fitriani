// Perhitungan geometri untuk MENGGAMBAR (posisi garis tinggi, label).
// Penilaian jawaban tetap di Python.

export const tambah = (a, b) => ({ x: a.x + b.x, y: a.y + b.y });
export const kurang = (a, b) => ({ x: a.x - b.x, y: a.y - b.y });
export const kali = (a, k) => ({ x: a.x * k, y: a.y * k });
export const dot = (a, b) => a.x * b.x + a.y * b.y;
export const panjang = (a) => Math.hypot(a.x, a.y);
export const jarak = (a, b) => panjang(kurang(a, b));
export const titikTengah = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });

export function satuan(v) {
  const p = panjang(v) || 1;
  return { x: v.x / p, y: v.y / p };
}

/** Proyeksi titik p ke garis AB. t = 0 di A, t = 1 di B; t < 0 atau t > 1 berarti di perpanjangan. */
export function proyeksi(p, a, b) {
  const ab = kurang(b, a);
  const t = dot(kurang(p, a), ab) / dot(ab, ab);
  return { titik: tambah(a, kali(ab, t)), t };
}

export function luasTigaTitik(a, b, c) {
  return Math.abs((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) / 2;
}

export function pusatBerat(...titik) {
  const n = titik.length;
  return {
    x: titik.reduce((s, p) => s + p.x, 0) / n,
    y: titik.reduce((s, p) => s + p.y, 0) / n,
  };
}

/** Titik sudut segitiga dari panjang sisi: AB = c (mendatar), BC = a, AC = b. Sumbu y ke atas. */
export function segitigaDariSisi(a, b, c) {
  const x = (b * b + c * c - a * a) / (2 * c);
  const y = Math.sqrt(Math.max(0, b * b - x * x));
  return [
    { x: 0, y: 0 },
    { x: c, y: 0 },
    { x, y },
  ];
}
