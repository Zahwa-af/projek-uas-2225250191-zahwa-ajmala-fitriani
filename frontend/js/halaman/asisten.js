
import { api } from "../api.js";
import { ambilSesi } from "../state.js";
import { el, kotakUmpan } from "../dom.js";
import { elPesanChat } from "../format-pesan.js";

export function halamanAsisten(app) {
  const sesi = ambilSesi();
  const riwayat = el("div", { class: "chat-riwayat", "aria-live": "polite" });

  // Tampilkan pesan terbaru tanpa melompat jauh (nyaman di HP).
  const tampilkan = (node) => {
    riwayat.append(node);
    node.scrollIntoView({ block: "nearest" });
  };

  const area = el("textarea", {
    rows: "3",
    maxlength: "500",
    placeholder: "Contoh: Hitung luas segitiga dengan alas 10 cm dan tinggi 6 cm."
  });

  const tombolKirim = el(
    "button",
    { type: "button", class: "tombol tombol-utama" },
    "Kirim pertanyaan"
  );

  riwayat.append(
    el(
      "p",
      { class: "teks-redup" },
      "Halo! Aku Pembimbing AI SegiPintar. Tanyakan rumus, konsep, atau minta aku menghitung soal. Aku akan menjawab langsung."
    )
  );

  async function kirim() {
    const teks = area.value.trim();

    if (!teks) {
      riwayat.append(
        kotakUmpan("info", "Tulis pertanyaanmu terlebih dahulu.")
      );
      return;
    }

    if (!sesi || !sesi.sesi_id) {
      riwayat.append(
        kotakUmpan("salah", "Sesi belajar tidak ditemukan. Silakan masuk kembali.")
      );
      return;
    }

    tombolKirim.disabled = true;

    tampilkan(elPesanChat("siswa", teks));

    area.value = "";

    const indikator = el(
      "p",
      { class: "teks-redup chat-memuat" },
      "Pembimbing AI sedang menyiapkan jawaban..."
    );

    tampilkan(indikator);

    try {
      const status = await api.statusAsisten();

      if (!status.aktif) {
        throw new Error("Pembimbing AI sedang tidak aktif.");
      }

      const hasil = await api.pesanAsistenBeranda(
        sesi.sesi_id,
        teks
      );

      indikator.remove();

      tampilkan(elPesanChat("asisten", hasil.balasan));
    } catch (e) {
      indikator.remove();
      tampilkan(kotakUmpan("salah", e.message));
    } finally {
      tombolKirim.disabled = false;
      area.focus();
    }
  }

  tombolKirim.addEventListener("click", kirim);

  area.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      kirim();
    }
  });

  app.append(
    el("h1", { tabindex: "-1" }, "Pembimbing AI SegiPintar"),
    el(
      "p",
      {},
      "Tanyakan materi matematika, terutama segitiga, atau pertanyaan pelajaran lainnya."
    ),
    el("section", { class: "kartu" }, riwayat, area, tombolKirim),
    el("p", {}, el("a", { href: "#/" }, "← Kembali ke beranda"))
  );
}
