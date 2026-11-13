"""Fungsi bantu untuk tes: membentuk jawaban benar dari kunci di bank soal."""

from __future__ import annotations

from typing import Any


def jawaban_dari_kunci(langkah: dict[str, Any]) -> dict[str, Any]:
    kunci = langkah["kunci"]
    tipe = langkah["tipe"]
    if tipe == "pilihan":
        return {"pilihan": kunci}
    if tipe == "angka":
        # Tulis seperti siswa Indonesia: koma sebagai desimal.
        return {"nilai": str(kunci["nilai"]).replace(".", ","), "satuan": kunci.get("satuan")}
    if tipe == "rumus":
        return {"isian": [str(x).replace(".", ",") for x in kunci["isian"]]}
    if tipe == "pilah":
        return {"penempatan": dict(kunci)}
    raise ValueError(tipe)
