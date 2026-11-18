// Membandingkan penilaian JavaScript (versi online) dengan Python.
// Pakai:  python web-statis/uji_kesetaraan.py | node web-statis/uji_kesetaraan.mjs

import { buatSoalTinggi, periksaSoalTinggi } from "./js/lokal/generator_soal.js";
import { parseAngka, parseSatuan, samakah } from "./js/lokal/parser_angka.js";
import { hitungSkorMisi, periksaLangkah } from "./js/lokal/penilai.js";

let masukan = "";
for await (const potong of process.stdin) masukan += potong;
const d = JSON.parse(masukan);
const gagal = [];

for (const k of d.kasus) {
  const h = periksaLangkah(k.langkah, k.jawaban);
  const js = [h.benar, h.kode, h.umpan_balik];
  if (JSON.stringify(js) !== JSON.stringify(k.hasil)) {
    gagal.push(`langkah ${k.langkah.no ?? k.langkah.id} ${JSON.stringify(k.jawaban)}\n  py: ${JSON.stringify(k.hasil)}\n  js: ${JSON.stringify(js)}`);
  }
}

for (const s of d.skor) {
  const misi = d.misi.find((m) => m.id === s.misi_id);
  const r = hitungSkorMisi(misi, s.status);
  const js = [r.skor, r.maks, r.bintang, r.total_petunjuk, r.rincian];
  if (JSON.stringify(js) !== JSON.stringify(s.hasil)) gagal.push(`skor misi ${s.misi_id}: py ${JSON.stringify(s.hasil)} js ${JSON.stringify(js)}`);
}

for (const [t, py] of d.angka) {
  const js = parseAngka(t);
  const sama = py === null ? js === null : js !== null && samakah(js, py, 1e-12);
  if (!sama) gagal.push(`parse_angka(${JSON.stringify(t)}): py ${py} js ${js}`);
}
for (const [t, py] of d.satuan) {
  if (parseSatuan(t) !== py) gagal.push(`parse_satuan(${JSON.stringify(t)}): py ${py} js ${parseSatuan(t)}`);
}

for (const seed of d.seed) {
  const s = buatSoalTinggi(seed);
  const tegak = s.kandidat.filter((k) => k.dari.x === k.ke.x);
  if (tegak.length !== 1 || tegak[0].peran !== "tinggi") gagal.push(`soal tinggi seed ${seed} tidak valid`);
  if (!periksaSoalTinggi(seed, tegak[0].id).benar) gagal.push(`periksa tinggi seed ${seed}`);
}

console.log(`Kasus langkah: ${d.kasus.length}, skor: ${d.skor.length}, angka: ${d.angka.length}, soal tinggi: ${d.seed.length}`);
if (gagal.length) {
  console.log(`BERBEDA (${gagal.length}):\n` + gagal.slice(0, 20).join("\n"));
  process.exit(1);
}
console.log("SEMUA SAMA: penilaian JavaScript identik dengan Python.");
