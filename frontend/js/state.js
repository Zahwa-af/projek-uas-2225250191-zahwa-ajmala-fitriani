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
  try {
    localStorage.removeItem(KUNCI);
  } catch {
    /* abaikan */
  }
}
