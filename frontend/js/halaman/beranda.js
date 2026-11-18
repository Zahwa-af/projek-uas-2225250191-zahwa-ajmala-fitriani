import { api } from "../api.js";
import { el, kotakUmpan } from "../dom.js";
import { ambilSesi, hapusSesi, simpanSesi } from "../state.js";

const MENU = [
  ["#/belajar", "Belajar", "Kenali jenis, alas, tinggi, keliling, dan luas segitiga."],
  ["#/latihan", "Latihan", "Tunjuk tinggi segitiga dan pilah informasi soal cerita."],
  ["#/misi", "Misi Segitiga", "4 misi literasi matematika di sekolah."],
  ["#/asisten", "Pembimbing AI", "Tanya rumus, konsep, atau minta soal dihitung langsung."],
  ["#/hasil", "Hasilku", "Lihat skor, bintang, dan lencanamu."],
];

export function halamanBeranda(app, segarkan) {
  const sesi = ambilSesi();
  if (!sesi) {
    formulirMasuk(app, segarkan);
    return;
  }
  app.append(
    el("h1", { tabindex: "-1" }, `Halo, ${sesi.nama_panggilan}!`),
    el("p", {}, "Saran urutan: Belajar → Latihan → Misi. Kamu boleh mengulang kapan saja."),
    el(
      "ol",
      { class: "menu" },
      MENU.map(([href, judul, teks], i) =>
        el(
          "li",
          {},
          el(
            "a",
            { class: "kartu-menu", href },
            el("span", { class: "nomor", "aria-hidden": "true" }, String(i + 1)),
            el("span", {}, el("strong", {}, judul), el("span", { class: "teks-redup" }, teks)),
          ),
        ),
      ),
    ),
    el(
      "p",
      { class: "teks-redup" },
      `Kelas ${sesi.kode_kelas}. Bukan kamu? `,
      el(
        "a",
        {
          href: "#/",
          onclick: (e) => {
            e.preventDefault();
            hapusSesi();
            segarkan();
          },
        },
        "Ganti nama",
      ),
      " · ",
      el("a", { href: "#/guru" }, "Halaman guru"),
    ),
  );
}

function formulirMasuk(app, segarkan) {
  const nama = el("input", { id: "nama", maxlength: "30", autocomplete: "nickname", required: true });
  const kelas = el("input", { id: "kelas", maxlength: "20", autocomplete: "off", placeholder: "contoh: 8A", required: true });
  const pesan = el("div", { "aria-live": "polite" });
  const kirim = el("button", { type: "submit", class: "tombol tombol-utama" }, "Mulai belajar");

  const form = el(
    "form",
    {
      class: "kartu",
      onsubmit: async (e) => {
        e.preventDefault();
        pesan.replaceChildren();
        if (!nama.value.trim() || !kelas.value.trim()) {
          pesan.append(kotakUmpan("info", "Isi nama panggilan dan kode kelas dulu."));
          return;
        }
        kirim.disabled = true;
        try {
          simpanSesi(await api.buatSesi(nama.value, kelas.value));
          segarkan();
        } catch (err) {
          pesan.append(kotakUmpan("salah", err.message));
          kirim.disabled = false;
        }
      },
    },
    el("label", { for: "nama" }, "Nama panggilan"),
    nama,
    el("label", { for: "kelas" }, "Kode kelas"),
    kelas,
    pesan,
    el("p", {}),
    kirim,
  );

  app.append(
    el("h1", { tabindex: "-1" }, "Selamat datang di SegiPintar"),
    el("p", {}, "Belajar segitiga langkah demi langkah, dengan tempo milikmu sendiri."),
    form,
    el("p", { class: "teks-redup" }, "Kami hanya menyimpan nama panggilan dan kode kelas. ", el("a", { href: "#/guru" }, "Halaman guru")),
  );
  nama.focus();
}
