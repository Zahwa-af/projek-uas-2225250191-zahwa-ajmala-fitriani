"""Tes fondasi chatbot DeepSeek. Semua memakai klien tiruan atau urlopen palsu (tanpa internet)."""

import io
import json
import subprocess
import urllib.error
from pathlib import Path

import pytest

from app import buat_app
from asisten.anonim import kode_anonim, samarkan
from asisten.klien import GalatLLM, KlienDeepSeek, KlienTiruan, buat_klien
from asisten.konfigurasi import KonfigurasiAsisten, dari_env
from asisten.pengaman import PENGGANTI, larangan, periksa_balasan
from asisten.prompt import StatusSiswa, susun_pesan, teks_kunci
from bantuan import jawaban_dari_kunci
from segitiga import bank_soal

AKAR = Path(__file__).resolve().parents[2]
KUNCI_PALSU = "sk-tes-INI-BUKAN-KUNCI-ASLI-123456"


def _langkah(misi_id, no):
    misi = bank_soal.ambil_misi(misi_id)
    return misi, bank_soal.cari_langkah(misi, no)


# ------------------------------------------------------------------ konfigurasi
def test_tanpa_key_mode_mati():
    k = dari_env({})
    assert k.mode == "mati" and not k.aktif


def test_ada_key_otomatis_deepseek():
    k = dari_env({"DEEPSEEK_API_KEY": KUNCI_PALSU})
    assert k.mode == "deepseek" and k.model == "deepseek-flash"


def test_mode_deepseek_tanpa_key_turun_ke_mati():
    k = dari_env({"SEGIPINTAR_ASISTEN": "deepseek"})
    assert k.mode == "mati" and k.peringatan


def test_mode_tidak_dikenal_ditolak():
    with pytest.raises(ValueError):
        dari_env({"SEGIPINTAR_ASISTEN": "gpt"})


def test_api_key_tidak_tampil_di_repr():
    k = dari_env({"DEEPSEEK_API_KEY": KUNCI_PALSU, "SEGIPINTAR_RAHASIA_ANONIM": "garam"})
    assert KUNCI_PALSU not in repr(k) and "garam" not in repr(k)
    assert KUNCI_PALSU not in repr(KlienDeepSeek(k))


def test_buat_klien_sesuai_mode():
    assert buat_klien(KonfigurasiAsisten(mode="mati")) is None
    assert isinstance(buat_klien(KonfigurasiAsisten(mode="tiruan")), KlienTiruan)
    assert isinstance(
        buat_klien(KonfigurasiAsisten(mode="deepseek", api_key=KUNCI_PALSU)), KlienDeepSeek
    )


# ------------------------------------------------------------------ klien DeepSeek (urlopen palsu)
class _Respons(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_klien_deepseek_format_permintaan_dan_balasan():
    terkirim = {}

    def buka(req, timeout):
        terkirim.update(
            url=req.full_url,
            header=dict(req.header_items()),
            badan=json.loads(req.data),
            timeout=timeout,
        )
        return _Respons(
            json.dumps(
                {
                    "model": "deepseek-flash",
                    "choices": [
                        {"message": {"role": "assistant", "content": " Apa yang ditanyakan? "}}
                    ],
                    "usage": {"prompt_tokens": 120, "completion_tokens": 15},
                }
            ).encode()
        )

    k = KonfigurasiAsisten(
        mode="deepseek", api_key=KUNCI_PALSU, base_url="https://api.deepseek.com/"
    )
    hasil = KlienDeepSeek(k, buka=buka).balas([{"role": "user", "content": "halo"}])
    assert terkirim["url"] == "https://api.deepseek.com/chat/completions"
    assert terkirim["header"]["Authorization"] == f"Bearer {KUNCI_PALSU}"
    assert terkirim["badan"]["model"] == "deepseek-flash"
    assert terkirim["badan"]["stream"] is False
    assert terkirim["timeout"] == 25.0
    assert hasil.teks == "Apa yang ditanyakan?"
    assert (hasil.token_masuk, hasil.token_keluar) == (120, 15)


@pytest.mark.parametrize(
    ("galat", "potongan"),
    [
        (urllib.error.HTTPError("u", 401, "x", {}, None), "ditolak"),
        (urllib.error.HTTPError("u", 402, "x", {}, None), "Saldo"),
        (urllib.error.HTTPError("u", 503, "x", {}, None), "bermasalah"),
        (urllib.error.URLError("dns"), "terhubung"),
        (TimeoutError(), "terhubung"),
    ],
)
def test_klien_deepseek_galat_tanpa_bocor_key(galat, potongan):
    def buka(req, timeout):
        raise galat

    k = KonfigurasiAsisten(mode="deepseek", api_key=KUNCI_PALSU)
    with pytest.raises(GalatLLM) as info:
        KlienDeepSeek(k, buka=buka).balas([{"role": "user", "content": "halo"}])
    assert potongan in info.value.pesan
    assert KUNCI_PALSU not in str(info.value) and info.value.__cause__ is None


def test_klien_deepseek_balasan_kosong_atau_rusak():
    k = KonfigurasiAsisten(mode="deepseek", api_key=KUNCI_PALSU)
    for isi in (
        b"bukan json",
        json.dumps({"choices": []}).encode(),
        json.dumps({"choices": [{"message": {"content": "  "}}]}).encode(),
    ):
        with pytest.raises(GalatLLM):
            KlienDeepSeek(k, buka=lambda req, timeout, isi=isi: _Respons(isi)).balas([])


# ------------------------------------------------------------------ anonim
def test_kode_anonim_stabil_dan_tidak_memuat_sesi_id():
    a = kode_anonim("abc123def456", "rahasia")
    assert a == kode_anonim("abc123def456", "rahasia")
    assert a != kode_anonim("abc123def456", "lain")
    assert a.startswith("S-") and "abc123" not in a.lower()


def test_samarkan_data_pribadi():
    teks, berubah = samarkan(
        "Aku Zahra, email zahra@sekolah.id, wa 0812-3456-7890, "
        "NIK 3201234567890123. Luasnya 1.200?",
        nama="zahra",
    )
    assert berubah
    assert "Zahra" not in teks and "zahra@" not in teks
    assert "0812" not in teks and "3201234567890123" not in teks
    assert "1.200" in teks  # angka soal tidak boleh ikut tersamarkan


def test_samarkan_tidak_mengubah_pertanyaan_biasa():
    teks = "Kenapa luasnya dikali ½? Alas 60 cm dan tinggi 40 cm."
    assert samarkan(teks, nama="Ani") == (teks, False)


# ------------------------------------------------------------------ prompt
def test_prompt_berisi_konteks_tanpa_identitas():
    misi, lk = _langkah(1, "2a")
    st = StatusSiswa(percobaan_salah=1, kode_terakhir="LUPA_SETENGAH", umpan_terakhir="Lupa ½")
    pesan = susun_pesan(misi, lk, st, [{"role": "user", "content": "lama"}], "bingung")
    sistem = pesan[0]["content"]
    assert pesan[0]["role"] == "system" and pesan[-1] == {"role": "user", "content": "bingung"}
    assert "Hitung luas Desain A." in sistem and "LUPA_SETENGAH" in sistem
    assert "1.200 cm²" in sistem and "RAHASIA" in sistem
    assert "Jangan pernah menyebutkan jawaban akhir" in sistem


def test_prompt_riwayat_dibatasi():
    misi, lk = _langkah(1, "2a")
    riwayat = [{"role": "user", "content": str(i)} for i in range(20)]
    pesan = susun_pesan(misi, lk, StatusSiswa(), riwayat, "x")
    assert len(pesan) == 1 + 8 + 1


def test_tahapan_rmt_berisi_prinsip_mediasi_hanya_untuk_misi():
    # Tahap 2F: prinsip MLE dipakai chatbot misi; kerangka masih usulan (docs/07, Q1).
    from asisten import mediasi, prompt

    assert prompt.TAHAPAN_RMT == mediasi.PRINSIP_MEDIASI
    assert prompt.TAHAPAN_RMT not in prompt.INSTRUKSI_BERANDA


def test_teks_kunci_semua_langkah():
    for m in bank_soal.semua_misi():
        for lk in m["langkah"]:
            assert teks_kunci(lk)


# ------------------------------------------------------------------ pengaman
@pytest.mark.parametrize(
    "balasan", ["Luasnya 1.200 cm².", "jadi 1200", "Hasilnya 1200cm2 ya", "= 1.200."]
)
def test_pengaman_menyaring_angka_kunci(balasan):
    misi, lk = _langkah(1, "2a")
    hasil = periksa_balasan(balasan, *larangan(misi, lk))
    assert hasil.disaring and hasil.teks == PENGGANTI


@pytest.mark.parametrize(
    ("misi_id", "no", "balasan"),
    [
        (2, "6", "Biayanya Rp300.000."),
        (2, "6", "300000 rupiah"),
        (4, "3", "Luasnya 1,8 m²"),
        (4, "3", "1.8 meter persegi"),
        (3, "3b", "bunga 14 m²"),
    ],
)
def test_pengaman_berbagai_misi(misi_id, no, balasan):
    misi, lk = _langkah(misi_id, no)
    assert periksa_balasan(balasan, *larangan(misi, lk)).disaring


def test_pengaman_mengizinkan_angka_soal_dan_bimbingan():
    misi, lk = _langkah(1, "2a")
    teks = (
        "Alasnya 60 cm dan tingginya 40 cm. "
        "Kalau 60 × 40 = 2.400, lalu apa yang dilakukan dengan ½?"
    )
    hasil = periksa_balasan(teks, *larangan(misi, lk))
    assert not hasil.disaring and hasil.teks == teks


def test_pengaman_pilihan_kalimat_kunci():
    misi, lk = _langkah(4, "5")
    kunci = next(o["teks"] for o in lk["opsi"] if o["id"] == lk["kunci"])
    assert periksa_balasan(f"Jawabannya: {kunci}.", *larangan(misi, lk)).disaring
    assert not periksa_balasan(
        "Coba pisahkan: perkaliannya atau rumusnya?", *larangan(misi, lk)
    ).disaring


# ------------------------------------------------------------------ endpoint
def _app(tmp_path, klien=None, **lain):
    k = KonfigurasiAsisten(
        mode="tiruan" if klien else "mati", maks_pesan_per_misi=3, rahasia_anonim="garam", **lain
    )
    return buat_app(
        {"DB_PATH": str(tmp_path / "uji.db"), "TESTING": True, "ASISTEN": k, "ASISTEN_KLIEN": klien}
    )


def _mulai(c, nama="Zahra"):
    sesi = c.post("/api/sesi", json={"nama_panggilan": nama, "kode_kelas": "8A"}).get_json()[
        "sesi_id"
    ]
    return sesi, c.post("/api/misi/1/mulai", json={"sesi_id": sesi}).get_json()["main_id"]


def test_endpoint_mati_503(tmp_path):
    c = _app(tmp_path).test_client()
    assert c.get("/api/asisten/status").get_json()["aktif"] is False
    _, main_id = _mulai(c)
    r = c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": "halo"})
    assert r.status_code == 503


def test_endpoint_alur_dan_log_anonim(tmp_path):
    klien = KlienTiruan(["Coba lihat garis biru. Mana alasnya?"])
    app = _app(tmp_path, klien)
    c = app.test_client()
    sesi_id, main_id = _mulai(c, nama="Zahra")
    # siswa salah dulu (lupa ½) supaya konteks memuat diagnosis
    c.post(
        "/api/periksa",
        json={"main_id": main_id, "langkah": "2a", "jawaban": {"nilai": "2400", "satuan": "cm²"}},
    )

    r = c.post(
        "/api/asisten/pesan",
        json={"main_id": main_id, "langkah": "2a", "teks": "Aku Zahra, bingung kenapa salah"},
    )
    assert r.status_code == 200
    assert r.get_json() == {"balasan": "Coba lihat garis biru. Mana alasnya?", "sisa_pertanyaan": 2}

    # yang dikirim ke model: tanpa nama, tanpa sesi_id, tanpa main_id, ada diagnosis
    terkirim = json.dumps(klien.panggilan[0], ensure_ascii=False)
    assert "Zahra" not in terkirim and sesi_id not in terkirim and main_id not in terkirim
    assert "[nama]" in terkirim and "LUPA_SETENGAH" in terkirim

    import db

    conn = db.hubungkan(app.config["DB_PATH"])
    rows = conn.execute("SELECT * FROM percakapan_asisten ORDER BY id").fetchall()
    assert [r["peran"] for r in rows] == ["siswa", "asisten"]
    assert rows[0]["disamarkan"] == 1 and "Zahra" not in rows[0]["teks"]
    assert rows[0]["kode_anonim"] == kode_anonim(sesi_id, "garam")
    assert rows[0]["kode_diagnosis"] == "LUPA_SETENGAH" and rows[0]["percobaan_salah"] == 1
    assert rows[1]["sumber"] == "tiruan" and rows[1]["tahap_rmt"] == "manipulasi"  # RMT Tahap 1
    semua = json.dumps([dict(r) for r in rows], ensure_ascii=False)
    assert "Zahra" not in semua and sesi_id not in semua


def test_endpoint_riwayat_dikirim_ke_model(tmp_path):
    klien = KlienTiruan(["Balasan satu?", "Balasan dua?"])
    c = _app(tmp_path, klien).test_client()
    _, main_id = _mulai(c)
    for t in ("pertama", "kedua"):
        c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": t})
    pesan_kedua = klien.panggilan[1]
    assert [p["content"] for p in pesan_kedua[1:]] == ["pertama", "Balasan satu?", "kedua"]


def test_endpoint_menyaring_jawaban_bocor(tmp_path):
    app = _app(tmp_path, KlienTiruan(["Jawabannya 1.200 cm²."]))
    c = app.test_client()
    _, main_id = _mulai(c)
    r = c.post(
        "/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": "kasih jawabannya"}
    )
    assert r.get_json()["balasan"] == PENGGANTI
    import db

    row = (
        db.hubungkan(app.config["DB_PATH"])
        .execute("SELECT * FROM percakapan_asisten WHERE peran = 'asisten'")
        .fetchone()
    )
    assert row["disaring"] == 1 and row["teks_asli"] == "Jawabannya 1.200 cm²."


def test_endpoint_tidak_menyaring_setelah_langkah_benar(tmp_path):
    c = _app(tmp_path, KlienTiruan(["Benar, 1.200 cm². Kenapa dikali ½?"])).test_client()
    _, main_id = _mulai(c)
    c.post(
        "/api/periksa",
        json={"main_id": main_id, "langkah": "2a", "jawaban": {"nilai": "1.200", "satuan": "cm²"}},
    )
    r = c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": "kenapa?"})
    assert "1.200" in r.get_json()["balasan"]


def test_endpoint_batas_pesan_dan_validasi(tmp_path):
    c = _app(tmp_path, KlienTiruan()).test_client()
    _, main_id = _mulai(c)

    def kirim(**d):
        return c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", **d})

    assert kirim(teks="").status_code == 400
    assert kirim(teks="x" * 501).status_code == 400
    assert (
        c.post(
            "/api/asisten/pesan", json={"main_id": main_id, "langkah": "99", "teks": "a"}
        ).status_code
        == 404
    )
    assert (
        c.post(
            "/api/asisten/pesan", json={"main_id": "salah", "langkah": "2a", "teks": "a"}
        ).status_code
        == 404
    )
    for _ in range(3):
        assert kirim(teks="tanya").status_code == 200
    assert kirim(teks="tanya").status_code == 429


def test_endpoint_galat_model_503_dan_dicatat(tmp_path):
    app = _app(tmp_path, KlienTiruan(galat=GalatLLM("Saldo akun DeepSeek habis.", 402)))
    c = app.test_client()
    _, main_id = _mulai(c)
    r = c.post("/api/asisten/pesan", json={"main_id": main_id, "langkah": "2a", "teks": "halo"})
    assert r.status_code == 503 and "Saldo" not in r.get_json()["galat"]
    import db

    sumber = [
        x["sumber"]
        for x in db.hubungkan(app.config["DB_PATH"]).execute(
            "SELECT sumber FROM percakapan_asisten ORDER BY id"
        )
    ]
    assert sumber == ["tiruan", "galat"]


def test_chatbot_tidak_mengubah_skor(tmp_path):
    c = _app(tmp_path, KlienTiruan(lambda pesan: "Coba pikirkan lagi?")).test_client()
    _, main_id = _mulai(c)
    for lk in bank_soal.ambil_misi(1)["langkah"]:
        c.post(
            "/api/asisten/pesan", json={"main_id": main_id, "langkah": lk["no"], "teks": "bantu"}
        )
        c.post(
            "/api/periksa",
            json={"main_id": main_id, "langkah": lk["no"], "jawaban": jawaban_dari_kunci(lk)},
        )
    hasil = c.post("/api/misi/selesai", json={"main_id": main_id}).get_json()
    assert hasil["skor"] == 6 and hasil["total_petunjuk"] == 0


# ------------------------------------------------------------------ keamanan repo
def test_frontend_tidak_memuat_rahasia():
    for folder in ("frontend", "web-statis"):
        for f in (AKAR / folder).rglob("*"):
            if f.suffix in {".js", ".html", ".json", ".css"}:
                isi = f.read_text(encoding="utf-8")
                assert "DEEPSEEK_API_KEY" not in isi and "api.deepseek.com" not in isi, f
                assert "Bearer" not in isi, f


def test_env_diabaikan_git():
    gitignore = (AKAR / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in gitignore and "!.env.example" in gitignore
    try:
        hasil = subprocess.run(
            ["git", "check-ignore", "-q", ".env"], cwd=AKAR, capture_output=True, timeout=10
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("git tidak tersedia")
    assert hasil.returncode == 0  # 0 = .env diabaikan git


def test_env_example_tanpa_key_asli():
    for baris in (AKAR / ".env.example").read_text(encoding="utf-8").splitlines():
        if baris.startswith("DEEPSEEK_API_KEY"):
            assert baris.strip() == "DEEPSEEK_API_KEY="
