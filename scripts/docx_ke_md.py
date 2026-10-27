#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docx_ke_md.py - Mengubah draf Word (.docx) menjadi teks Markdown supaya bisa dibaca
agent AI (agent tidak bisa membaca file .docx biner secara langsung).

Contoh:
    python scripts/docx_ke_md.py draft/proposal.docx
    -> output/teks/proposal.md

Catatan:
  - Terima dulu semua perubahan (Review → Accept All Changes) bila memakai Track Changes;
    teks hasil revisi yang belum diterima tidak ikut terbaca.
  - Judul dikenali dari style Heading ATAU pola penomoran ("BAB 1 ...", "1.1 ...").
  - Gambar diganti penanda [GAMBAR]; tabel jadi tabel Markdown.
  - Hasilnya bisa diubah balik jadi .docx dengan buat_docx.py.
"""
import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.hyperlink import Hyperlink
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from common import (BAB_RE, SUBJUDUL_RE, ensure_output_dir, looks_like_toc_line,
                    normalize, setup_stdout)


def bungkus(t, tebal, miring):
    inti = t.strip()
    if not inti:
        return t
    awal = t[: len(t) - len(t.lstrip())]
    akhir = t[len(t.rstrip()):]
    if tebal:
        inti = f"**{inti}**"
    if miring:
        inti = f"*{inti}*"
    return awal + inti + akhir


def teks_inline(p: Paragraph):
    kelompok = []  # [(tebal, miring, teks)]
    for item in p.iter_inner_content():
        if isinstance(item, Run):
            t, b, i = item.text, bool(item.bold), bool(item.italic)
        elif isinstance(item, Hyperlink):
            t, b, i = item.text, False, False
        else:
            continue
        if not t:
            continue
        if kelompok and kelompok[-1][0] == b and kelompok[-1][1] == i:
            kelompok[-1][2] += t
        else:
            kelompok.append([b, i, t])
    return "".join(bungkus(t, b, i) for b, i, t in kelompok).strip()


def seluruhnya_tebal(p: Paragraph):
    runs = [r for r in p.runs if r.text.strip()]
    if not runs:
        return False
    return all(bool(r.bold) for r in runs) or (p.style is not None and bool(p.style.font.bold))


def tingkat_judul(p: Paragraph, teks_polos: str):
    sn = (p.style.name if p.style is not None else "") or ""
    m = re.match(r"^heading\s*(\d)", sn, re.IGNORECASE)
    if m:
        return min(int(m.group(1)), 4)
    t = teks_polos.strip()
    if len(t) > 120:
        return None
    if BAB_RE.match(t):
        return 1
    n = normalize(t)
    if n in ("daftar pustaka", "lampiran") or re.match(r"^lampiran\s+\d+", n):
        return 1
    mm = SUBJUDUL_RE.match(t)
    if mm and not t.endswith((".", ",", ";")) and seluruhnya_tebal(p):
        return min(mm.group(1).count(".") + 1, 4)
    return None


def tabel_ke_md(t: Table):
    baris = []
    for r in t.rows:
        sel = []
        for c in r.cells:
            sel.append(re.sub(r"\s+", " ", c.text).replace("|", "/").strip())
        baris.append("| " + " | ".join(sel) + " |")
    if not baris:
        return []
    ncol = len(t.rows[0].cells)
    baris.insert(1, "|" + "|".join(["---"] * ncol) + "|")
    return baris


def konversi(path: Path):
    doc = Document(str(path))
    out = []
    for blok in doc.iter_inner_content():
        if isinstance(blok, Table):
            out.append("")
            out.extend(tabel_ke_md(blok))
            out.append("")
            continue
        p = blok
        sn = (p.style.name if p.style is not None else "") or ""
        polos = p.text.strip()
        if p._p.xpath(".//w:drawing | .//w:pict"):
            out.append("")
            out.append("[GAMBAR]")
            out.append("")
            if not polos:
                continue
        if not polos:
            if out and out[-1] != "":
                out.append("")
            continue
        if looks_like_toc_line(p.text, sn):
            continue
        lvl = tingkat_judul(p, polos)
        if lvl:
            out.append("")
            out.append("#" * lvl + " " + polos)
            out.append("")
            continue
        md = teks_inline(p).replace("\t", " ")
        adalah_butir = bool(p._p.xpath("./w:pPr/w:numPr")) or sn.lower().startswith("list bullet")
        if adalah_butir and not re.match(r"^(\d+[.)]|[a-z][.)])\s", polos):
            out.append("- " + md)
        else:
            out.append(md)
            out.append("")
    # rapikan baris kosong berlebih
    teks = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
    return teks


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description="Konversi .docx → Markdown agar terbaca agent.")
    ap.add_argument("berkas")
    ap.add_argument("--keluar", help="path .md keluaran (default: output/teks/<nama>.md)")
    a = ap.parse_args()
    path = Path(a.berkas)
    if not path.exists() or path.suffix.lower() != ".docx":
        print("Beri path file .docx yang valid.")
        sys.exit(2)
    teks = konversi(path)
    out = Path(a.keluar) if a.keluar else ensure_output_dir() / "teks" / f"{path.stem}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(teks, encoding="utf-8")
    kata = len(teks.split())
    print(f"✅ Teks dibaca: {out} (±{kata} kata)")


if __name__ == "__main__":
    main()
