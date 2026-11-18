// Rekap kelas untuk guru (F-16). Dilindungi PIN sederhana.

import { api } from "../api.js";
import { el, fmt, kotakUmpan } from "../dom.js";
import { LABEL_KESALAHAN } from "../teks.js";

export function halamanGuru(app) {
  const kelas = el("input", { id: "g-kelas", maxlength: "20", placeholder: "contoh: 8A" });
  const pin = el("input", { id: "g-pin", type: "password", inputmode: "numeric", autocomplete: "off" });
  const hasil = el("div", { "aria-live": "polite" });

  const form = el(
    "form",
    {
      class: "kartu",
      onsubmit: async (e) => {
        e.preventDefault();
        hasil.replaceChildren();
        try {
          tampilkan(hasil, await api.guru(kelas.value, pin.value));
        } catch (err) {
          hasil.append(kotakUmpan("salah", err.message));
        }
      },
    },
    el("label", { for: "g-kelas" }, "Kode kelas"),
    kelas,
    el("label", { for: "g-pin" }, "PIN guru"),
    pin,
    el("p", {}),
    el("button", { type: "submit", class: "tombol tombol-utama" }, "Lihat rekap"),
  );

  app.append(el("h1", { tabindex: "-1" }, "Rekap kelas"), form, hasil, el("p", {}, el("a", { href: "#/" }, "← Beranda")));
}

function tampilkan(wadah, data) {
  if (!data.siswa.length) {
    wadah.append(kotakUmpan("info", `Belum ada siswa kelas ${data.kode_kelas} yang menyelesaikan misi.`));
    return;
  }
  wadah.append(
    el("h2", {}, `Kelas ${data.kode_kelas} · ${data.siswa.length} siswa`),
    el(
      "div",
      { class: "gulir-x" },
      el(
        "table",
        { class: "tabel" },
        el(
          "thead",
          {},
          el(
            "tr",
            {},
            el("th", {}, "Nama"),
            data.judul_misi.map((_, i) => el("th", {}, `M${i + 1}`)),
            el("th", {}, "Total"),
            el("th", {}, "Kategori"),
            el("th", {}, "Petunjuk"),
            el("th", {}, "Kesalahan terbanyak"),
            el("th", { title: "Jumlah jawaban salah per fase kognitif RMT: Input / Elaborasi / Output" }, "Fase sulit (I/E/O)"),
          ),
        ),
        el(
          "tbody",
          {},
          data.siswa.map((s) =>
            el(
              "tr",
              {},
              el(
                "td",
                {},
                s.nama_panggilan,
                s.refleksi.length
                  ? el("details", {}, el("summary", {}, "Penjelasan"), s.refleksi.map((r) => el("p", { class: "teks-redup" }, r)))
                  : null,
              ),
              s.skor_misi.map((x) => el("td", {}, x === null ? "–" : fmt(x))),
              el("td", {}, `${fmt(s.total)}/24`),
              el("td", {}, s.kategori),
              el("td", {}, String(s.petunjuk_dibuka)),
              el("td", {}, s.kesalahan_terbanyak.map((k) => LABEL_KESALAHAN[k] ?? k).join(", ") || "–"),
              el("td", {}, teksFase(s.fase_kesulitan)),
            ),
          ),
        ),
      ),
    ),
    el("p", { class: "teks-redup" }, `Misi: ${data.judul_misi.map((j, i) => `M${i + 1} ${j}`).join(" · ")}`),
    el(
      "p",
      { class: "teks-redup" },
      "Fase sulit (RMT): jumlah jawaban salah pada fase Input (mengumpulkan informasi) / " +
        "Elaborasi (mengolah, memilih rumus) / Output (menyatakan hasil, satuan, ketelitian). " +
        "Pemetaan masih usulan peneliti.",
    ),
  );
}

// Data lama (sebelum fitur ini) tidak punya fase_kesulitan: tampilkan tanda strip.
function teksFase(fase) {
  if (!fase) return "–";
  return `${fase.input ?? 0} / ${fase.elaborasi ?? 0} / ${fase.output ?? 0}`;
}
