#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buat_daftar_sumber.py - Membaca semua catatan di referensi/catatan/*.md, lalu membuat
  1) referensi/daftar-sumber.md  : indeks semua sumber + progres menuju target pedoman
  2) draf Daftar Pustaka (APA) dari sumber yang SUDAH terverifikasi (opsional, --pustaka)

Contoh:
    python scripts/buat_daftar_sumber.py
    python scripts/buat_daftar_sumber.py --pustaka        # juga tulis output/daftar-pustaka-draf.md

Catatan memakai frontmatter sederhana (lihat referensi/catatan/_TEMPLATE.md):
    ---
    id: penulis-2024
    apa: "Penulis, A. A. (2024). Judul. *Jurnal*, 5(1), 1-10."
    jenis: jurnal            # jurnal | prosiding | buku | skripsi | web | lainnya
    tahun: 2024
    tautan: https://doi.org/...
    status: terverifikasi    # terverifikasi | belum-diverifikasi
    asal: dari-saya          # dari-saya | rekomendasi-agent
    dipakai_di: bab 2.1, bab 2.2
    ---
Berkas yang namanya diawali "_" diabaikan (mis. _TEMPLATE.md).
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import config
from common import ROOT, ensure_output_dir, setup_stdout

CATATAN = ROOT / "referensi" / "catatan"
INDEKS = ROOT / "referensi" / "daftar-sumber.md"


def baca_frontmatter(path: Path):
    teks = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^\ufeff?---\s*\n(.*?)\n---\s*(?:\n|$)", teks, re.DOTALL)
    data = {}
    if not m:
        return data, teks
    for baris in m.group(1).splitlines():
        if ":" not in baris or baris.lstrip().startswith("#"):
            continue
        k, v = baris.split(":", 1)
        v = re.sub(r"\s+#\s.*$", "", v).strip()      # buang komentar di akhir baris
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        data[k.strip().lower()] = v
    return data, teks[m.end():]


def sudah_diringkas(isi: str) -> bool:
    """Catatan dianggap sudah berisi ringkasan bila ada teks nyata selain placeholder [ ... ]."""
    t = re.sub(r"^#+.*$", "", isi, flags=re.MULTILINE)
    t = re.sub(r"\[[^\]]*\]", "", t)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.DOTALL)
    return len(t.split()) >= 25


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description="Buat indeks sumber dari referensi/catatan/*.md")
    ap.add_argument("--pustaka", action="store_true",
                    help="juga tulis draf Daftar Pustaka APA (hanya sumber terverifikasi)")
    ap.add_argument("--tahun-sekarang", type=int, default=datetime.now().year)
    a = ap.parse_args()

    CATATAN.mkdir(parents=True, exist_ok=True)
    berkas = sorted(p for p in CATATAN.glob("*.md") if not p.name.startswith("_"))
    R = config.REFERENSI
    rows, peringatan = [], []
    for p in berkas:
        d, isi = baca_frontmatter(p)
        if not d:
            peringatan.append(f"{p.name}: frontmatter (--- … ---) tidak ditemukan")
            continue
        try:
            tahun = int(re.search(r"\d{4}", d.get("tahun", "") or d.get("apa", "")).group(0))
        except Exception:  # noqa: BLE001
            tahun = None
            peringatan.append(f"{p.name}: tahun tidak terbaca")
        rows.append({
            "file": p.name,
            "id": d.get("id") or p.stem,
            "apa": d.get("apa", ""),
            "jenis": (d.get("jenis") or "lainnya").lower(),
            "tahun": tahun,
            "tautan": d.get("tautan", ""),
            "status": (d.get("status") or "belum-diverifikasi").lower(),
            "asal": (d.get("asal") or "dari-saya").lower(),
            "dipakai": d.get("dipakai_di", ""),
            "diringkas": sudah_diringkas(isi),
        })
        if not d.get("apa"):
            peringatan.append(f"{p.name}: kolom 'apa' (sitasi APA) kosong")
        if not d.get("tautan"):
            peringatan.append(f"{p.name}: tautan/DOI kosong")

    n = len(rows)
    ver = [r for r in rows if r["status"] == "terverifikasi"]
    ilmiah = [r for r in ver if r["jenis"] in ("jurnal", "prosiding")]
    jurnal = [r for r in ver if r["jenis"] == "jurnal"]
    baru = [r for r in ver if r["tahun"] and a.tahun_sekarang - r["tahun"] <= R["tahun_batas"]]

    def persen(x, y):
        return f"{100.0 * x / y:.0f}%" if y else "-"

    L = [
        "# Daftar Sumber",
        "",
        "> Dibuat otomatis oleh `python scripts/buat_daftar_sumber.py`. **Jangan diedit manual**; ubah catatan di `referensi/catatan/` lalu jalankan ulang.",
        "",
        f"Tanggal: {datetime.now():%Y-%m-%d} | Total catatan: {n} | Terverifikasi: {len(ver)} | Belum diverifikasi: {n - len(ver)}",
        "",
        "## Progres menuju target pedoman (hanya sumber terverifikasi)",
        "",
        "| Aspek | Sekarang | Target | Rujukan |",
        "|---|---|---|---|",
        f"| Jumlah referensi | {len(ver)} | ≥ {R['min_total']} (saran {R['min_total']}–{R['saran_max_total']}) | Bab 3.3 |",
        f"| Jurnal/prosiding | {len(ilmiah)} ({persen(len(ilmiah), len(ver))}) | ≥ {R['min_pct_jurnal_prosiding']}% | Bab 3.3 |",
        f"| Sumber jurnal | {len(jurnal)} | ≥ {R['min_jurnal']} | Bab 1.4 |",
        f"| Terbit ≤ {R['tahun_batas']} tahun | {len(baru)} ({persen(len(baru), len(ver))}) | ≥ {R['min_pct_terbaru']}% | Bab 3.3 |",
        "",
        "## Indeks sumber",
        "",
    ]
    if not rows:
        L.append("_Belum ada catatan. Salin `catatan/_TEMPLATE.md` atau jalankan prompt `/tambah-sumber`._")
    else:
        L += ["| ID | Sitasi (APA) | Jenis | Tahun | Status | Asal | Diringkas | Dipakai di | Tautan |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda x: x["apa"].lower()):
            st = "✅ terverifikasi" if r["status"] == "terverifikasi" else "⚠️ belum diverifikasi"
            L.append("| " + " | ".join([
                f"[{r['id']}](catatan/{r['file']})", r["apa"].replace("|", "/")[:110] or "-", r["jenis"],
                str(r["tahun"] or "?"), st, r["asal"], "ya" if r["diringkas"] else "belum",
                r["dipakai"] or "-", (f"[tautan]({r['tautan']})" if r["tautan"].startswith("http") else (r["tautan"] or "-")),
            ]) + " |")
    if peringatan:
        L += ["", "## Perlu dilengkapi", ""] + [f"- {w}" for w in peringatan]
    INDEKS.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"✅ {INDEKS.relative_to(ROOT)}: {n} catatan ({len(ver)} terverifikasi)")
    print(f"   Target: {len(ver)}/{R['min_total']} referensi, {len(jurnal)}/{R['min_jurnal']} jurnal, "
          f"{len(ilmiah)} jurnal/prosiding, {len(baru)} terbit ≤ {R['tahun_batas']} th")
    for w in peringatan[:8]:
        print(f"   ⚠️ {w}")

    if a.pustaka:
        urut = sorted(ver, key=lambda x: re.sub(r"[^a-z0-9 ]", "", x["apa"].lower()))
        out = ensure_output_dir() / "daftar-pustaka-draf.md"
        isi = ["# DAFTAR PUSTAKA", "",
               "<!-- Draf otomatis dari referensi/catatan (hanya yang terverifikasi), urut A–Z. "
               "Periksa kembali tanda baca APA sebelum dipakai. -->", ""]
        for r in urut:
            if r["apa"]:
                isi += [r["apa"], ""]
        out.write_text("\n".join(isi), encoding="utf-8")
        print(f"✅ Draf Daftar Pustaka: {out.relative_to(ROOT)} ({len(urut)} entri)")


if __name__ == "__main__":
    main()
