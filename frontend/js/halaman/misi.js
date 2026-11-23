// Game "Misi Segitiga" (F-15): cerita → satu langkah per layar → ringkasan → refleksi → skor.

import {
  buatStatusAktivitas,
  elAktivitas,
  elTujuanMakna,
  lewatiAktivitas,
  periksaAktivitas,
  tombolAktivitas,
} from "../aktivitas-rmt.js";
import { api } from "../api.js";
import { barBawah, bintangTeks, el, fmt, kotakUmpan, tombol } from "../dom.js";
import { elPesanChat } from "../format-pesan.js";
import { buatKomponen } from "../langkah.js";
import { elRemedial } from "../remedial.js";
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

  // Aktivitas pendamping RMT (tanpa skor). Jika gagal dimuat, misi tetap berjalan seperti biasa.
  let rmt = null;
  try {
    const konten = await api.rmtMisi(id);
    rmt = {
      konten,
      status: Object.fromEntries(konten.aktivitas.map((a) => [a.id, buatStatusAktivitas(a)])),
    };
  } catch {
    rmt = null;
  }
  const idTahap = (tahap) => rmt?.konten.aktivitas.find((a) => a.tahap === tahap)?.id ?? null;
  const RMT_PRA = ["input", "perencanaan", "representasi"].map(idTahap).filter(Boolean);
  const RMT_VALIDASI = idTahap("validasi");
  const RMT_TRANSENDENSI = idTahap("transendensi");
  const RMT_REFLEKSI = rmt?.konten.aktivitas.find((a) => a.tahap === "refleksi") ?? null;

  const st = {
    mainId: mulai.main_id,
    layar: "cerita",
    kalimat: 1,
    i: 0,
    sibuk: false,
    hasil: null,
    kunciLayar: null,
    chat: [],
    chatSibuk: false,
    chatTerbuka: null, // null = ikuti bawaan (tertutup sampai ada percakapan)
    remedial: null,
    rmtId: null, // aktivitas RMT yang sedang tampil (layar "rmt")
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
    const kunci = `${st.layar}-${st.i}-${st.rmtId}`;
    const pindahLayar = kunci !== st.kunciLayar;
    st.kunciLayar = kunci;
    app.replaceChildren();
    const layar = {
      cerita: layarCerita,
      rmt: layarRmt,
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
          semua && !RMT_PRA.length ? "Mulai langkah 1" : "Lanjut",
          () => {
            if (semua && RMT_PRA.length) {
              keRmt(RMT_PRA[0]);
              return;
            }
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

  // ---------- layar aktivitas RMT (tanpa skor, boleh dilewati)
  function keRmt(idAktivitas) {
    st.layar = "rmt";
    st.rmtId = idAktivitas;
    render();
  }

  function posisiRmt() {
    const urut = RMT_PRA.indexOf(st.rmtId);
    if (urut >= 0) return `Misi ${misi.id} · Sebelum mengerjakan (${urut + 1} dari ${RMT_PRA.length})`;
    if (st.rmtId === RMT_VALIDASI) return `Misi ${misi.id} · Setelah mengerjakan`;
    return `Misi ${misi.id} · Setelah misi`;
  }

  function majuDariRmt() {
    const urut = RMT_PRA.indexOf(st.rmtId);
    if (urut >= 0 && urut < RMT_PRA.length - 1) return keRmt(RMT_PRA[urut + 1]);
    if (urut >= 0) {
      st.layar = "langkah";
      st.i = 0;
      st.rmtId = null;
      return render();
    }
    if (st.rmtId === RMT_VALIDASI) return selesaiMisi();
    st.layar = "refleksi"; // setelah transendensi
    st.rmtId = null;
    return render();
  }

  function mundurDariRmt() {
    const urut = RMT_PRA.indexOf(st.rmtId);
    if (urut > 0) return keRmt(RMT_PRA[urut - 1]);
    if (urut === 0) {
      st.layar = "cerita";
    } else if (st.rmtId === RMT_VALIDASI) {
      st.layar = "langkah";
      st.i = misi.langkah.length - 1;
    } else {
      st.layar = "ringkasan"; // dari transendensi
    }
    st.rmtId = null;
    return render();
  }

  function layarRmt() {
    const s = rmt.status[st.rmtId];
    const pembuka = st.rmtId === RMT_PRA[0] ? elTujuanMakna(rmt.konten) : null;
    app.append(
      ...elAktivitas(s, { posisi: posisiRmt(), pembuka }),
      barBawah(
        tombol("Kembali", mundurDariRmt, false, { disabled: s.sibuk || st.sibuk }),
        ...tombolAktivitas(s, {
          periksa: async () => {
            const tugas = periksaAktivitas(api, st.mainId, s);
            render(); // tampilkan tombol nonaktif selama mengirim
            await tugas;
            render(".umpan");
          },
          lewati: async () => {
            await lewatiAktivitas(api, st.mainId, s);
            majuDariRmt();
          },
          lanjut: majuDariRmt,
        }),
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
          panelPembimbing(lk),
        ),
      ),
      barBawah(
        tombol("Kembali", () => {
          if (st.i === 0 && RMT_PRA.length) return keRmt(RMT_PRA[RMT_PRA.length - 1]);
          if (st.i === 0) st.layar = "cerita";
          else st.i -= 1;
          render();
        }),
        ...tombolKanan,
      ),
    );
  }

function panelPembimbing(lk) {
  const riwayat = el(
    "div",
    { class: "chat-riwayat", "aria-live": "polite" },
    ...st.chat.map((pesan) => elPesanChat(pesan.peran, pesan.teks)),
    st.chatSibuk
      ? el("p", { class: "teks-redup chat-memuat" }, "Pembimbing sedang berpikir...")
      : null
  );

  const area = el("textarea", {
    rows: "3",
    maxlength: "500",
    placeholder: "Contoh: Aku belum paham cara mengerjakan langkah ini."
  });

  const kirim = async () => {
    const teks = area.value.trim();

    if (!teks || st.chatSibuk) return;

    st.chat.push({ peran: "siswa", teks });
    st.chatSibuk = true;
    render();

    try {
      const hasil = await api.pesanAsisten(
        st.mainId,
        lk.no,
        teks
      );

      st.chat.push({
        peran: "asisten",
        teks: hasil.balasan
      });
    } catch (e) {
      st.chat.push({
        peran: "asisten",
        teks: e.message || "Pembimbing belum bisa menjawab. Coba lagi."
      });
    } finally {
      st.chatSibuk = false;
      render();
    }
  };

  // Tertutup secara bawaan agar perhatian tidak terbagi (extraneous load); terbuka bila
  // siswa membukanya atau sudah ada percakapan.
  return el(
    "details",
    {
      class: "kartu panel-pembimbing",
      open: st.chatTerbuka ?? st.chat.length > 0,
      ontoggle: (e) => {
        st.chatTerbuka = e.currentTarget.open;
      },
    },
    el("summary", {}, "Tanya Pembimbing AI"),
    el(
      "p",
      { class: "teks-redup" },
      "Tanyakan bagian yang belum kamu pahami. Pembimbing akan membantumu secara bertahap."
    ),
    riwayat,
    area,
    tombol("Kirim pertanyaan", kirim, true, {
      disabled: st.chatSibuk
    })
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
    if (RMT_VALIDASI) return keRmt(RMT_VALIDASI); // "Cek hasilmu" sebelum misi diselesaikan
    return selesaiMisi();
  }

  async function selesaiMisi() {
    st.sibuk = true;
    try {
      st.hasil = await api.selesai(st.mainId);
      try {
        st.remedial = await api.remedial(sesi.sesi_id, st.mainId); // hanya saran, skor tetap
      } catch {
        st.remedial = null;
      }
      st.layar = "ringkasan";
      st.rmtId = null;
    } catch (e) {
      // Tampilkan galat di layar yang sedang aktif (langkah terakhir atau "Cek hasilmu").
      const s = st.layar === "rmt" ? rmt.status[st.rmtId] : st.langkah[st.i];
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
            if (RMT_TRANSENDENSI) return keRmt(RMT_TRANSENDENSI); // "Di mana lagi?"
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
    // Kalimat pembuka refleksi terpandu (RMT) — dari backend, bukan ditulis di frontend.
    const pembuka = RMT_REFLEKSI?.kalimat_pembuka?.length
      ? el(
          "div",
          { class: "kartu kartu-tujuan" },
          el("p", {}, el("strong", {}, "Boleh mulai dengan:")),
          el("ul", { class: "kalimat-pembuka" }, RMT_REFLEKSI.kalimat_pembuka.map((k) => el("li", {}, k))),
        )
      : ""; // bukan null: append() asli menulis null sebagai teks "null"
    app.append(
      el("h1", { tabindex: "-1" }, "Jelaskan ke temanmu"),
      el("p", {}, "Bayangkan temanmu belum paham misi ini. Tulis caranya dengan kalimatmu sendiri."),
      pembuka,
      el("label", { for: "refleksi" }, "Penjelasanmu (boleh dilewati)"),
      area,
      barBawah(
        tombol("Lewati", async () => {
          if (RMT_REFLEKSI) {
            await lewatiAktivitas(api, st.mainId, rmt.status[RMT_REFLEKSI.id]);
          }
          keHasil();
        }),
        tombol(
          "Kirim",
          async (e) => {
            if (st.sibuk) return; // cegah ketukan ganda menyimpan refleksi dua kali
            st.sibuk = true;
            e.currentTarget.disabled = true;
            const teks = area.value.trim();
            try {
              await api.refleksi(st.mainId, area.value); // tetap dipakai rekap guru
              if (RMT_REFLEKSI && teks) await api.rmtRespons(st.mainId, RMT_REFLEKSI.id, { teks });
            } catch {
              /* refleksi opsional; tetap lanjut */
            }
            st.sibuk = false;
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
      elRemedial(st.remedial?.saran, { judul: "Perkuat dulu bagian ini" }) ?? "",
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
