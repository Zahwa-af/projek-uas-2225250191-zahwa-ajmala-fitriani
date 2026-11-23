// Tampilan satu aktivitas pendamping RMT (tanpa skor).
// SEMUA isi aktivitas (pertanyaan, opsi, kartu, tujuan, makna) berasal dari backend
// (GET /api/rmt/misi/<id> ← backend/data/soal/rmt_misi.json). Di sini hanya label layar.
// Kunci jawaban tidak pernah dikirim ke browser; penjelasan datang setelah siswa menjawab.

import { el, kotakUmpan, tombol } from "./dom.js";
import { buatKomponen } from "./langkah.js";
import { buatUrutan } from "./urutkan.js";

// Label layar per tahap RMT (bukan konten soal).
export const LABEL_TAHAP = {
  input: "Tebak dulu",
  perencanaan: "Susun rencanamu",
  representasi: "Tata informasinya",
  validasi: "Cek hasilmu",
  refleksi: "Jelaskan ke temanmu",
  transendensi: "Di mana lagi?",
};

/** Status awal sebuah aktivitas di halaman misi. */
export function buatStatusAktivitas(a) {
  let komponen = null;
  if (a.jenis === "urutan") {
    komponen = buatUrutan(a.kartu);
  } else if (a.jenis === "pilihan" || a.jenis === "pilihan_banyak" || a.jenis === "prediksi") {
    komponen = buatKomponen({
      no: `rmt-${a.id}`,
      tipe: "pilihan",
      opsi: a.opsi,
      pilih_banyak: a.jenis === "pilihan_banyak",
    });
  }
  return {
    aktivitas: a,
    komponen,
    selesai: false, // sudah dijawab (benar / tercatat) atau dilewati
    umpan: null,
    jenisUmpan: null,
    sibuk: false,
  };
}

/**
 * Kirim jawaban. `api` disuntikkan agar modul ini mudah diuji.
 * Mengembalikan status yang diperbarui (objek yang sama).
 */
export async function periksaAktivitas(api, mainId, s) {
  const a = s.aktivitas;
  if (s.sibuk || s.selesai) return s;
  if (s.komponen.kosong()) {
    s.umpan = a.jenis === "pilihan_banyak" ? "Pilih jawabanmu dulu (boleh lebih dari satu)." : "Pilih jawabanmu dulu.";
    s.jenisUmpan = "info";
    return s;
  }
  s.sibuk = true;
  try {
    const r = await api.rmtRespons(mainId, a.id, s.komponen.ambil());
    if (r.benar === false) {
      s.umpan = r.umpan_balik;
      s.jenisUmpan = "salah";
    } else {
      // benar (aktivitas berkunci) atau tercatat (prediksi tanpa jawaban benar)
      s.umpan = r.penjelasan || r.umpan_balik;
      s.jenisUmpan = r.benar ? "benar" : "info";
      s.selesai = true;
      s.komponen.kunci();
    }
  } catch (e) {
    s.umpan = `${e.message} Kamu tetap bisa melanjutkan misi.`;
    s.jenisUmpan = "info";
  } finally {
    s.sibuk = false;
  }
  return s;
}

/** Lewati aktivitas. Gagal tersimpan pun tidak menghalangi misi. */
export async function lewatiAktivitas(api, mainId, s) {
  if (!s.selesai) {
    try {
      await api.rmtLewati(mainId, s.aktivitas.id);
    } catch {
      /* aktivitas pendamping: jangan menghalangi misi */
    }
  }
  s.selesai = true;
  return s;
}

/**
 * Elemen layar aktivitas (tanpa bar tombol bawah; bar disusun oleh halaman misi).
 * `pembuka` opsional: konten tambahan di atas pertanyaan (mis. tujuan & makna misi).
 */
export function elAktivitas(s, { posisi, pembuka = null }) {
  const a = s.aktivitas;
  return [
    el("p", { class: "posisi" }, posisi),
    pembuka,
    el(
      "h1",
      { class: "judul-langkah", tabindex: "-1" },
      el("span", { class: "label-tahap" }, LABEL_TAHAP[a.tahap] ?? a.tahap),
      a.pertanyaan ?? a.instruksi,
    ),
    s.komponen?.node ?? null,
    s.umpan ? kotakUmpan(s.jenisUmpan, s.umpan) : null,
    el("p", { class: "teks-redup" }, "Aktivitas ini tidak memengaruhi skor misi."),
  ].filter((x) => x != null); // append() asli mengubah null menjadi teks "null"
}

/** Kartu tujuan & makna misi (Intensionalitas & Makna MLE). */
export function elTujuanMakna(konten) {
  return el(
    "section",
    { class: "kartu kartu-tujuan" },
    el("p", {}, el("strong", {}, "Tujuan misi ini: "), konten.tujuan),
    el("p", {}, el("strong", {}, "Mengapa penting: "), konten.makna),
  );
}

/** Tombol untuk bar bawah layar aktivitas. */
export function tombolAktivitas(s, { periksa, lewati, lanjut }) {
  if (s.selesai) return [tombol("Lanjut", lanjut, true)];
  const labelKirim = s.aktivitas.jenis === "prediksi" ? "Simpan tebakan" : "Periksa";
  return [
    tombol("Lewati", lewati, false, { disabled: s.sibuk }),
    tombol(labelKirim, periksa, true, { disabled: s.sibuk }),
  ];
}
