// "Server" di dalam browser untuk versi online (tanpa Flask).
// Perilakunya meniru backend/api/*.py; progres disimpan di localStorage HP siswa.

import { buatSoalTinggi, periksaSoalTinggi, soalTinggiPublik } from "./generator_soal.js";
import {
  BATAS_PERCOBAAN,
  TINGKAT_PETUNJUK_MAKS,
  hitungSkorMisi,
  kategoriLiterasi,
  periksaLangkah,
} from "./penilai.js";

const KUNCI_SIMPAN = "segipintar.data.v1";
const FIELD_RAHASIA = new Set([
  "kunci", "petunjuk", "pola_salah", "pola_salah_isian", "konteks_diagnosis",
  "penjelasan_benar", "umpan_balik_opsi", "umpan_balik_item",
]);

class GalatApi extends Error {
  constructor(pesan, status = 400) {
    super(pesan);
    this.status = status;
  }
}

function muatData() {
  try {
    const t = localStorage.getItem(KUNCI_SIMPAN);
    if (t) return JSON.parse(t);
  } catch {
    /* mode privat: pakai memori saja */
  }
  return { sesi: {}, main: {}, refleksi: [] };
}

const data = muatData();

function simpan() {
  try {
    localStorage.setItem(KUNCI_SIMPAN, JSON.stringify(data));
  } catch {
    /* tetap jalan tanpa penyimpanan */
  }
}

function idAcak(n) {
  const b = new Uint8Array(n / 2);
  crypto.getRandomValues(b);
  return [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

const salin = (x) => JSON.parse(JSON.stringify(x));
const sekarang = () => new Date().toISOString();

let bank = null;
async function muatBank() {
  if (!bank) {
    const ambil = async (p) => {
      const r = await fetch(p);
      if (!r.ok) throw new GalatApi("Soal gagal dimuat. Periksa koneksi, lalu muat ulang halaman.", 500);
      return r.json();
    };
    const [misi, latihan] = await Promise.all([ambil("data/misi.json"), ambil("data/latihan.json")]);
    bank = { misi, latihan };
  }
  return bank;
}

const saringRahasia = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => !FIELD_RAHASIA.has(k)));

async function ambilMisiPenuh(id) {
  const m = (await muatBank()).misi.find((x) => x.id === Number(id));
  if (!m) throw new GalatApi("Misi tidak ditemukan.", 404);
  return m;
}

function ambilMain(mainId) {
  const main = data.main[mainId];
  if (!main) throw new GalatApi("Permainan misi tidak ditemukan. Mulai ulang misinya.", 404);
  return main;
}

const stLangkah = (main, no) => (main.langkah[no] ??= { benar: false, salah: 0, tingkat: 0 });

async function daftarMisiDenganStatus(sesiId) {
  const { misi } = await muatBank();
  const terbaik = {};
  for (const m of Object.values(data.main)) {
    if (m.sesi_id !== sesiId || !m.selesai) continue;
    const t = (terbaik[m.misi_id] ??= { skor: m.skor, bintang: m.bintang });
    t.skor = Math.max(t.skor, m.skor);
    t.bintang = Math.max(t.bintang, m.bintang);
  }
  let sebelumnyaSelesai = true;
  return misi.map((m) => {
    const st = terbaik[m.id];
    const hasil = {
      id: m.id,
      judul: m.judul,
      indikator: m.indikator,
      indikator_singkat: m.indikator_singkat,
      lencana: m.lencana,
      selesai: Boolean(st),
      skor: st ? st.skor : null,
      bintang: st ? st.bintang : 0,
      maks: 6,
      terbuka: sebelumnyaSelesai,
    };
    sebelumnyaSelesai = Boolean(st);
    return hasil;
  });
}

function bukaPetunjuk(main, lk, sampai) {
  const st = stLangkah(main, lk.no);
  const baru = [];
  for (let t = st.tingkat + 1; t <= sampai; t++) baru.push({ tingkat: t, teks: lk.petunjuk[t - 1] });
  st.tingkat = Math.max(st.tingkat, sampai);
  return baru;
}

async function jalankan(fn) {
  try {
    const hasil = await fn();
    simpan();
    return salin(hasil);
  } catch (e) {
    if (e instanceof GalatApi) throw e;
    throw new GalatApi(e.message || "Terjadi gangguan. Coba lagi.", 500);
  }
}

function teksWajib(nilai, label, maks) {
  const t = String(nilai ?? "").trim();
  if (!t) throw new GalatApi(`${label} belum diisi.`);
  if (t.length > maks) throw new GalatApi(`${label} terlalu panjang (maksimal ${maks} huruf).`);
  return t;
}

export const api = {
  buatSesi: (nama, kelas) =>
    jalankan(() => {
      const n = teksWajib(nama, "Nama panggilan", 30);
      const k = teksWajib(kelas, "Kode kelas", 20).toUpperCase();
      const id = idAcak(12);
      data.sesi[id] = { nama_panggilan: n, kode_kelas: k, dibuat: sekarang() };
      return { sesi_id: id, nama_panggilan: n, kode_kelas: k };
    }),

  cekSesi: (sesiId) =>
    jalankan(() => {
      const s = data.sesi[sesiId];
      if (!s) throw new GalatApi("Sesi tidak ditemukan.", 404);
      return { sesi_id: sesiId, nama_panggilan: s.nama_panggilan, kode_kelas: s.kode_kelas };
    }),

  daftarMisi: (sesiId) => jalankan(() => daftarMisiDenganStatus(sesiId)),

  ambilMisi: (id) =>
    jalankan(async () => {
      const m = await ambilMisiPenuh(id);
      return { ...Object.fromEntries(Object.entries(m).filter(([k]) => k !== "langkah")), langkah: m.langkah.map(saringRahasia) };
    }),

  mulaiMisi: (id, sesiId) =>
    jalankan(async () => {
      if (!data.sesi[sesiId]) throw new GalatApi("Sesi tidak ditemukan. Masukkan namamu lagi.", 404);
      const status = (await daftarMisiDenganStatus(sesiId)).find((m) => m.id === Number(id));
      if (!status) throw new GalatApi("Misi tidak ditemukan.", 404);
      if (!status.terbuka) throw new GalatApi("Selesaikan misi sebelumnya dulu.", 403);
      const mainId = idAcak(16);
      data.main[mainId] = { sesi_id: sesiId, misi_id: Number(id), mulai: sekarang(), selesai: null, langkah: {} };
      return { main_id: mainId };
    }),

  periksa: (mainId, no, jawaban) =>
    jalankan(async () => {
      const main = ambilMain(mainId);
      if (main.selesai) throw new GalatApi("Misi ini sudah selesai. Mulai lagi untuk mengulang.");
      const misi = await ambilMisiPenuh(main.misi_id);
      const lk = misi.langkah.find((x) => x.no === String(no));
      if (!lk) throw new GalatApi("Langkah tidak ditemukan.", 404);
      const st = stLangkah(main, lk.no);
      if (st.benar) {
        return { benar: true, kode_diagnosis: null, umpan_balik: lk.penjelasan_benar, boleh_lanjut: true, tingkat_petunjuk: st.tingkat, petunjuk_baru: [] };
      }
      const h = periksaLangkah(lk, jawaban && typeof jawaban === "object" ? jawaban : {});
      const dihitung = !["KOSONG", "FORMAT_ANGKA"].includes(h.kode);
      if (dihitung) {
        if (h.benar) st.benar = true;
        else st.salah += 1;
      }
      let umpan = h.umpan_balik;
      let baru = [];
      if (!h.benar && st.salah >= BATAS_PERCOBAAN) {
        baru = bukaPetunjuk(main, lk, TINGKAT_PETUNJUK_MAKS);
        if (baru.length) umpan += " Kamu sudah mencoba 3 kali. Yuk, lihat cara lengkapnya di petunjuk.";
      }
      return {
        benar: h.benar,
        kode_diagnosis: h.kode,
        umpan_balik: umpan,
        boleh_lanjut: h.benar || st.tingkat >= TINGKAT_PETUNJUK_MAKS,
        tingkat_petunjuk: st.tingkat,
        petunjuk_baru: baru,
      };
    }),

  petunjuk: (mainId, no) =>
    jalankan(async () => {
      const main = ambilMain(mainId);
      if (main.selesai) throw new GalatApi("Misi ini sudah selesai.");
      const misi = await ambilMisiPenuh(main.misi_id);
      const lk = misi.langkah.find((x) => x.no === String(no));
      if (!lk) throw new GalatApi("Langkah tidak ditemukan.", 404);
      const st = stLangkah(main, lk.no);
      if (st.benar) throw new GalatApi("Langkah ini sudah benar.");
      if (st.tingkat >= TINGKAT_PETUNJUK_MAKS) throw new GalatApi("Semua petunjuk sudah dibuka.");
      const baru = bukaPetunjuk(main, lk, st.tingkat + 1);
      return { petunjuk_baru: baru, tingkat_petunjuk: st.tingkat, boleh_lanjut: st.tingkat >= TINGKAT_PETUNJUK_MAKS };
    }),

  selesai: (mainId) =>
    jalankan(async () => {
      const main = ambilMain(mainId);
      const misi = await ambilMisiPenuh(main.misi_id);
      const belum = misi.langkah
        .filter((lk) => {
          const st = main.langkah[lk.no];
          return !(st && (st.benar || st.tingkat >= TINGKAT_PETUNJUK_MAKS));
        })
        .map((lk) => lk.no);
      if (belum.length) throw new GalatApi(`Masih ada langkah yang belum selesai: ${belum.join(", ")}.`);
      const skor = hitungSkorMisi(misi, main.langkah);
      if (!main.selesai) {
        Object.assign(main, { selesai: sekarang(), skor: skor.skor, rincian: skor.rincian, bintang: skor.bintang, total_petunjuk: skor.total_petunjuk });
      }
      return {
        ...skor,
        lencana: skor.skor >= 4 ? misi.lencana : null,
        ringkasan: misi.langkah.map((lk) => ({
          no: lk.no,
          judul: lk.judul || "",
          instruksi: lk.instruksi,
          penjelasan: lk.penjelasan_benar,
          dapat_skor: main.langkah[lk.no].benar && main.langkah[lk.no].tingkat < TINGKAT_PETUNJUK_MAKS,
        })),
      };
    }),

  refleksi: (mainId, teks) =>
    jalankan(() => {
      ambilMain(mainId);
      const t = String(teks ?? "").trim().slice(0, 1000);
      if (t) data.refleksi.push({ main_id: mainId, teks: t, waktu: sekarang() });
      return { tersimpan: Boolean(t) };
    }),

  progres: (sesiId) =>
    jalankan(async () => {
      const misi = await daftarMisiDenganStatus(sesiId);
      const total = misi.reduce((s, m) => s + (m.skor || 0), 0);
      return {
        misi,
        total,
        maks: 6 * misi.length,
        kategori: misi.some((m) => m.selesai) ? kategoriLiterasi(total) : null,
        lencana: misi.filter((m) => (m.skor || 0) >= 4).map((m) => m.lencana),
      };
    }),

  latihanPilah: () => jalankan(async () => (await muatBank()).latihan.pilah.map(saringRahasia)),

  periksaPilah: (soalId, penempatan) =>
    jalankan(async () => {
      const soal = (await muatBank()).latihan.pilah.find((s) => s.id === soalId);
      if (!soal) throw new GalatApi("Soal latihan tidak ditemukan.", 404);
      const h = periksaLangkah(soal, { penempatan: penempatan || {} });
      return { benar: h.benar, kode: h.kode, umpan_balik: h.umpan_balik };
    }),

  soalTinggi: () => jalankan(() => soalTinggiPublik(buatSoalTinggi(1 + Math.floor(Math.random() * 1_000_000)))),

  periksaTinggi: (seed, pilihan) => jalankan(() => periksaSoalTinggi(Number(seed), String(pilihan || ""))),

  guru: () =>
    jalankan(() => {
      throw new GalatApi(
        "Rekap guru hanya ada di versi server (python backend/app.py). Di versi online ini, data setiap siswa tersimpan di HP masing-masing.",
        403,
      );
    }),

  // Fitur Tahap 2 (RMT, Soal Cerita Bertahap, remedial) memakai logika Python dan belum
  // diterjemahkan ke versi statis. Halaman misi melewati aktivitas RMT bila gagal dimuat,
  // saran remedial disembunyikan, dan latihan bertahap memberi pesan yang jelas.
  rmtMisi: () => jalankan(() => {
    throw new GalatApi("Aktivitas RMT hanya ada di versi server.", 404);
  }),
  rmtRespons: () => jalankan(() => {
    throw new GalatApi("Aktivitas RMT hanya ada di versi server.", 404);
  }),
  rmtLewati: () => jalankan(() => ({ tercatat: false, dilewati: true })),
  remedial: () => jalankan(() => ({ saran: [], ada_data: false })),
  soalBertahap: () => jalankan(() => {
    throw new GalatApi(
      "Soal Cerita Bertahap hanya ada di versi server (python backend/app.py). Coba latihan lain dulu.",
      404,
    );
  }),
};
for (const nama of ["periksaBertahap", "petunjukBertahap", "selesaiBertahap"]) api[nama] = api.soalBertahap;
