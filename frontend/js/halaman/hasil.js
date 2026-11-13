import { api } from "../api.js";
import { barBawah, bintangTeks, el, fmt } from "../dom.js";
import { ambilSesi } from "../state.js";
import { LENCANA_IKON } from "../teks.js";

export async function halamanHasil(app) {
  const sesi = ambilSesi();
  const p = await api.progres(sesi.sesi_id);
  const adaSelesai = p.misi.some((m) => m.selesai);

  app.append(
    el("h1", { tabindex: "-1" }, "Hasilku"),
    adaSelesai
      ? el(
          "div",
          { class: "kartu" },
          el("p", { class: "teks-redup" }, "Total skor literasi matematika"),
          el("p", { class: "skor-besar" }, `${fmt(p.total)} dari ${p.maks}`),
          el("p", {}, "Kategori: ", el("strong", {}, p.kategori)),
        )
      : el("p", {}, "Belum ada misi yang selesai. Yuk mulai dari Misi 1!"),
    el("h2", {}, "Per misi"),
    el(
      "div",
      { class: "gulir-x" },
      el(
        "table",
        { class: "tabel" },
        el("thead", {}, el("tr", {}, el("th", {}, "Misi"), el("th", {}, "Skor terbaik"), el("th", {}, "Bintang"))),
        el(
          "tbody",
          {},
          p.misi.map((m) =>
            el(
              "tr",
              {},
              el("td", {}, `${m.id}. ${m.judul}`, el("br"), el("span", { class: "teks-redup" }, m.indikator_singkat)),
              el("td", {}, m.selesai ? `${fmt(m.skor)} dari 6` : "–"),
              el("td", {}, m.selesai ? bintangTeks(m.bintang) : "–"),
            ),
          ),
        ),
      ),
    ),
    el("h2", {}, "Lencana"),
    p.lencana.length
      ? el(
          "ul",
          { class: "lencana-daftar" },
          p.lencana.map((l) => el("li", { class: "lencana" }, `${LENCANA_IKON[l] ?? ""} ${l}`)),
        )
      : el("p", { class: "teks-redup" }, "Raih skor 4 atau lebih pada sebuah misi untuk mendapat lencana."),
    barBawah(el("a", { class: "tombol", href: "#/" }, "Beranda"), el("a", { class: "tombol tombol-utama", href: "#/misi" }, "Ke misi")),
  );
}
