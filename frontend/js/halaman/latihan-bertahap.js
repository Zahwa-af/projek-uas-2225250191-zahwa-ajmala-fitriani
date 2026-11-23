// Soal Cerita Bertahap (fading, F-09). Tidak berskor.
// Tingkat 1 = contoh hampir lengkap … tingkat 4 = mandiri. Soal, kunci, dan keputusan
// naik/turun tingkat ada di server (backend/segitiga/fading.py). Satu isian per layar.

import { api } from "../api.js";
import { barBawah, el, gantiIsi, kotakUmpan, tombol } from "../dom.js";
import { buatKomponen } from "../langkah.js";
import { gambar } from "../segitiga-svg.js";
import { ambilSesi, ambilTingkatBertahap, simpanTingkatBertahap } from "../state.js";

export async function halamanLatihanBertahap(app) {
  const sesi = ambilSesi();
  let soal = null;
  let st = null;

  async function muat(tingkat) {
    soal = await api.soalBertahap(tingkat);
    st = { i: 0, salah: 0, petunjukMaks: 0, selesai: [], teksDiri: "", akhir: null, lihatPenjelasan: false };
    siapkanIsian();
    render();
    window.scrollTo(0, 0);
  }

  function siapkanIsian() {
    const isian = soal.isian[st.i];
    st.komponen = buatKomponen({ ...isian, no: `bertahap-${isian.no}` }, { kirim: periksa });
    st.umpan = null;
    st.petunjuk = [];
    st.benar = false;
    st.sibuk = false;
  }

  async function periksa() {
    if (st.sibuk || st.benar) return;
    if (st.komponen.kosong()) {
      st.umpan = ["info", "Isi jawabanmu dulu."];
      render(".umpan");
      return;
    }
    st.sibuk = true;
    try {
      const r = await api.periksaBertahap(soal.seed, soal.tingkat, soal.isian[st.i].no, st.komponen.ambil());
      st.benar = r.benar;
      st.umpan = [r.benar ? "benar" : "salah", r.umpan_balik];
      if (r.benar) {
        st.komponen.kunci();
        st.selesai.push(r.umpan_balik.replace(/^Tepat!\s*/, ""));
      } else if (r.kode !== "FORMAT_ANGKA" && r.kode !== "KOSONG") {
        st.salah += 1;
      }
    } catch (e) {
      st.umpan = ["info", e.message];
    }
    st.sibuk = false;
    render(".umpan");
  }

  async function bukaPetunjuk() {
    if (st.sibuk || st.petunjuk.length >= 3) return;
    st.sibuk = true;
    try {
      const p = await api.petunjukBertahap(soal.seed, soal.tingkat, soal.isian[st.i].no, st.petunjuk.length + 1);
      st.petunjuk.push(p.teks);
      st.petunjukMaks = Math.max(st.petunjukMaks, p.tingkat);
    } catch (e) {
      st.umpan = ["info", e.message];
    }
    st.sibuk = false;
    render(".petunjuk-item:last-of-type");
  }

  async function lanjut() {
    if (st.i < soal.isian.length - 1) {
      st.i += 1;
      siapkanIsian();
      render();
      window.scrollTo(0, 0);
      return;
    }
    st.sibuk = true;
    try {
      st.akhir = await api.selesaiBertahap(soal.seed, soal.tingkat, st.salah, st.petunjukMaks);
      simpanTingkatBertahap(sesi.sesi_id, st.akhir.tingkat_berikut);
    } catch (e) {
      st.umpan = ["info", e.message];
      st.sibuk = false;
      render(".umpan");
      return;
    }
    st.sibuk = false;
    render();
    window.scrollTo(0, 0);
  }

  function posisi() {
    return el(
      "p",
      { class: "posisi" },
      `Soal Cerita Bertahap · Tingkat ${soal.tingkat} dari ${soal.tingkat_maks}: ${soal.nama_tingkat}`,
    );
  }

  function layarSoal() {
    const isian = soal.isian[st.i];
    const sudah = [...soal.langkah_contoh.map(([j, t]) => `${j}: ${t}`), ...st.selesai];
    return [
      posisi(),
      el(
        "div",
        { class: "tata-langkah" },
        el("div", { class: "kolom-gambar" }, gambar(soal.gambar)),
        el(
          "div",
          {},
          el("ol", { class: "cerita" }, soal.cerita.map((k) => el("li", {}, k))),
          sudah.length
            ? el(
                "div",
                { class: "kartu kartu-contoh" },
                el("p", { class: "teks-redup" }, "Sudah dikerjakan:"),
                el("ol", { class: "langkah-contoh" }, sudah.map((k) => el("li", {}, k))),
              )
            : el("p", { class: "teks-redup" }, soal.keterangan),
          el(
            "h1",
            { class: "judul-langkah", tabindex: "-1" },
            el("span", { class: "label-tahap" }, `Isian ${st.i + 1} dari ${soal.isian.length}`),
            isian.instruksi,
          ),
          st.komponen.node,
          st.umpan ? kotakUmpan(st.umpan[0], st.umpan[1]) : null,
          el(
            "div",
            { class: "petunjuk" },
            st.petunjuk.map((t, k) => el("p", { class: "petunjuk-item" }, el("strong", {}, `Petunjuk ${k + 1}: `), t)),
            !st.benar && st.petunjuk.length < 3
              ? el(
                  "button",
                  { type: "button", class: "tombol-petunjuk", onclick: bukaPetunjuk, disabled: st.sibuk },
                  `💡 Buka petunjuk ${st.petunjuk.length + 1} dari 3`,
                )
              : null,
          ),
          // Bantuan tidak pernah hilang seluruhnya: contoh lengkap selalu bisa dibuka lagi.
          el("p", { class: "teks-redup" }, el("a", { href: "#/belajar/5/1" }, "Lihat lagi contoh lengkap")),
        ),
      ),
      barBawah(
        el("a", { class: "tombol", href: "#/latihan" }, "Kembali"),
        st.benar
          ? tombol(st.i < soal.isian.length - 1 ? "Lanjut" : "Selesai", lanjut, true, { disabled: st.sibuk })
          : tombol("Periksa", periksa, true, { disabled: st.sibuk }),
      ),
    ];
  }

  // Penjelasan diri (Germane): siswa menulis dulu, lalu membandingkan. Teks tidak dikirim ke server.
  function layarRefleksi() {
    const a = st.akhir;
    const area = el("textarea", { id: "penjelasan-diri", rows: "3", maxlength: "500" });
    area.value = st.teksDiri;
    area.addEventListener("input", () => {
      st.teksDiri = area.value;
    });
    return [
      posisi(),
      el("h1", { tabindex: "-1" }, "Soal selesai!"),
      kotakUmpan(a.arah === "naik" ? "benar" : "info", a.pesan),
      el("p", {}, el("strong", {}, "Jelaskan dengan kalimatmu: "), a.refleksi.tanya),
      el("label", { for: "penjelasan-diri" }, "Penjelasanmu (boleh dilewati)"),
      area,
      st.lihatPenjelasan
        ? el(
            "div",
            { class: "kartu kartu-tujuan" },
            el("p", {}, el("strong", {}, "Bandingkan dengan penjelasan ini:")),
            el("p", {}, a.refleksi.penjelasan),
          )
        : el(
            "p",
            {},
            tombol("Bandingkan penjelasanku", () => {
              st.lihatPenjelasan = true;
              render(".kartu-tujuan");
            }),
          ),
      barBawah(
        el("a", { class: "tombol", href: "#/latihan" }, "Kembali"),
        tombol("Soal berikutnya", () => muat(a.tingkat_berikut), true),
      ),
    ];
  }

  function render(fokus = null) {
    gantiIsi(app, st.akhir ? layarRefleksi() : layarSoal());
    if (fokus) app.querySelector(fokus)?.scrollIntoView({ block: "nearest" });
  }

  await muat(ambilTingkatBertahap(sesi.sesi_id));
}
