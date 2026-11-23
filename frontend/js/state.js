// Menyimpan sesi siswa. localStorage bisa gagal (mode privat), jadi selalu pakai try/catch.

const KUNCI = "segipintar.sesi";
let cadangan = null;

export function ambilSesi() {
  try {
    const teks = localStorage.getItem(KUNCI);
    if (teks) return JSON.parse(teks);
  } catch {
    /* abaikan */
  }
  return cadangan;
}

export function simpanSesi(sesi) {
  cadangan = sesi;
  try {
    localStorage.setItem(KUNCI, JSON.stringify(sesi));
  } catch {
    /* tetap jalan dengan cadangan di memori */
  }
}

export function hapusSesi() {
  cadangan = null;
  tingkatCadangan = null;
  try {
    localStorage.removeItem(KUNCI);
    localStorage.removeItem(KUNCI_TINGKAT); // jangan tinggalkan jejak siswa sebelumnya
  } catch {
    /* abaikan */
  }
}

// Tingkat bantuan Soal Cerita Bertahap (fading). Hanya kenyamanan: bila hilang, mulai dari 1.
// Hanya SATU siswa yang disimpan ({sesi_id, tingkat}), agar di HP yang dipakai bergantian
// tidak tertinggal daftar sesi_id siswa lain. Milik siswa lain diabaikan (mulai dari 1).
const KUNCI_TINGKAT = "segipintar.tingkatBertahap";
let tingkatCadangan = null;

export function ambilTingkatBertahap(sesiId) {
  let data = tingkatCadangan;
  try {
    data = JSON.parse(localStorage.getItem(KUNCI_TINGKAT) || "null") ?? data;
  } catch {
    /* abaikan */
  }
  return data && data.sesi_id === sesiId && Number.isInteger(data.tingkat) ? data.tingkat : 1;
}

export function simpanTingkatBertahap(sesiId, tingkat) {
  tingkatCadangan = { sesi_id: sesiId, tingkat };
  try {
    localStorage.setItem(KUNCI_TINGKAT, JSON.stringify(tingkatCadangan));
  } catch {
    /* tetap jalan dengan cadangan di memori */
  }
}
