"""Klien model bahasa: API bergaya OpenAI (DeepSeek / OpenRouter) dan tiruan (mock).

Format: POST {base_url}/chat/completions dengan header Authorization: Bearer <key>.
- DeepSeek resmi : base_url https://api.deepseek.com      (https://api-docs.deepseek.com)
- OpenRouter     : base_url https://openrouter.ai/api/v1  (https://openrouter.ai/docs)
Hanya pustaka standar yang dipakai (urllib).
"""

from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .konfigurasi import MODE_DEEPSEEK, MODE_TIRUAN, KonfigurasiAsisten

Pesan = dict[str, str]  # {"role": "system" | "user" | "assistant", "content": "..."}

PANJANG_RINCIAN_MAKS = 300

CATATAN_TERPOTONG = "(Jawaban dipersingkat. Tanyakan lagi jika ingin penjelasan lanjutannya.)"


def potong_ke_kalimat_utuh(teks: str) -> str:
    """Buang potongan kalimat terakhir yang tidak selesai, lalu beri catatan singkat.

    Batas kalimat: titik/tanda tanya/tanda seru yang diikuti spasi atau baris baru, atau
    baris baru (langkah hitung ditulis satu per baris). Angka desimal seperti 1,8 atau
    1.200 tidak dianggap batas kalimat.
    """
    bersih = teks.rstrip()
    batas = -1
    for i, c in enumerate(bersih):
        akhir_kalimat = c in ".!?" and (i + 1 == len(bersih) or bersih[i + 1] in " \n")
        if akhir_kalimat or c == "\n":
            batas = i
    if batas < len(bersih) * 0.3:  # hampir tidak ada yang utuh: biarkan, tetap beri catatan
        return f"{bersih} …\n\n{CATATAN_TERPOTONG}"
    return f"{bersih[: batas + 1].rstrip()}\n\n{CATATAN_TERPOTONG}"


@dataclass(frozen=True)
class HasilLLM:
    teks: str
    model: str
    token_masuk: int | None = None
    token_keluar: int | None = None


class GalatLLM(Exception):
    """Galat saat memanggil model. Pesannya aman dicatat: tidak pernah memuat API key.

    `pesan` ditulis untuk pengembang/peneliti (log server & database), BUKAN untuk siswa.
    Siswa tetap melihat pesan umum dari routes_asisten.py.
    """

    def __init__(self, pesan: str, status: int | None = None) -> None:
        super().__init__(pesan)
        self.pesan = pesan
        self.status = status


class KlienLLM(Protocol):
    sumber: str

    def balas(self, pesan: list[Pesan]) -> HasilLLM: ...


def nama_penyedia(base_url: str) -> str:
    return "OpenRouter" if "openrouter.ai" in base_url.lower() else "DeepSeek"


def _pesan_http(kode: int, penyedia: str) -> str:
    tabel = {
        400: f"Permintaan ke {penyedia} tidak valid (periksa DEEPSEEK_MODEL).",
        401: f"API key ditolak {penyedia}. Periksa DEEPSEEK_API_KEY.",
        402: f"Saldo/kredit akun {penyedia} tidak cukup.",
        403: f"Akses ke model ditolak {penyedia} (kebijakan atau moderasi).",
        404: f"Model tidak ditemukan atau tidak tersedia di {penyedia} (periksa DEEPSEEK_MODEL).",
        408: f"{penyedia} kehabisan waktu menunggu model.",
        422: f"Parameter permintaan ke {penyedia} tidak valid.",
        429: f"Batas permintaan {penyedia} tercapai (kuota/menit atau kuota harian).",
    }
    if kode in tabel:
        return tabel[kode]
    if kode >= 500:
        return f"Server {penyedia} atau penyedia model sedang bermasalah (HTTP {kode})."
    return f"{penyedia} menolak permintaan (HTTP {kode})."


def _rincian_dari_badan(badan: bytes, api_key: str) -> str:
    """Ambil pesan galat dari badan respons ({"error": {"message": ...}}), tanpa API key."""
    teks = badan.decode("utf-8", errors="replace").strip()
    try:
        data = json.loads(teks)
        galat = data.get("error") if isinstance(data, dict) else None
        if isinstance(galat, dict):
            teks = str(galat.get("message") or "")
            mentah = (galat.get("metadata") or {}).get("raw")
            if mentah:
                teks = f"{teks} | {mentah}"
        elif isinstance(galat, str):
            teks = galat
    except (json.JSONDecodeError, AttributeError):
        pass
    if api_key:
        teks = teks.replace(api_key, "[KEY]")
    return teks[:PANJANG_RINCIAN_MAKS]


class KlienDeepSeek:
    """Klien untuk API bergaya OpenAI. Dipakai untuk DeepSeek resmi maupun OpenRouter."""

    sumber = "deepseek"

    def __init__(
        self,
        konfigurasi: KonfigurasiAsisten,
        buka: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        if not konfigurasi.api_key:
            raise ValueError("DEEPSEEK_API_KEY belum diatur.")
        self._k = konfigurasi
        self._buka = buka
        self._penyedia = nama_penyedia(konfigurasi.base_url)

    def __repr__(self) -> str:  # jangan pernah menampilkan API key
        return f"KlienDeepSeek(model={self._k.model!r}, base_url={self._k.base_url!r})"

    def _galat(self, pesan: str, rincian: str = "", status: int | None = None) -> GalatLLM:
        teks = f"{pesan} Rincian: {rincian}" if rincian else pesan
        return GalatLLM(teks, status)

    def balas(self, pesan: list[Pesan]) -> HasilLLM:
        k = self._k
        p = self._penyedia
        badan = json.dumps(
            {
                "model": k.model,
                "messages": pesan,
                "max_tokens": k.maks_token,
                "temperature": k.suhu,
                "stream": False,
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {k.api_key}",
        }
        if p == "OpenRouter":
            headers["X-Title"] = "SegiPintar"  # opsional, nama aplikasi di dasbor OpenRouter
        permintaan = urllib.request.Request(
            f"{k.base_url.rstrip('/')}/chat/completions",
            data=badan,
            method="POST",
            headers=headers,
        )

        try:
            with self._buka(permintaan, timeout=k.batas_waktu) as respons:
                mentah = respons.read()
        except urllib.error.HTTPError as e:
            try:
                rincian = _rincian_dari_badan(e.read() or b"", k.api_key)
            except Exception:  # noqa: BLE001 - badan galat bisa tidak terbaca
                rincian = ""
            raise self._galat(_pesan_http(e.code, p), rincian, e.code) from None
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            alasan = getattr(e, "reason", None) or type(e).__name__
            raise self._galat(
                f"Tidak bisa terhubung ke {p} (jaringan, DNS, SSL, atau batas waktu "
                f"{k.batas_waktu:g} detik).",
                str(alasan)[:PANJANG_RINCIAN_MAKS],
            ) from None
        except http.client.HTTPException as e:
            # Bukan turunan OSError: misalnya IncompleteRead (koneksi putus di tengah
            # jawaban, sering pada model gratis yang lambat) atau BadStatusLine.
            # Tanpa ini, Flask membalas 500 HTML dan frontend hanya menampilkan
            # "Terjadi gangguan".
            raise self._galat(
                f"Koneksi ke {p} terputus saat menerima jawaban.",
                type(e).__name__,
            ) from None

        try:
            data = json.loads(mentah.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise self._galat(f"Respons {p} bukan JSON.") from None

        # OpenRouter kadang mengirim galat di dalam respons HTTP 200.
        if isinstance(data, dict) and data.get("error"):
            rincian = _rincian_dari_badan(json.dumps(data).encode("utf-8"), k.api_key)
            kode = data["error"].get("code") if isinstance(data["error"], dict) else None
            raise self._galat(
                f"{p} mengembalikan galat.", rincian, kode if isinstance(kode, int) else None
            )

        try:
            pilihan = data["choices"][0]
            pesan_model = pilihan.get("message") or {}
        except (KeyError, IndexError, TypeError):
            raise self._galat(f"Format respons {p} tidak dikenal.") from None

        teks = str(pesan_model.get("content") or "").strip()
        if not teks:
            alasan = pilihan.get("finish_reason")
            if alasan == "length" or pesan_model.get("reasoning"):
                # Model "berpikir" (reasoning) menghabiskan jatah token sebelum menjawab.
                raise self._galat(
                    "Balasan kosong: jatah token habis untuk proses berpikir model. "
                    "Naikkan ASISTEN_MAKS_TOKEN (misalnya 1000) atau pilih model lain.",
                    f"finish_reason={alasan}",
                )
            raise self._galat(f"{p} mengirim balasan kosong.", f"finish_reason={alasan}")

        if pilihan.get("finish_reason") == "length":
            # Jatah token habis di tengah jawaban: jangan tampilkan kalimat yang menggantung.
            teks = potong_ke_kalimat_utuh(teks)

        pakai = data.get("usage") or {}
        return HasilLLM(
            teks=teks,
            model=str(data.get("model") or k.model),
            token_masuk=pakai.get("prompt_tokens"),
            token_keluar=pakai.get("completion_tokens"),
        )


BALASAN_TIRUAN = (
    "Ini balasan contoh (mode tiruan). Coba ceritakan dulu: informasi apa saja yang "
    "kamu ketahui dari soal ini?"
)


class KlienTiruan:
    """Pengganti model tanpa internet: untuk tes otomatis dan mencoba alur aplikasi.

    `balasan` bisa berupa daftar teks (dipakai berurutan) atau fungsi(pesan) -> teks.
    Semua panggilan disimpan di `panggilan` agar tes bisa memeriksa apa yang dikirim.
    """

    sumber = "tiruan"

    def __init__(
        self,
        balasan: list[str] | Callable[[list[Pesan]], str] | None = None,
        galat: GalatLLM | None = None,
    ) -> None:
        self._balasan = balasan
        self._galat = galat
        self.panggilan: list[list[Pesan]] = []

    def balas(self, pesan: list[Pesan]) -> HasilLLM:
        self.panggilan.append([dict(p) for p in pesan])
        if self._galat is not None:
            raise self._galat
        if callable(self._balasan):
            teks = self._balasan(pesan)
        elif self._balasan:
            teks = self._balasan.pop(0)
        else:
            teks = BALASAN_TIRUAN
        return HasilLLM(teks=teks, model="tiruan")


def buat_klien(konfigurasi: KonfigurasiAsisten) -> KlienLLM | None:
    if konfigurasi.mode == MODE_DEEPSEEK:
        return KlienDeepSeek(konfigurasi)
    if konfigurasi.mode == MODE_TIRUAN:
        return KlienTiruan()
    return None
