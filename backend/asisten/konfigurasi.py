"""Konfigurasi chatbot dari variabel lingkungan (.env di lokal, Environment Variables di Vercel)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

MODE_DEEPSEEK = "deepseek"
MODE_TIRUAN = "tiruan"
MODE_MATI = "mati"
SEMUA_MODE = {MODE_DEEPSEEK, MODE_TIRUAN, MODE_MATI}


@dataclass(frozen=True)
class KonfigurasiAsisten:
    mode: str = MODE_MATI
    # repr=False: API key & rahasia tidak pernah tercetak di log atau pesan galat.
    api_key: str = field(default="", repr=False)
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-flash"
    batas_waktu: float = 25.0
    maks_token: int = 300
    suhu: float = 0.4
    maks_pesan_per_misi: int = 30
    maks_panjang_pesan: int = 500
    rahasia_anonim: str = field(default="", repr=False)
    peringatan: tuple[str, ...] = ()

    @property
    def aktif(self) -> bool:
        return self.mode != MODE_MATI


def _angka(env: Mapping[str, str], nama: str, bawaan: float) -> float:
    teks = (env.get(nama) or "").strip()
    if not teks:
        return bawaan
    try:
        return float(teks)
    except ValueError as e:
        raise ValueError(f"{nama} harus berupa angka.") from e


def dari_env(env: Mapping[str, str] | None = None) -> KonfigurasiAsisten:
    """Baca konfigurasi. Tanpa API key, mode 'deepseek' otomatis turun menjadi 'mati'."""
    env = os.environ if env is None else env
    api_key = (env.get("DEEPSEEK_API_KEY") or "").strip()
    mode = (env.get("SEGIPINTAR_ASISTEN") or "").strip().lower()
    peringatan: list[str] = []

    if not mode:
        mode = MODE_DEEPSEEK if api_key else MODE_MATI
    if mode not in SEMUA_MODE:
        raise ValueError(
            f"SEGIPINTAR_ASISTEN harus salah satu dari: {', '.join(sorted(SEMUA_MODE))}."
        )
    if mode == MODE_DEEPSEEK and not api_key:
        peringatan.append(
            "Mode deepseek dipilih tetapi DEEPSEEK_API_KEY kosong; chatbot dimatikan."
        )
        mode = MODE_MATI

    rahasia = (env.get("SEGIPINTAR_RAHASIA_ANONIM") or "").strip()
    if mode != MODE_MATI and not rahasia:
        peringatan.append(
            "SEGIPINTAR_RAHASIA_ANONIM kosong; kode anonim tetap dibuat, tetapi sebaiknya diisi."
        )

    return KonfigurasiAsisten(
        mode=mode,
        api_key=api_key,
        base_url=(env.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com").strip(),
        model=(env.get("DEEPSEEK_MODEL") or "deepseek-flash").strip(),
        batas_waktu=_angka(env, "ASISTEN_BATAS_WAKTU", 25.0),
        maks_token=int(_angka(env, "ASISTEN_MAKS_TOKEN", 300)),
        maks_pesan_per_misi=int(_angka(env, "ASISTEN_MAKS_PESAN_PER_MISI", 30)),
        maks_panjang_pesan=int(_angka(env, "ASISTEN_MAKS_PANJANG_PESAN", 500)),
        rahasia_anonim=rahasia,
        peringatan=tuple(peringatan),
    )
