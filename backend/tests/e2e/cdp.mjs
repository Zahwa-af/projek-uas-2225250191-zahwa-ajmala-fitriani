// Helper uji tampilan dengan Edge headless lewat Chrome DevTools Protocol (tanpa dependensi).
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export const tidur = (ms) => new Promise((r) => setTimeout(r, ms));

export async function mulaiBrowser({ dir, base, port = 9335, nama = "uji" }) {
  const shots = join(dir, `shots-${nama}`);
  mkdirSync(shots, { recursive: true });
  const exe = process.env.EDGE || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
  const edge = spawn(exe, [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${join(dir, `edge-profil-${nama}`)}`,
    "--no-first-run",
    "--disable-extensions",
    "about:blank",
  ]);
  for (let i = 0; i < 50; i++) {
    try {
      await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
      break;
    } catch {
      await tidur(200);
    }
  }
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener("open", r));

  let id = 0;
  const tunggu = new Map();
  const galat = [];
  const hasil = [];
  const melebar = [];
  let jumlahGagal = 0;
  ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && tunggu.has(m.id)) {
      tunggu.get(m.id)(m);
      tunggu.delete(m.id);
    } else if (m.method === "Runtime.exceptionThrown") {
      galat.push("EXC: " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
    } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
      galat.push("CONSOLE: " + m.params.args.map((a) => a.value ?? a.description).join(" "));
    }
  });
  const cmd = (method, params = {}) =>
    new Promise((r) => {
      const i = ++id;
      tunggu.set(i, r);
      ws.send(JSON.stringify({ id: i, method, params }));
    });
  await cmd("Runtime.enable");
  await cmd("Page.enable");

  const gagal = (pesan) => {
    jumlahGagal++;
    hasil.push("GAGAL  " + pesan);
  };
  const b = {
    cmd,
    galat,
    js: async (expr) => {
      const r = await cmd("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
      if (r.result?.exceptionDetails) galat.push("EVAL: " + expr.slice(0, 80));
      return r.result?.result?.value;
    },
    ukuran: (w, h, mobile) =>
      cmd("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile }),
    async foto(namaFoto) {
      const m = await cmd("Page.getLayoutMetrics");
      const s = m.result.cssContentSize || m.result.contentSize;
      const clip = { x: 0, y: 0, width: s.width, height: Math.min(s.height, 4000), scale: 1 };
      const r = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip });
      writeFileSync(join(shots, namaFoto + ".png"), Buffer.from(r.result.data, "base64"));
    },
    async buka(url, ms = 1200) {
      await cmd("Page.navigate", { url: base + url });
      await tidur(ms);
    },
    async pergi(hash, ms = 900) {
      await b.js(`location.hash = ${JSON.stringify(hash)}`);
      await tidur(ms);
    },
    async klik(sel, teks = "", ms = 350) {
      const r = await b.js(
        `(() => { const e = [...document.querySelectorAll(${JSON.stringify(sel)})].find(x => x.textContent.includes(${JSON.stringify(teks)}) && !x.disabled); if (!e) return false; e.click(); return true; })()`,
      );
      await tidur(ms);
      if (!r) gagal(`tidak menemukan ${sel} "${teks}"`);
      return r;
    },
    isi: (sel, nilai) =>
      b.js(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); e.value = ${JSON.stringify(nilai)}; e.dispatchEvent(new Event('input')); })()`),
    teks: (sel) => b.js(`document.querySelector(${JSON.stringify(sel)})?.textContent ?? null`),
    jumlah: (sel) => b.js(`document.querySelectorAll(${JSON.stringify(sel)}).length`),
    kelasUmpan: () => b.js(`document.querySelector('.umpan')?.className ?? null`),
    gagal,
    cek(kondisi, pesan, info = "") {
      if (kondisi) hasil.push("OK     " + pesan);
      else gagal(`${pesan} ${info ?? ""}`);
    },
    async cekLebar(namaLayar, batas = 360) {
      const w = await b.js("document.documentElement.scrollWidth");
      if (w > batas) melebar.push(`${namaLayar}=${w}px`);
      if (await b.js("/\\b(null|undefined|NaN)\\b/.test(document.body.innerText)")) {
        gagal(`${namaLayar}: teks "null/undefined/NaN" tampil`);
      }
    },
    async masuk(nama = "Uji", kelas = "8z") {
      await b.buka("/");
      await b.js("(() => { try { localStorage.clear(); } catch {} })()");
      await b.buka("/");
      await b.isi("#nama", nama);
      await b.isi("#kelas", kelas);
      await b.js(`document.querySelector('form').requestSubmit()`);
      await tidur(900);
    },
    selesai() {
      console.log(hasil.join("\n"));
      console.log("\nMelebar:", melebar.length ? melebar.join(", ") : "tidak ada");
      console.log("Galat JS:", galat.length ? "\n" + galat.join("\n") : "tidak ada");
      console.log(`\n${jumlahGagal ? "ADA " + jumlahGagal + " PEMERIKSAAN GAGAL" : "SEMUA PEMERIKSAAN LULUS"}`);
      ws.close();
      edge.kill();
      process.exit(jumlahGagal || melebar.length || galat.length ? 1 : 0);
    },
  };
  return b;
}
