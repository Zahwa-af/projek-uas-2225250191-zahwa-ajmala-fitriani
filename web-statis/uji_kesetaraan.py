"""Membuat kasus uji + hasil penilaian Python, untuk dibandingkan dengan versi JavaScript.

Pakai:  python web-statis/uji_kesetaraan.py | node web-statis/uji_kesetaraan.mjs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from segitiga import bank_soal  # noqa: E402
from segitiga.generator_soal import buat_soal_tinggi  # noqa: E402
from segitiga.parser_angka import parse_angka, parse_satuan  # noqa: E402
from segitiga.penilai import StatusLangkah, hitung_skor_misi, periksa_langkah  # noqa: E402

TEKS_ANGKA = [
    "1,8", "1.200", "Rp300.000", "rp 300.000", "Rp. 25.000", "1200 cm²", "1200cm^2", "42 m²",
    " 42 ", "1.5", "0.333", "1.200,5", "1,200.5", "1/3", "⅓", "½", "-4", "", "abc", "1/0",
    "1.2.3", "1,2,3", "cm²", "2.400", "3,60", "12m", "1 200", "1,200,000", "0,5", "−3",
]
SATUAN = ["cm2", "cm²", "CM^2", "m", "m2", "Rp", "", "kg", "mm²"]


def variasi_angka(lk):
    k = float(lk["kunci"]["nilai"])
    s = lk["kunci"].get("satuan")
    nilai = [k, k * 2, k + 1, k * 10, k / 10, k * 1.1, k * 3, 999.5]
    ktx = lk.get("konteks_diagnosis") or {}
    if ktx.get("alas"):
        nilai += [ktx["alas"] * ktx["tinggi"], ktx["alas"] + ktx["tinggi"]]
    nilai += [p["nilai"] for p in lk.get("pola_salah", [])]
    hasil = [{"nilai": str(v).replace(".", ","), "satuan": s} for v in nilai]
    hasil += [{"nilai": str(k), "satuan": x} for x in ("cm", "m", "m²", None, "cm²")]
    hasil += [{"nilai": "abc"}, {"nilai": ""}, {}]
    return hasil


def variasi(lk):
    t = lk["tipe"]
    if t == "pilihan":
        ids = [o["id"] for o in lk["opsi"]]
        v = [{"pilihan": i} for i in ids] + [{"pilihan": None}, {}]
        if isinstance(lk["kunci"], list):
            v += [{"pilihan": [a, b]} for a in ids for b in ids if a < b] + [{"pilihan": [ids[0]]}]
        return v
    if t == "angka":
        return variasi_angka(lk)
    if t == "rumus":
        k = [str(x) for x in lk["kunci"]["isian"]]
        v = [{"isian": k}, {"isian": k[::-1]}, {"isian": k[:-1]}, {"isian": [*k[:-1], "7"]}]
        v += [{"isian": ["x"] + k[1:]}, {"isian": ["99"] * len(k)}]
        for p in lk.get("pola_salah_isian", []):
            s = list(k)
            s[p["isian_ke"] - 1] = str(p["nilai"])
            v.append({"isian": s})
        return v
    if t == "pilah":
        kunci = lk["kunci"]
        ids = list(kunci)
        tukar = dict(kunci)
        tukar[ids[0]], tukar[ids[1]] = kunci[ids[1]], kunci[ids[0]]
        return [{"penempatan": kunci}, {"penempatan": tukar}, {"penempatan": {ids[0]: kunci[ids[0]]}}, {}]
    return []


def main() -> None:
    kasus = []
    langkah_semua = [lk for m in bank_soal.semua_misi() for lk in m["langkah"]]
    langkah_semua += bank_soal.latihan()["pilah"]
    for lk in langkah_semua:
        for j in variasi(lk):
            h = periksa_langkah(lk, j)
            kasus.append({"langkah": lk, "jawaban": j, "hasil": [h.benar, h.kode, h.umpan_balik]})

    skor = []
    for m in bank_soal.semua_misi():
        for i, _ in enumerate(m["langkah"]):
            st = {lk["no"]: StatusLangkah(True, 0) for lk in m["langkah"]}
            no = m["langkah"][i]["no"]
            st[no] = StatusLangkah(True, 3)
            if i + 1 < len(m["langkah"]):
                st[m["langkah"][i + 1]["no"]] = StatusLangkah(True, 2)
            s = hitung_skor_misi(m, st)
            skor.append(
                {
                    "misi_id": m["id"],
                    "status": {k: {"benar": v.benar, "tingkat": v.tingkat_petunjuk} for k, v in st.items()},
                    "hasil": [s.skor, s.maks, s.bintang, s.total_petunjuk, s.rincian],
                }
            )

    angka = [[t, parse_angka(t)] for t in TEKS_ANGKA]
    satuan = [[t, parse_satuan(t)] for t in SATUAN]
    tinggi = []
    for seed in range(1, 300):
        s = buat_soal_tinggi(seed)
        tinggi.append(seed)
        assert sum(1 for k in s["kandidat"] if k["peran"] == "tinggi") == 1

    json.dump(
        {"kasus": kasus, "skor": skor, "angka": angka, "satuan": satuan, "misi": list(bank_soal.semua_misi()), "seed": tinggi},
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
