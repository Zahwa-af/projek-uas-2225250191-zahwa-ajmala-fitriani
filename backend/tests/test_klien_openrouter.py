"""Tes klien untuk OpenRouter: rincian galat, model reasoning, dan keamanan API key.

Kasus 404 meniru respons asli OpenRouter saat model ':free' tidak lagi gratis.
Tidak ada panggilan internet: urlopen diganti fungsi palsu.
"""

import io
import json
import urllib.error

import pytest

from asisten.klien import GalatLLM, KlienDeepSeek, nama_penyedia
from asisten.konfigurasi import KonfigurasiAsisten

KUNCI = "sk-or-v1-PALSU-hanya-untuk-tes-0000000000"
OR = "https://openrouter.ai/api/v1"


class _Respons(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _klien(buka, base_url=OR, model="deepseek/deepseek-v4-flash:free"):
    k = KonfigurasiAsisten(mode="deepseek", api_key=KUNCI, base_url=base_url, model=model)
    return KlienDeepSeek(k, buka=buka)


def _http_error(kode, badan: dict):
    def buka(req, timeout):
        raise urllib.error.HTTPError(
            req.full_url, kode, "err", {}, io.BytesIO(json.dumps(badan).encode())
        )

    return buka


def test_nama_penyedia():
    assert nama_penyedia(OR) == "OpenRouter"
    assert nama_penyedia("https://api.deepseek.com") == "DeepSeek"


def test_404_model_tidak_gratis_rincian_terlihat():
    badan = {
        "error": {
            "message": "This model is unavailable for free. The paid version is available now",
            "code": 404,
        },
        "user_id": "user_x",
    }
    with pytest.raises(GalatLLM) as info:
        _klien(_http_error(404, badan)).balas([{"role": "user", "content": "hai"}])
    pesan = info.value.pesan
    assert info.value.status == 404
    assert "OpenRouter" in pesan and "DEEPSEEK_MODEL" in pesan
    assert "unavailable for free" in pesan


def test_rincian_galat_tidak_membocorkan_key():
    badan = {"error": {"message": f"Invalid key {KUNCI}", "code": 401}}
    with pytest.raises(GalatLLM) as info:
        _klien(_http_error(401, badan)).balas([])
    assert KUNCI not in info.value.pesan and "[KEY]" in info.value.pesan
    assert info.value.__cause__ is None


def test_429_dan_metadata_raw_penyedia():
    badan = {
        "error": {
            "message": "Rate limit exceeded",
            "code": 429,
            "metadata": {"raw": "free-models-per-day"},
        }
    }
    with pytest.raises(GalatLLM) as info:
        _klien(_http_error(429, badan)).balas([])
    assert "Batas permintaan" in info.value.pesan and "free-models-per-day" in info.value.pesan


def test_galat_di_dalam_respons_200():
    isi = json.dumps({"error": {"message": "Provider returned error", "code": 502}}).encode()
    with pytest.raises(GalatLLM) as info:
        _klien(lambda req, timeout: _Respons(isi)).balas([])
    assert "Provider returned error" in info.value.pesan and info.value.status == 502


def test_model_reasoning_kehabisan_token():
    isi = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "", "reasoning": "Hmm, siswa bertanya..."},
                }
            ]
        }
    ).encode()
    with pytest.raises(GalatLLM) as info:
        _klien(lambda req, timeout: _Respons(isi)).balas([])
    assert "ASISTEN_MAKS_TOKEN" in info.value.pesan


def test_balasan_normal_dan_header_openrouter():
    terkirim = {}

    def buka(req, timeout):
        terkirim["header"] = {k.lower(): v for k, v in req.header_items()}
        terkirim["url"] = req.full_url
        return _Respons(
            json.dumps(
                {
                    "model": "google/gemma-4-31b-it:free",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": "Tinggi tegak lurus alas. Mana alasnya?",
                                "reasoning": "...",
                            },
                        }
                    ],
                    "usage": {"prompt_tokens": 50, "completion_tokens": 12},
                }
            ).encode()
        )

    hasil = _klien(buka).balas([{"role": "user", "content": "hai"}])
    assert hasil.teks == "Tinggi tegak lurus alas. Mana alasnya?"
    assert terkirim["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert terkirim["header"]["authorization"] == f"Bearer {KUNCI}"
    assert terkirim["header"]["x-title"] == "SegiPintar"


def test_deepseek_resmi_tanpa_header_openrouter():
    terkirim = {}

    def buka(req, timeout):
        terkirim["header"] = {k.lower() for k, _ in req.header_items()}
        return _Respons(json.dumps({"choices": [{"message": {"content": "Halo?"}}]}).encode())

    _klien(buka, base_url="https://api.deepseek.com", model="deepseek-flash").balas([])
    assert "x-title" not in terkirim["header"]


def test_galat_jaringan_menyebut_alasan():
    def buka(req, timeout):
        raise urllib.error.URLError("getaddrinfo failed")

    with pytest.raises(GalatLLM) as info:
        _klien(buka).balas([])
    assert "terhubung" in info.value.pesan and "getaddrinfo" in info.value.pesan
