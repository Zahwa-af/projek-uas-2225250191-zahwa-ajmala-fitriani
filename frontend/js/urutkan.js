// Komponen "urutkan kartu" (Planning RMT). Tombol ↑/↓ dipakai, bukan seret:
// andal di layar sentuh, bisa dipakai dengan keyboard, dan tidak butuh gerakan presisi.
// Antarmuka sama dengan komponen di langkah.js: { node, ambil(), kosong(), kunci() }.

import { el } from "./dom.js";

export function buatUrutan(kartu) {
  const teks = Object.fromEntries(kartu.map((k) => [k.id, k.teks]));
  const urutan = kartu.map((k) => k.id); // urutan awal dari server (bukan urutan jawaban)
  let terkunci = false;
  const daftar = el("ol", { class: "urutan", "aria-label": "Urutan langkah" });

  function gambarUlang(fokus = null) {
    daftar.replaceChildren(
      ...urutan.map((id, i) =>
        el(
          "li",
          { class: "urutan-kartu" },
          el("span", { class: "urutan-no", "aria-hidden": "true" }, String(i + 1)),
          el("span", { class: "urutan-teks" }, teks[id]),
          el(
            "span",
            { class: "urutan-tombol" },
            el(
              "button",
              {
                type: "button",
                class: "opsi urutan-geser",
                "data-arah": "naik",
                "aria-label": `Naikkan: ${teks[id]}`,
                disabled: terkunci || i === 0,
                onclick: () => geser(i, -1),
              },
              "↑",
            ),
            el(
              "button",
              {
                type: "button",
                class: "opsi urutan-geser",
                "data-arah": "turun",
                "aria-label": `Turunkan: ${teks[id]}`,
                disabled: terkunci || i === urutan.length - 1,
                onclick: () => geser(i, 1),
              },
              "↓",
            ),
          ),
        ),
      ),
    );
    if (fokus) {
      // Fokus tetap pada kartu yang baru dipindah (penting untuk pengguna keyboard).
      const li = daftar.children[fokus.posisi];
      const tombolSama = li?.querySelector(`[data-arah="${fokus.arah}"]:not([disabled])`);
      (tombolSama ?? li?.querySelector("button:not([disabled])"))?.focus();
    }
  }

  function geser(i, arah) {
    const j = i + arah;
    if (terkunci || j < 0 || j >= urutan.length) return;
    [urutan[i], urutan[j]] = [urutan[j], urutan[i]];
    gambarUlang({ posisi: j, arah: arah < 0 ? "naik" : "turun" });
  }

  gambarUlang();
  return {
    node: daftar,
    ambil: () => ({ urutan: [...urutan] }),
    kosong: () => false,
    kunci() {
      terkunci = true;
      gambarUlang();
    },
  };
}
