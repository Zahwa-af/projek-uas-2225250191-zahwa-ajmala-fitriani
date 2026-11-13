// Semua panggilan ke server ada di sini (CLAUDE.md).

async function minta(method, url, data) {
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: data ? { "Content-Type": "application/json" } : {},
      body: data ? JSON.stringify(data) : undefined,
    });
  } catch {
    throw new Error("Tidak tersambung ke server. Periksa Wi-Fi, lalu coba lagi.");
  }
  let isi = {};
  try {
    isi = await res.json();
  } catch {
    /* respons bukan JSON */
  }
  if (!res.ok) {
    const galat = new Error(isi.galat || "Terjadi gangguan. Coba lagi.");
    galat.status = res.status;
    throw galat;
  }
  return isi;
}

export const api = {
  buatSesi: (nama, kelas) =>
    minta("POST", "/api/sesi", { nama_panggilan: nama, kode_kelas: kelas }),
  cekSesi: (sesiId) => minta("GET", `/api/sesi/${encodeURIComponent(sesiId)}`),
  daftarMisi: (sesiId) => minta("GET", `/api/misi?sesi_id=${encodeURIComponent(sesiId)}`),
  ambilMisi: (id) => minta("GET", `/api/misi/${id}`),
  mulaiMisi: (id, sesiId) => minta("POST", `/api/misi/${id}/mulai`, { sesi_id: sesiId }),
  periksa: (mainId, langkah, jawaban) =>
    minta("POST", "/api/periksa", { main_id: mainId, langkah, jawaban }),
  petunjuk: (mainId, langkah) => minta("POST", "/api/petunjuk", { main_id: mainId, langkah }),
  selesai: (mainId) => minta("POST", "/api/misi/selesai", { main_id: mainId }),
  refleksi: (mainId, teks) => minta("POST", "/api/refleksi", { main_id: mainId, teks }),
  progres: (sesiId) => minta("GET", `/api/progres/${encodeURIComponent(sesiId)}`),
  latihanPilah: () => minta("GET", "/api/latihan/pilah"),
  periksaPilah: (soalId, penempatan) =>
    minta("POST", "/api/latihan/pilah/periksa", { soal_id: soalId, penempatan }),
  soalTinggi: () => minta("GET", "/api/latihan/tinggi"),
  periksaTinggi: (seed, pilihan) => minta("POST", "/api/latihan/tinggi/periksa", { seed, pilihan }),
  guru: (kodeKelas, pin) => minta("POST", "/api/guru", { kode_kelas: kodeKelas, pin }),
};
