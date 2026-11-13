"""Membuat soal latihan secara acak namun dapat diulang (berdasarkan seed).

Saat ini: mini-game "Tunjuk Tingginya" (F-02).
Soal dibuat ulang dari seed saat diperiksa, jadi kunci tidak perlu dikirim ke browser.
"""

from __future__ import annotations

import random
from typing import Any

JENIS = ("lancip", "siku-siku", "tumpul")
Y_ALAS = 85.0

PESAN_KANDIDAT = {
    "tinggi": "Tepat! Garis ini tegak lurus dengan alas dan berangkat dari titik puncak.",
    "miring": "Garis ini memang dari titik puncak ke alas, tetapi tidak tegak lurus. "
    "Tinggi harus membentuk sudut siku-siku dengan alas.",
    "sisi": "Garis ini adalah sisi segitiga, bukan tinggi. "
    "Tinggi harus tegak lurus dengan alas.",
}


def _titik(x: float, y: float) -> dict[str, float]:
    return {"x": round(x, 1), "y": round(y, 1)}


def buat_soal_tinggi(seed: int) -> dict[str, Any]:
    """Segitiga dengan alas mendatar dan 3 garis kandidat; satu di antaranya tinggi."""
    rng = random.Random(seed)
    jenis = JENIS[seed % 3]
    y_puncak = rng.uniform(20, 35)
    if jenis == "lancip":
        ax, bx = 12.0, 88.0
        px = rng.uniform(32, 68)
        sisi_ke = rng.choice([ax, bx])
    elif jenis == "siku-siku":
        ax, bx = 18.0, 88.0
        px = ax
        sisi_ke = bx  # sisi tegak AC adalah tinggi, jadi pengecohnya sisi miring CB
    else:  # tumpul: kaki tinggi di perpanjangan alas
        ax, bx = 45.0, 92.0
        px = rng.uniform(12, 25)
        sisi_ke = ax

    # Garis miring: dari puncak ke titik di alas yang bukan kaki tinggi.
    pilihan_x = [
        x for x in (ax + f * (bx - ax) for f in (0.2, 0.35, 0.65, 0.8)) if abs(x - px) > 12
    ]
    miring_x = rng.choice(pilihan_x)

    kandidat = [
        {"peran": "tinggi", "dari": _titik(px, y_puncak), "ke": _titik(px, Y_ALAS)},
        {"peran": "miring", "dari": _titik(px, y_puncak), "ke": _titik(miring_x, Y_ALAS)},
        {"peran": "sisi", "dari": _titik(px, y_puncak), "ke": _titik(sisi_ke, Y_ALAS)},
    ]
    rng.shuffle(kandidat)
    for kode, k in zip("PQR", kandidat, strict=True):
        k["id"] = kode

    return {
        "seed": seed,
        "jenis": jenis,
        "titik": {
            "A": _titik(ax, Y_ALAS),
            "B": _titik(bx, Y_ALAS),
            "C": _titik(px, y_puncak),
        },
        "kandidat": kandidat,
    }


def soal_tinggi_publik(soal: dict[str, Any]) -> dict[str, Any]:
    """Hilangkan peran (kunci) dari kandidat sebelum dikirim ke browser."""
    return {
        **soal,
        "kandidat": [{k: v for k, v in c.items() if k != "peran"} for c in soal["kandidat"]],
    }


def periksa_soal_tinggi(seed: int, pilihan: str) -> dict[str, Any]:
    soal = buat_soal_tinggi(seed)
    benar_id = next(c["id"] for c in soal["kandidat"] if c["peran"] == "tinggi")
    dipilih = next((c for c in soal["kandidat"] if c["id"] == pilihan), None)
    if dipilih is None:
        return {
            "benar": False,
            "umpan_balik": "Pilih salah satu garis: P, Q, atau R.",
            "kunci": None,
        }
    pesan = PESAN_KANDIDAT[dipilih["peran"]]
    if soal["jenis"] == "tumpul":
        pesan += " Pada segitiga tumpul, tinggi jatuh di perpanjangan alas."
    return {"benar": dipilih["peran"] == "tinggi", "umpan_balik": pesan, "kunci": benar_id}
