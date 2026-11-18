// Terjemahan JavaScript dari backend/segitiga/generator_soal.py (Tunjuk Tingginya).
// Memakai PRNG sendiri, jadi seed yang sama memberi soal yang sama di browser.

const JENIS = ["lancip", "siku-siku", "tumpul"];
const Y_ALAS = 85;

const PESAN_KANDIDAT = {
  tinggi: "Tepat! Garis ini tegak lurus dengan alas dan berangkat dari titik puncak.",
  miring:
    "Garis ini memang dari titik puncak ke alas, tetapi tidak tegak lurus. Tinggi harus membentuk sudut siku-siku dengan alas.",
  sisi: "Garis ini adalah sisi segitiga, bukan tinggi. Tinggi harus tegak lurus dengan alas.",
};

function acak(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const titik = (x, y) => ({ x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10 });

export function buatSoalTinggi(seed) {
  const r = acak(seed);
  const seragam = (a, b) => a + (b - a) * r();
  const pilih = (arr) => arr[Math.floor(r() * arr.length)];
  const jenis = JENIS[seed % 3];
  const yPuncak = seragam(20, 35);
  let ax;
  let bx;
  let px;
  let sisiKe;
  if (jenis === "lancip") {
    [ax, bx] = [12, 88];
    px = seragam(32, 68);
    sisiKe = pilih([ax, bx]);
  } else if (jenis === "siku-siku") {
    [ax, bx] = [18, 88];
    px = ax;
    sisiKe = bx;
  } else {
    [ax, bx] = [45, 92];
    px = seragam(12, 25);
    sisiKe = ax;
  }
  const pilihanX = [0.2, 0.35, 0.65, 0.8].map((f) => ax + f * (bx - ax)).filter((x) => Math.abs(x - px) > 12);
  const miringX = pilih(pilihanX);

  const kandidat = [
    { peran: "tinggi", dari: titik(px, yPuncak), ke: titik(px, Y_ALAS) },
    { peran: "miring", dari: titik(px, yPuncak), ke: titik(miringX, Y_ALAS) },
    { peran: "sisi", dari: titik(px, yPuncak), ke: titik(sisiKe, Y_ALAS) },
  ];
  for (let i = kandidat.length - 1; i > 0; i--) {
    const j = Math.floor(r() * (i + 1));
    [kandidat[i], kandidat[j]] = [kandidat[j], kandidat[i]];
  }
  kandidat.forEach((k, i) => (k.id = "PQR"[i]));
  return {
    seed,
    jenis,
    titik: { A: titik(ax, Y_ALAS), B: titik(bx, Y_ALAS), C: titik(px, yPuncak) },
    kandidat,
  };
}

export function soalTinggiPublik(soal) {
  return { ...soal, kandidat: soal.kandidat.map(({ peran, ...k }) => k) };
}

export function periksaSoalTinggi(seed, pilihan) {
  const soal = buatSoalTinggi(seed);
  const benarId = soal.kandidat.find((c) => c.peran === "tinggi").id;
  const dipilih = soal.kandidat.find((c) => c.id === pilihan);
  if (!dipilih) return { benar: false, umpan_balik: "Pilih salah satu garis: P, Q, atau R.", kunci: null };
  let pesan = PESAN_KANDIDAT[dipilih.peran];
  if (soal.jenis === "tumpul") pesan += " Pada segitiga tumpul, tinggi jatuh di perpanjangan alas.";
  return { benar: dipilih.peran === "tinggi", umpan_balik: pesan, kunci: benarId };
}
