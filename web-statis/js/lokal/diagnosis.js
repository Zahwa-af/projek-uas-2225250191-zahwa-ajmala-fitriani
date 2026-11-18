// Terjemahan JavaScript dari backend/segitiga/diagnosis.py.

import { samakah } from "./parser_angka.js";

export const PESAN = {
  LUPA_SETENGAH: "Hasilmu 2 kali lebih besar. Sudahkah kamu mengalikan dengan ½?",
  PAKAI_KELILING: "Itu cara menghitung keliling. Yang ditanya adalah luas.",
  JUMLAH_BUKAN_KALI: "Pada rumus luas, alas dan tinggi dikalikan, bukan dijumlahkan.",
  SALAH_TINGGI: "Tinggi harus tegak lurus dengan alas. Lihat garis oranye putus-putus.",
  LUPA_JUMLAH_BENDA: "Itu baru untuk satu benda. Ada berapa banyak bendanya?",
  TERTUKAR_BAGIAN: "Itu luas bagian yang lain. Baca lagi bagian mana yang ditanya.",
  SALAH_SATUAN: "Angkamu benar! Coba periksa satuannya lagi.",
  SATUAN_KOSONG: "Angkamu benar! Sekarang pilih juga satuannya.",
  SALAH_HITUNG: "Caramu sudah mendekati. Coba hitung ulang perkaliannya dengan teliti.",
  SALAH_DESIMAL:
    "Angkamu 10 kali terlalu besar atau terlalu kecil. Periksa letak koma atau banyaknya angka nol.",
  FORMAT_ANGKA: "Tulis jawabanmu sebagai angka, misalnya 1.200 atau 1,8.",
  TIDAK_DIKENALI: "Jawabanmu belum tepat. Coba baca lagi langkahnya, atau buka petunjuk.",
};

export const buat = (kode, pesan = null) => ({ kode, pesan: pesan || PESAN[kode] });

export function diagnosisAngka(nilai, kunci, konteks = {}, polaSalah = []) {
  konteks = konteks || {};
  for (const pola of polaSalah || []) {
    if (samakah(nilai, Number(pola.nilai))) return buat(pola.kode, pola.pesan);
  }
  const { alas, tinggi, sisi, sisi_miring: sisiMiring } = konteks;
  if (alas && tinggi) {
    if (samakah(nilai, alas * tinggi)) return buat("LUPA_SETENGAH");
    if (samakah(nilai, alas + tinggi) || samakah(nilai, (alas + tinggi) / 2)) return buat("JUMLAH_BUKAN_KALI");
  }
  if (sisi && sisi.length && samakah(nilai, sisi.reduce((a, b) => a + b, 0))) return buat("PAKAI_KELILING");
  if (alas && sisiMiring && samakah(nilai, 0.5 * alas * sisiMiring)) return buat("SALAH_TINGGI");
  if (kunci) {
    for (const f of [10, 100, 0.1, 0.01]) if (samakah(nilai, kunci * f)) return buat("SALAH_DESIMAL");
    if (Math.abs(nilai - kunci) / Math.abs(kunci) <= 0.2) return buat("SALAH_HITUNG");
  }
  return buat("TIDAK_DIKENALI");
}
