// Terjemahan JavaScript dari backend/segitiga/penilai.py.

import { PESAN, diagnosisAngka } from "./diagnosis.js";
import { parseAngka, parseSatuan, samakah } from "./parser_angka.js";

export const TINGKAT_PETUNJUK_MAKS = 3;
export const BATAS_PERCOBAAN = 3;

const benar = (lk) => ({ benar: true, kode: null, umpan_balik: lk.penjelasan_benar ?? "Tepat!" });
const salah = (kode, pesan = null) => ({
  benar: false,
  kode,
  umpan_balik: pesan || PESAN[kode] || PESAN.TIDAK_DIKENALI,
});

function periksaPilihan(lk, jawaban) {
  const kunciSet = new Set(Array.isArray(lk.kunci) ? lk.kunci : [lk.kunci]);
  const d = jawaban.pilihan;
  const dipilih = new Set(Array.isArray(d) ? d : d ? [d] : []);
  if (!dipilih.size) return salah("KOSONG", "Pilih jawabanmu dulu.");
  if (dipilih.size === kunciSet.size && [...dipilih].every((x) => kunciSet.has(x))) return benar(lk);

  const teksOpsi = Object.fromEntries(lk.opsi.map((o) => [o.id, o.teks]));
  const umpanOpsi = lk.umpan_balik_opsi || {};
  const keliru = [...dipilih].filter((x) => !kunciSet.has(x)).sort();
  if (keliru.length) {
    const p = keliru[0];
    const pesan = umpanOpsi[p] || `Pilihan “${teksOpsi[p] ?? p}” belum tepat. Baca lagi pertanyaannya.`;
    return salah("PILIHAN_SALAH", pesan);
  }
  const kurang = kunciSet.size - dipilih.size;
  return salah(
    "KURANG_LENGKAP",
    `Pilihanmu sudah benar, tetapi masih kurang ${kurang}. Pilih ${kunciSet.size} jawaban.`,
  );
}

function periksaAngkaLangkah(lk, jawaban) {
  const target = Number(lk.kunci.nilai);
  const nilai = parseAngka(jawaban.nilai);
  if (nilai === null) return salah("FORMAT_ANGKA");
  if (samakah(nilai, target)) {
    const satuanKunci = lk.kunci.satuan;
    if (satuanKunci && satuanKunci !== "Rp") {
      const satuan = parseSatuan(jawaban.satuan);
      if (!satuan) return salah("SATUAN_KOSONG");
      if (satuan !== satuanKunci) {
        let pesan = PESAN.SALAH_SATUAN;
        const dasar = satuanKunci.replace(/²+$/, "");
        if (satuanKunci.endsWith("²") && !satuan.endsWith("²")) {
          pesan = "Angkamu benar! Satuan luas memakai pangkat dua, misalnya cm² atau m².";
        } else if (dasar !== satuan.replace(/²+$/, "")) {
          pesan = `Angkamu benar! Perhatikan satuan pada soal: ukurannya dalam ${dasar}.`;
        }
        return salah("SALAH_SATUAN", pesan);
      }
    }
    return benar(lk);
  }
  const d = diagnosisAngka(nilai, target, lk.konteks_diagnosis, lk.pola_salah);
  return salah(d.kode, d.pesan);
}

function susunanKunci(isian, bebasTukar) {
  const hasil = [];
  for (let mask = 0; mask < 1 << bebasTukar.length; mask++) {
    const s = [...isian];
    bebasTukar.forEach(([i, j], k) => {
      if (mask & (1 << k)) [s[i], s[j]] = [s[j], s[i]];
    });
    hasil.push(s);
  }
  return hasil;
}

function periksaRumus(lk, jawaban) {
  const isianKunci = lk.kunci.isian.map((x) => parseAngka(x));
  const isian = jawaban.isian || [];
  if (isian.length !== isianKunci.length) return salah("KOSONG", "Isi semua kotak dulu.");
  const nilai = isian.map((x) => parseAngka(x));
  for (let i = 0; i < nilai.length; i++) {
    if (nilai[i] === null) return salah("FORMAT_ANGKA", `Kotak ke-${i + 1} belum berisi angka.`);
  }
  let terbaik = null;
  for (const s of susunanKunci(isianKunci, lk.kunci.bebas_tukar || [])) {
    const keliru = nilai.map((v, i) => (samakah(v, s[i]) ? -1 : i)).filter((i) => i >= 0);
    if (!keliru.length) return benar(lk);
    if (terbaik === null || keliru.length < terbaik.length) terbaik = keliru;
  }
  for (const pola of lk.pola_salah_isian || []) {
    const i = pola.isian_ke - 1;
    if (terbaik.includes(i) && samakah(nilai[i], parseAngka(pola.nilai) || 0)) return salah(pola.kode, pola.pesan);
  }
  const daftar = terbaik.map((i) => `ke-${i + 1}`).join(", ");
  return salah("RUMUS_SALAH", `Kotak ${daftar} belum tepat. Kotak lainnya sudah benar.`);
}

function periksaPilah(lk, jawaban) {
  const kunci = lk.kunci;
  const penempatan = jawaban.penempatan || {};
  const teksItem = Object.fromEntries(lk.item.map((it) => [it.id, it.teks]));
  const belum = Object.keys(kunci).filter((i) => !penempatan[i]);
  if (belum.length) return salah("KOSONG", `Masih ada ${belum.length} yang belum ditempatkan.`);
  const keliru = Object.keys(kunci).filter((i) => penempatan[i] !== kunci[i]);
  if (!keliru.length) return benar(lk);
  const nama = keliru.map((i) => `“${teksItem[i]}”`).join(", ");
  let pesan = `Cek lagi: ${nama} belum di tempat yang tepat.`;
  const khusus = (lk.umpan_balik_item || {})[keliru[0]];
  if (khusus) pesan += " " + khusus;
  return salah("PILAH_SALAH", pesan);
}

const PEMERIKSA = { pilihan: periksaPilihan, angka: periksaAngkaLangkah, rumus: periksaRumus, pilah: periksaPilah };

export function periksaLangkah(lk, jawaban) {
  const p = PEMERIKSA[lk.tipe];
  if (!p) throw new Error(`Tipe langkah tidak dikenal: ${lk.tipe}`);
  if (!jawaban || typeof jawaban !== "object" || Array.isArray(jawaban)) return salah("KOSONG", "Isi jawabanmu dulu.");
  return p(lk, jawaban);
}

export const langkahDapatSkor = (st) => st.benar && st.tingkat < TINGKAT_PETUNJUK_MAKS;

export function hitungBintang(skor, maks, totalPetunjuk) {
  if (skor >= maks && totalPetunjuk <= 1) return 3;
  if (skor >= 4) return 2;
  return 1;
}

export function hitungSkorMisi(misi, status) {
  const perTahap = new Map();
  let totalPetunjuk = 0;
  for (const lk of misi.langkah) {
    const st = status[lk.no] || { benar: false, tingkat: 0 };
    totalPetunjuk += st.tingkat;
    if (!perTahap.has(lk.tahap)) perTahap.set(lk.tahap, { skor: 0, maks: 0 });
    const t = perTahap.get(lk.tahap);
    t.maks += lk.skor;
    if (langkahDapatSkor(st)) t.skor += lk.skor;
  }
  const rincian = [...perTahap.entries()].sort((a, b) => a[0] - b[0]).map(([tahap, v]) => ({ tahap, ...v }));
  const skor = rincian.reduce((s, r) => s + r.skor, 0);
  const maks = rincian.reduce((s, r) => s + r.maks, 0);
  return { skor, maks, rincian, bintang: hitungBintang(skor, maks, totalPetunjuk), total_petunjuk: totalPetunjuk };
}

export function kategoriLiterasi(total) {
  if (total >= 20) return "Sangat baik";
  if (total >= 15) return "Baik";
  if (total >= 10) return "Cukup";
  return "Perlu bimbingan";
}
