// Game "Misi Segitiga" (F-15): cerita → satu langkah per layar → ringkasan → refleksi → skor.

import { api } from "../api.js";
import { barBawah, bintangTeks, el, fmt, kotakUmpan, tombol } from "../dom.js";
import { buatKomponen } from "../langkah.js";
import { gambar } from "../segitiga-svg.js";
import { ambilSesi, simpanSesi } from "../state.js";
import { INGAT_LAGI, LENCANA_IKON } from "../teks.js";

const KODE_SALAH_HITUNG = new Set(["SALAH_HITUNG", "SALAH_DESIMAL"]);

// ------------------------------------------------------------------ daftar misi
export async function halamanDaftarMisi(app) {
  const sesi = ambilSesi();
  const daftar = await api.daftarMisi(sesi.sesi_id);
  app.append(
    el("h1", {}, "Misi Segitiga"),
    el("p", {}, "Bantu panitia sekolah menyelesaikan 4 masalah. Kerjakan langkah demi langkah."),
    el(
      "ol",
      { class: "menu" },
      daftar.map((m) => {
        const status = m.selesai
          ? el("span", { class: "status" }, bintangTeks(m.bintang), ` Skor terbaik ${fmt(m.skor)} dari 6`)
          : el("span", { class: "status" }, m.terbuka ? "Belum dikerjakan" : "🔒 Selesaikan misi sebelumnya");
        const isi = [
          el("span", { class: "nomor", "aria-hidden": "true" }, String(m.id)),
          el(
            "span",
            {},
            el("strong", {}, m.judul),
            el("span", { class: "teks-redup" }, m.indikator_singkat),
            status,
          ),
        ];
        return el(
          "li",
          {},
          m.terbuka
            ? el("a", { class: "kartu-menu", href: `#/misi/${m.id}` }, isi)
            : el("div", { class: "kartu-menu", "aria-disabled": "true" }, isi),
        );
      }),
    ),
    barBawah(el("a", { class: "tombol", href: "#/" }, "Beranda"), el("a", { class: "tombol", href: "#/hasil" }, "Hasilku")),
  );
}

// ------------------------------------------------------------------ satu misi
export async function halamanMisi(app, idTeks) {
  const id = Number(idTeks);
  let sesi = ambilSesi();
  const misi = await api.ambilMisi(id);
  let mulai;
  try {
    mulai = await api.mulaiMisi(id, sesi.sesi_id);
  } catch (e) {
    // Database server bisa direset (misal di hosting gratis): buat ulang sesi dari data di HP.
    if (e.status !== 404) throw e;
    sesi = await api.buatSesi(sesi.nama_panggilan, sesi.kode_kelas);
    simpanSesi(sesi);
    mulai = await api.mulaiMisi(id, sesi.sesi_id);
  }

  const st = {
    mainId: mulai.main_id,
    layar: "cerita",
    kalimat: 1,
    i: 0,
    sibuk: false,
    hasil: null,
    kunciLayar: null,
  };
  st.langkah = misi.langkah.map((lk) => ({
    komponen: buatKomponen(lk, { kirim: () => periksa() }),
    benar: false,
    bolehLanjut: false,
    petunjuk: [],
    umpan: null,
    jenisUmpan: null,
    kode: null,
    tingkat: 0,
  }));

  function render(fokus = null) {
    const kunci = `${st.layar}-${st.i}`;
    const pindahLayar = kunci !== st.kunciLayar;
    st.kunciLayar = kunci;
    app.replaceChildren();
    const layar = {
      cerita: layarCerita,
      langkah: layarLangkah,
      ringkasan: layarRingkasan,
      refleksi: layarRefleksi,
      hasil: layarHasil,
    }[st.layar];
    layar();
    if (pindahLayar) {
      window.scrollTo(0, 0);
      app.querySelector("h1")?.focus({ preventScroll: true });
    } else if (fokus) {
      const target = app.querySelector(fokus);
      target?.focus({ preventScroll: true });
      target?.scrollIntoView({ block: "nearest" });
    }
  }

  function daftarKalimat(sampai, sorotTerakhir = false) {
    return el(
      "ol",
      { class: "cerita" },
      misi.cerita
        .slice(0, sampai)
        .map((k, i) => el("li", { class: sorotTerakhir && i === sampai - 1 ? "baru" : null }, k)),
    );
  }

  // ---------- layar cerita: kalimat muncul satu per satu (EL01)
  function layarCerita() {
    const semua = st.kalimat >= misi.cerita.length;
    app.append(
      el("p", { class: "posisi" }, `Misi ${misi.id} · ${misi.indikator_singkat}`),
      el("h1", { tabindex: "-1" }, misi.judul),
      el(
        "div",
        { class: "tata-langkah" },
        el("div", { class: "kolom-gambar" }, gambar(misi.gambar)),
        el(
          "div",
          {},
          daftarKalimat(st.kalimat, true),
          el("p", { class: "teks-redup" }, semua ? "Ceritanya sudah lengkap." : "Ketuk Lanjut untuk membaca kalimat berikutnya."),
        ),
      ),
      barBawah(
        el("a", { class: "tombol", href: "#/misi" }, "Kembali"),
        st.kalimat > 1
          ? tombol("Ulangi", () => {
              st.kalimat = 1;
              render();
            })
          : null,
        tombol(
          semua ? "Mulai langkah 1" : "Lanjut",
          () => {
            if (semua) {
              st.layar = "langkah";
              st.i = 0;
            } else {
              st.kalimat += 1;
            }
            render();
          },
          true,
        ),
      ),
    );
  }

  // ---------- layar langkah: satu langkah per layar (IL02)
  function layarLangkah() {
    const lk = misi.langkah[st.i];
    const s = st.langkah[st.i];
    const n = misi.langkah.length;

    const progres = el(
      "ol",
      { class: "titik-progres", "aria-hidden": "true" },
      st.langkah.map((x, j) =>
        el("li", { class: [x.bolehLanjut ? "selesai" : "", j === st.i ? "sekarang" : ""].join(" ").trim() || null }),
      ),
    );

    const petunjuk = el(
      "div",
      { class: "petunjuk" },
      s.petunjuk.map((p) =>
        el("p", { class: "petunjuk-item" }, el("strong", {}, `Petunjuk ${p.tingkat}: `), p.teks),
      ),
      !s.benar && s.tingkat < 3
        ? el(
            "button",
            { type: "button", class: "tombol-petunjuk", onclick: bukaPetunjuk, disabled: st.sibuk },
            `💡 Buka petunjuk ${s.tingkat + 1} dari 3`,
          )
        : null,
    );

    const ingatLagi =
      s.kode && KODE_SALAH_HITUNG.has(s.kode)
        ? el(
            "details",
            { class: "ingat-lagi", open: true },
            el("summary", {}, "Ingat lagi: cara menghitung"),
            el("ul", {}, INGAT_LAGI.map((t) => el("li", {}, t))),
          )
        : null;

    const tombolKanan = [];
    if (!s.benar) tombolKanan.push(tombol("Periksa", periksa, !s.bolehLanjut, { disabled: st.sibuk }));
    if (s.bolehLanjut) {
      tombolKanan.push(tombol(st.i < n - 1 ? "Lanjut" : "Selesai", lanjut, true, { disabled: st.sibuk }));
    }

    app.append(
      el(
        "div",
        { class: "kepala-langkah" },
        el("p", { class: "posisi" }, `Misi ${misi.id} · Langkah ${st.i + 1} dari ${n}`),
        progres,
      ),
      el(
        "div",
        { class: "tata-langkah" },
        el(
          "div",
          { class: "kolom-gambar" },
          el("details", { class: "cerita-lagi" }, el("summary", {}, "Lihat cerita lagi"), daftarKalimat(misi.cerita.length)),
          gambar(lk.gambar ?? misi.gambar),
        ),
        el(
          "div",
          {},
          el("h1", { class: "judul-langkah", tabindex: "-1" }, el("span", { class: "label-tahap" }, lk.judul), lk.instruksi),
          s.komponen.node,
          s.umpan ? kotakUmpan(s.jenisUmpan, s.umpan) : null,
          ingatLagi,
          petunjuk,
        ),
      ),
      barBawah(
        tombol("Kembali", () => {
          if (st.i === 0) st.layar = "cerita";
          else st.i -= 1;
          render();
        }),
        ...tombolKanan,
      ),
    );
  }

  async function periksa() {
    const lk = misi.langkah[st.i];
    const s = st.langkah[st.i];
    if (st.sibuk || s.benar) return;
    if (s.komponen.kosong()) {
      s.umpan = lk.tipe === "pilah" ? "Tempatkan dulu semua informasinya." : "Isi jawabanmu dulu.";
      s.jenisUmpan = "info";
      s.kode = null;
      render(".umpan");
      return;
    }
    st.sibuk = true;
    try {
      const r = await api.periksa(st.mainId, lk.no, s.komponen.ambil());
      s.benar = r.benar;
      s.kode = r.kode_diagnosis;
      s.umpan = r.umpan_balik;
      s.jenisUmpan = r.benar ? "benar" : "salah";
      s.tingkat = r.tingkat_petunjuk;
      s.bolehLanjut = r.boleh_lanjut;
      s.petunjuk.push(...r.petunjuk_baru);
      if (r.benar) s.komponen.kunci();
    } catch (e) {
      s.umpan = e.message;
      s.jenisUmpan = "info";
    } finally {
      st.sibuk = false;
    }
    render(".umpan");
  }

  async function bukaPetunjuk() {
    const lk = misi.langkah[st.i];
    const s = st.langkah[st.i];
    if (st.sibuk) return;
    st.sibuk = true;
    try {
      const r = await api.petunjuk(st.mainId, lk.no);
      s.petunjuk.push(...r.petunjuk_baru);
      s.tingkat = r.tingkat_petunjuk;
      s.bolehLanjut = s.bolehLanjut || r.boleh_lanjut;
    } catch (e) {
      s.umpan = e.message;
      s.jenisUmpan = "info";
    } finally {
      st.sibuk = false;
    }
    render(".petunjuk-item:last-of-type");
  }

  async function lanjut() {
    if (st.i < misi.langkah.length - 1) {
      st.i += 1;
      render();
      return;
    }
    st.sibuk = true;
    try {
      st.hasil = await api.selesai(st.mainId);
      st.layar = "ringkasan";
    } catch (e) {
      const s = st.langkah[st.i];
      s.umpan = e.message;
      s.jenisUmpan = "info";
    } finally {
      st.sibuk = false;
    }
    render();
  }

  // ---------- ringkasan: semua langkah berurutan untuk membangun skema (GL01)
  function layarRingkasan() {
    app.append(
      el("h1", { tabindex: "-1" }, "Ringkasan langkahmu"),
      el("p", {}, "Ini cara lengkap menyelesaikan misi. Baca sekali lagi pelan-pelan."),
      el(
        "ol",
        { class: "ringkasan" },
        st.hasil.ringkasan.map((r, j) =>
          el("li", {}, el("strong", {}, `${j + 1}. ${r.judul}`), el("p", {}, r.penjelasan)),
        ),
      ),
      barBawah(
        null,
        tombol(
          "Lanjut",
          () => {
            st.layar = "refleksi";
            render();
          },
          true,
        ),
      ),
    );
  }

  // ---------- refleksi: jelaskan ke teman (GL04)
  function layarRefleksi() {
    const area = el("textarea", { id: "refleksi", rows: "5", maxlength: "1000" });
    const keHasil = () => {
      st.layar = "hasil";
      render();
    };
    app.append(
      el("h1", { tabindex: "-1" }, "Jelaskan ke temanmu"),
      el("p", {}, "Bayangkan temanmu belum paham misi ini. Tulis caranya dengan kalimatmu sendiri."),
      el("label", { for: "refleksi" }, "Penjelasanmu (boleh dilewati)"),
      area,
      barBawah(
        tombol("Lewati", keHasil),
        tombol(
          "Kirim",
          async () => {
            try {
              await api.refleksi(st.mainId, area.value);
            } catch {
              /* refleksi opsional; tetap lanjut */
            }
            keHasil();
          },
          true,
        ),
      ),
    );
  }

  // ---------- hasil
  function layarHasil() {
    const h = st.hasil;
    app.append(
      el("h1", { tabindex: "-1" }, `Misi ${misi.id} selesai!`),
      el(
        "div",
        { class: "kartu" },
        el("p", { class: "skor-besar" }, `${fmt(h.skor)} dari ${fmt(h.maks)}`),
        el("p", {}, bintangTeks(h.bintang)),
        h.lencana
          ? el("p", {}, "Lencana: ", el("span", { class: "lencana" }, `${LENCANA_IKON[h.lencana] ?? ""} ${h.lencana}`))
          : el("p", { class: "teks-redup" }, "Dapatkan skor 4 atau lebih untuk meraih lencana."),
      ),
      el("h2", {}, "Skor per tahap"),
      el(
        "table",
        { class: "tabel" },
        el("thead", {}, el("tr", {}, el("th", {}, "Tahap"), el("th", {}, "Skor"))),
        el(
          "tbody",
          {},
          h.rincian.map((r) => el("tr", {}, el("td", {}, `Tahap ${r.tahap}`), el("td", {}, `${fmt(r.skor)} dari ${fmt(r.maks)}`))),
        ),
      ),
      el("p", { class: "teks-redup" }, "Skor suatu tahap menjadi 0 jika petunjuk ke-3 (cara lengkap) dibuka."),
      barBawah(
        el("a", { class: "tombol", href: "#/misi" }, "Daftar misi"),
        misi.id < 4
          ? el("a", { class: "tombol tombol-utama", href: `#/misi/${misi.id + 1}` }, "Misi berikutnya")
          : el("a", { class: "tombol tombol-utama", href: "#/hasil" }, "Lihat hasilku"),
      ),
    );
  }

  render();
}
