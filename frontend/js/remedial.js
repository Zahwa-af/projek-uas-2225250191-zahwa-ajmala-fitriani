// Kartu saran remedial (penguatan). Isi saran & tautan dihitung server dari kesalahan siswa
// sendiri (backend/segitiga/remedial.py). Hanya saran: skor dan jawaban tidak berubah.

import { el } from "./dom.js";
import { INGAT_LAGI } from "./teks.js";

export function elRemedial(saran, { judul = "Perkuat pemahamanmu" } = {}) {
  if (!saran?.length) return null;
  return el(
    "section",
    { class: "kartu kartu-remedial" },
    el("h2", {}, judul),
    el("p", { class: "teks-redup" }, "Saran ini dari jawabanmu yang belum tepat. Skormu tidak berubah."),
    saran.map((s) =>
      el(
        "div",
        { class: "remedial-item" },
        el("h3", {}, s.judul),
        el("p", {}, s.pesan),
        s.area === "operasi_hitung"
          ? el(
              "details",
              { class: "ingat-lagi" },
              el("summary", {}, "Ingat lagi: cara menghitung"),
              el("ul", {}, INGAT_LAGI.map((t) => el("li", {}, t))),
            )
          : null,
        el(
          "p",
          { class: "remedial-tautan" },
          s.tautan.map((t) => el("a", { class: "tombol", href: t.href }, t.label)),
        ),
      ),
    ),
  );
}
