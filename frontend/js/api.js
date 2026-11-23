
// Semua panggilan ke server ada di sini.

async function minta(method, url, data) {
  let res;

  try {
    res = await fetch(url, {
      method,
      headers: data ? { "Content-Type": "application/json" } : {},
      body: data ? JSON.stringify(data) : undefined,
    });
  } catch {
    throw new Error(
      "Tidak tersambung ke server. Periksa Wi-Fi, lalu coba lagi."
    );
  }

  let isi = {};

  try {
    isi = await res.json();
  } catch {
    // Respons bukan JSON.
  }

  if (!res.ok) {
    const galat = new Error(
      isi.galat || "Terjadi gangguan. Coba lagi."
    );
    galat.status = res.status;
    throw galat;
  }

  return isi;
}

export const api = {
  buatSesi: (nama, kelas) =>
    minta("POST", "/api/sesi", {
      nama_panggilan: nama,
      kode_kelas: kelas,
    }),

  cekSesi: (sesiId) =>
    minta("GET", `/api/sesi/${encodeURIComponent(sesiId)}`),

  daftarMisi: (sesiId) =>
    minta("GET", `/api/misi?sesi_id=${encodeURIComponent(sesiId)}`),

  ambilMisi: (id) =>
    minta("GET", `/api/misi/${id}`),

  mulaiMisi: (id, sesiId) =>
    minta("POST", `/api/misi/${id}/mulai`, {
      sesi_id: sesiId,
    }),

  periksa: (mainId, langkah, jawaban) =>
    minta("POST", "/api/periksa", {
      main_id: mainId,
      langkah,
      jawaban,
    }),

  petunjuk: (mainId, langkah) =>
    minta("POST", "/api/petunjuk", {
      main_id: mainId,
      langkah,
    }),

  selesai: (mainId) =>
    minta("POST", "/api/misi/selesai", {
      main_id: mainId,
    }),

  refleksi: (mainId, teks) =>
    minta("POST", "/api/refleksi", {
      main_id: mainId,
      teks,
    }),

  progres: (sesiId) =>
    minta("GET", `/api/progres/${encodeURIComponent(sesiId)}`),

  latihanPilah: () =>
    minta("GET", "/api/latihan/pilah"),

  periksaPilah: (soalId, penempatan) =>
    minta("POST", "/api/latihan/pilah/periksa", {
      soal_id: soalId,
      penempatan,
    }),

  soalTinggi: () =>
    minta("GET", "/api/latihan/tinggi"),

  periksaTinggi: (seed, pilihan) =>
    minta("POST", "/api/latihan/tinggi/periksa", {
      seed,
      pilihan,
    }),

  // Soal Cerita Bertahap (fading, tanpa skor). Kunci tetap di server.
  soalBertahap: (tingkat) =>
    minta("GET", `/api/latihan/bertahap?tingkat=${encodeURIComponent(tingkat)}`),

  periksaBertahap: (seed, tingkat, isian, jawaban) =>
    minta("POST", "/api/latihan/bertahap/periksa", { seed, tingkat, isian, jawaban }),

  petunjukBertahap: (seed, tingkat, isian, ke) =>
    minta("POST", "/api/latihan/bertahap/petunjuk", { seed, tingkat, isian, ke }),

  selesaiBertahap: (seed, tingkat, salah, petunjuk) =>
    minta("POST", "/api/latihan/bertahap/selesai", { seed, tingkat, salah, petunjuk }),

  // Saran remedial dari kesalahan siswa sendiri (hanya membaca, skor tidak berubah).
  remedial: (sesiId, mainId = null) =>
    minta(
      "GET",
      `/api/remedial/${encodeURIComponent(sesiId)}` +
        (mainId ? `?main_id=${encodeURIComponent(mainId)}` : ""),
    ),

  statusAsisten: () =>
    minta("GET", "/api/asisten/status"),

  // Chat Pembimbing AI di dalam misi.
  pesanAsisten: (mainId, langkah, teks) =>
    minta("POST", "/api/asisten/pesan", {
      main_id: mainId,
      langkah,
      teks,
    }),

  // Chat Pembimbing AI di beranda.
  pesanAsistenBeranda: (sesiId, teks) =>
    minta("POST", "/api/asisten/beranda", {
      sesi_id: sesiId,
      teks,
    }),

  // Aktivitas pendamping RMT (tanpa skor). Konten dari backend/data/soal/rmt_misi.json.
  rmtMisi: (misiId) =>
    minta("GET", `/api/rmt/misi/${misiId}`),

  rmtRespons: (mainId, aktivitas, jawaban) =>
    minta("POST", "/api/rmt/respons", {
      main_id: mainId,
      aktivitas,
      jawaban,
    }),

  rmtLewati: (mainId, aktivitas) =>
    minta("POST", "/api/rmt/respons", {
      main_id: mainId,
      aktivitas,
      dilewati: true,
    }),

  guru: (kodeKelas, pin) =>
    minta("POST", "/api/guru", {
      kode_kelas: kodeKelas,
      pin,
    }),
};
