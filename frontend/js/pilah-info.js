// Komponen "Pilah Informasi" (F-05): seret atau ketuk angka ke kotak yang tepat.
// Dua cara: (1) ketuk chip lalu ketuk kotak — andal di layar sentuh; (2) seret chip ke kotak.

import { el } from "./dom.js";

export function buatPilah({ item, kotak }) {
  const penempatan = {};
  const chip = {};
  let terpilih = null;
  let terkunci = false;

  const node = el("div", { class: "pilah" });

  function buatZona(id, label) {
    const isi = el("div", { class: "zona-isi" });
    const judul = el("button", { type: "button", class: "zona-label" }, label);
    const zona = el(
      "div",
      { class: id ? "zona" : "zona zona-bank", role: "group", "aria-label": label },
      judul,
      isi,
    );
    zona.dataset.zona = id ?? "";
    zona.isi = isi;
    zona.addEventListener("click", (e) => {
      if (e.target.closest(".chip")) return;
      taruh(id);
    });
    return zona;
  }

  const bank = buatZona(null, "Ketuk lalu taruh di kotak:");
  const zonaKotak = kotak.map((k) => buatZona(k.id, k.label));
  node.append(bank, el("div", { class: "zona-kotak" }, zonaKotak));

  function segarkan() {
    for (const [id, b] of Object.entries(chip)) b.setAttribute("aria-pressed", String(id === terpilih));
    node.classList.toggle("ada-terpilih", Boolean(terpilih));
  }

  function pindah(id, zonaId) {
    if (zonaId) penempatan[id] = zonaId;
    else delete penempatan[id];
    const tujuan = zonaId ? zonaKotak.find((z) => z.dataset.zona === zonaId) : bank;
    tujuan.isi.append(chip[id]);
  }

  function pilih(id) {
    if (terkunci) return;
    terpilih = terpilih === id ? null : id;
    segarkan();
  }

  function taruh(zonaId) {
    if (terkunci || !terpilih) return;
    pindah(terpilih, zonaId);
    terpilih = null;
    segarkan();
  }

  function zonaDi(x, y, kecuali) {
    for (const e of document.elementsFromPoint(x, y)) {
      if (e === kecuali) continue;
      const z = e.closest?.(".zona");
      if (z && node.contains(z)) return z;
    }
    return null;
  }

  function sorot(zona) {
    for (const z of [bank, ...zonaKotak]) z.classList.toggle("sorot", z === zona);
  }

  function pasangSeret(b, id) {
    let awal = null;
    let seret = false;
    let abaikanKlik = false;

    const selesai = (e, batal) => {
      if (!awal) return;
      const tadiSeret = seret;
      awal = null;
      seret = false;
      b.classList.remove("diseret");
      b.style.transform = "";
      sorot(null);
      if (tadiSeret) {
        abaikanKlik = true;
        if (!batal) {
          const z = zonaDi(e.clientX, e.clientY, b);
          if (z) {
            pindah(id, z.dataset.zona || null);
            terpilih = null;
            segarkan();
          }
        }
      }
    };

    b.addEventListener("pointerdown", (e) => {
      if (terkunci || e.button > 0) return;
      awal = { x: e.clientX, y: e.clientY };
      seret = false;
      b.setPointerCapture(e.pointerId);
    });
    b.addEventListener("pointermove", (e) => {
      if (!awal) return;
      const dx = e.clientX - awal.x;
      const dy = e.clientY - awal.y;
      if (!seret && Math.hypot(dx, dy) > 8) {
        seret = true;
        b.classList.add("diseret");
      }
      if (seret) {
        b.style.transform = `translate(${dx}px, ${dy}px)`;
        sorot(zonaDi(e.clientX, e.clientY, b));
      }
    });
    b.addEventListener("pointerup", (e) => selesai(e, false));
    b.addEventListener("pointercancel", (e) => selesai(e, true));
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      if (abaikanKlik) {
        abaikanKlik = false;
        return;
      }
      pilih(id);
    });
  }

  for (const it of item) {
    const b = el("button", { type: "button", class: "chip", "aria-pressed": "false" }, it.teks);
    chip[it.id] = b;
    pasangSeret(b, it.id);
    bank.isi.append(b);
  }

  return {
    node,
    ambil: () => ({ penempatan: { ...penempatan } }),
    kosong: () => Object.keys(penempatan).length === 0,
    kunci() {
      terkunci = true;
      terpilih = null;
      segarkan();
      for (const b of Object.values(chip)) b.disabled = true;
    },
  };
}
