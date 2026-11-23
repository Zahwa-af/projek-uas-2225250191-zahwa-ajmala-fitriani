"""Tes RMT Tahap 2B: integrasi frontend ↔ endpoint RMT, tanpa duplikasi konten & tanpa bocor.

Uji tampilan (browser) ada di backend/tests/e2e/uji_rmt_misi.mjs (dijalankan manual).
"""

import json
from pathlib import Path

import db
from app import buat_app
from asisten.konfigurasi import KonfigurasiAsisten
from bantuan import jawaban_dari_kunci
from segitiga import aktivitas_rmt, bank_soal

AKAR = Path(__file__).resolve().parents[2]
FRONTEND = AKAR / "frontend"


def _isi_frontend() -> str:
    return "\n".join(
        f.read_text(encoding="utf-8")
        for f in FRONTEND.rglob("*")
        if f.suffix in {".js", ".html", ".css", ".json", ".webmanifest"}
    )


def _teks_konten(a: dict) -> list[str]:
    teks = [a.get("pertanyaan"), a.get("instruksi"), a.get("penjelasan"), a.get("umpan_balik")]
    teks += [o["teks"] for o in a.get("opsi", [])] + [k["teks"] for k in a.get("kartu", [])]
    teks += list((a.get("umpan_balik_opsi") or {}).values()) + list(a.get("kalimat_pembuka") or [])
    return [t for t in teks if t and len(t) >= 15]


# ------------------------------------------------------------------ konten tidak diduplikasi
def test_konten_rmt_tidak_diduplikasi_di_frontend():
    isi = _isi_frontend()
    for k in aktivitas_rmt.semua_konten():
        for t in [k["tujuan"], k["makna"]] + [x for a in k["aktivitas"] for x in _teks_konten(a)]:
            assert t not in isi, f"konten RMT tertulis langsung di frontend: {t[:50]}"


def test_frontend_memakai_endpoint_rmt():
    api_js = (FRONTEND / "js" / "api.js").read_text(encoding="utf-8")
    assert "/api/rmt/misi/" in api_js and "/api/rmt/respons" in api_js
    misi_js = (FRONTEND / "js" / "halaman" / "misi.js").read_text(encoding="utf-8")
    assert "api.rmtMisi(" in misi_js and "rmt: layarRmt" in misi_js


def test_frontend_tidak_memuat_kunci_rmt():
    isi = _isi_frontend()
    for kata in ("jawaban_sebenarnya", "umpan_balik_opsi", "a.kunci", '"kunci"', "kunci:"):
        assert kata not in isi, kata


# ------------------------------------------------------------------ alur seperti di frontend
def test_alur_misi_dengan_aktivitas_rmt(tmp_path):
    """Urutan panggilan sama dengan halaman misi: pra-RMT → langkah → cek hasil → selesai →
    transendensi → refleksi. Skor tetap 6/6 dan semua respons RMT tersimpan."""
    app = buat_app(
        {
            "DB_PATH": str(tmp_path / "uji.db"),
            "TESTING": True,
            "ASISTEN": KonfigurasiAsisten(mode="mati", rahasia_anonim="garam"),
        }
    )
    c = app.test_client()
    sesi = c.post("/api/sesi", json={"nama_panggilan": "Ani", "kode_kelas": "8A"}).get_json()
    m = c.post("/api/misi/2/mulai", json={"sesi_id": sesi["sesi_id"]})
    assert m.status_code == 403  # misi 2 masih terkunci: alur lama tetap berlaku
    m = c.post("/api/misi/1/mulai", json={"sesi_id": sesi["sesi_id"]}).get_json()["main_id"]

    konten = c.get("/api/rmt/misi/1").get_json()
    per_tahap = {a["tahap"]: a for a in konten["aktivitas"]}
    kirim = lambda a, **isi: c.post(  # noqa: E731
        "/api/rmt/respons", json={"main_id": m, "aktivitas": per_tahap[a]["id"], **isi}
    ).get_json()

    # sebelum mengerjakan
    assert kirim("input", jawaban={"pilihan": "a"})["benar"] is None
    kartu_awal = [k["id"] for k in per_tahap["perencanaan"]["kartu"]]
    assert (
        kirim("perencanaan", jawaban={"urutan": kartu_awal})["benar"] is False
    )  # urutan tampil salah
    assert kirim("perencanaan", jawaban={"urutan": ["m", "k", "t", "b"]})["benar"] is True
    assert kirim("representasi", dilewati=True)["dilewati"] is True

    # langkah berskor (tidak berubah)
    for lk in bank_soal.ambil_misi(1)["langkah"]:
        r = c.post(
            "/api/periksa",
            json={"main_id": m, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
        assert r.get_json()["benar"]

    # cek hasil SEBELUM misi diselesaikan
    assert kirim("validasi", jawaban={"pilihan": "a"})["benar"] is True
    hasil = c.post("/api/misi/selesai", json={"main_id": m}).get_json()
    assert hasil["skor"] == 6 and hasil["bintang"] == 3

    # setelah misi selesai
    assert kirim("transendensi", jawaban={"pilihan": ["a", "b"]})["benar"] is True
    teks = "Pertama aku hitung luas A dan B, lalu kubandingkan."
    assert c.post("/api/refleksi", json={"main_id": m, "teks": teks}).get_json()["tersimpan"]
    assert kirim("refleksi", jawaban={"teks": teks})["tercatat"]

    conn = db.hubungkan(app.config["DB_PATH"])
    rows = conn.execute(
        "SELECT aktivitas, tahap_rmt, dilewati, benar FROM aktivitas_rmt ORDER BY id"
    ).fetchall()
    assert [r["tahap_rmt"] for r in rows] == [
        "input",
        "perencanaan",
        "perencanaan",
        "representasi",
        "validasi",
        "transendensi",
        "refleksi",
    ]
    assert [r["dilewati"] for r in rows].count(1) == 1
    # refleksi lama (dipakai rekap guru) tetap tersimpan
    assert conn.execute("SELECT COUNT(*) FROM refleksi").fetchone()[0] == 1
    # skor tersimpan tetap 6 setelah aktivitas pasca-misi
    assert conn.execute("SELECT skor_rubrik FROM main_misi WHERE id = ?", (m,)).fetchone()[0] == 6
    assert (
        json.loads(conn.execute("SELECT rincian FROM main_misi WHERE id = ?", (m,)).fetchone()[0])[
            -1
        ]["tahap"]
        == 5
    )
