// Komponen isian untuk satu langkah: pilihan, angka, rumus, pilah.
// Setiap komponen: { node, ambil(), kosong(), kunci() }.

import { el } from "./dom.js";
import { buatPilah } from "./pilah-info.js";

function buatPilihan(lk) {
  const banyak = Boolean(lk.pilih_banyak);
  const dipilih = new Set();
  let terkunci = false;

  const tombol = lk.opsi.map((o) => {
    const b = el(
      "button",
      {
        type: "button",
        class: "opsi",
        "aria-pressed": "false",
        onclick: () => {
          if (terkunci) return;
          if (banyak) {
            if (dipilih.has(o.id)) dipilih.delete(o.id);
            else dipilih.add(o.id);
          } else {
            dipilih.clear();
            dipilih.add(o.id);
          }
          for (const t of tombol) t.setAttribute("aria-pressed", String(dipilih.has(t.dataset.id)));
        },
      },
      o.teks,
    );
    b.dataset.id = o.id;
    return b;
  });

  return {
    node: el("div", { class: "opsi-grup", role: "group", "aria-label": "Pilihan jawaban" }, tombol),
    ambil: () => ({ pilihan: banyak ? [...dipilih] : ([...dipilih][0] ?? null) }),
    kosong: () => dipilih.size === 0,
    kunci() {
      terkunci = true;
      for (const t of tombol) t.disabled = true;
    },
  };
}

function buatAngka(lk, { kirim }) {
  const input = el("input", {
    type: "text",
    inputmode: "decimal",
    autocomplete: "off",
    id: `isian-${lk.no}`,
    placeholder: "contoh: 1.200 atau 1,8",
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") kirim();
  });

  let satuan = null;
  const tombolSatuan = (lk.pilihan_satuan || []).map((s) => {
    const b = el(
      "button",
      {
        type: "button",
        class: "opsi",
        "aria-pressed": "false",
        onclick: () => {
          satuan = s;
          for (const t of tombolSatuan) t.setAttribute("aria-pressed", String(t.textContent === s));
        },
      },
      s,
    );
    return b;
  });

  const node = el(
    "div",
    {},
    el("label", { for: `isian-${lk.no}` }, "Jawabanmu"),
    el("div", { class: "isian-angka" }, lk.awalan ? el("span", { class: "awalan" }, lk.awalan) : null, input),
    tombolSatuan.length
      ? el(
          "div",
          { class: "pilihan-satuan", role: "group", "aria-label": "Pilih satuan" },
          el("span", { class: "teks-redup" }, "Satuan:"),
          tombolSatuan,
        )
      : null,
  );

  return {
    node,
    ambil: () => ({ nilai: input.value, satuan }),
    kosong: () => input.value.trim() === "",
    kunci() {
      input.readOnly = true;
      for (const t of tombolSatuan) t.disabled = true;
    },
  };
}

function buatRumus(lk, { kirim }) {
  const bagian = lk.template.split("[]");
  const isian = [];
  const anak = [];
  bagian.forEach((teks, i) => {
    if (teks.trim()) anak.push(el("span", {}, teks.trim()));
    if (i < bagian.length - 1) {
      const input = el("input", {
        type: "text",
        inputmode: "text",
        autocomplete: "off",
        "aria-label": `Kotak ke-${i + 1}`,
      });
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") kirim();
      });
      isian.push(input);
      anak.push(input);
    }
  });
  return {
    node: el("div", { class: "rumus" }, anak),
    ambil: () => ({ isian: isian.map((i) => i.value) }),
    kosong: () => isian.some((i) => i.value.trim() === ""),
    kunci() {
      for (const i of isian) i.readOnly = true;
    },
  };
}

export function buatKomponen(lk, opsi = { kirim: () => {} }) {
  switch (lk.tipe) {
    case "pilihan":
      return buatPilihan(lk);
    case "angka":
      return buatAngka(lk, opsi);
    case "rumus":
      return buatRumus(lk, opsi);
    case "pilah":
      return buatPilah(lk);
    default:
      throw new Error(`Tipe langkah tidak dikenal: ${lk.tipe}`);
  }
}
