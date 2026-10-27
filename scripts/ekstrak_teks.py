#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ekstrak_teks.py - Mengubah PDF / DOCX menjadi teks Markdown supaya bisa dibaca agent AI
(agent tidak bisa membaca file PDF/DOCX biner secara langsung).

Contoh:
    python scripts/ekstrak_teks.py dokumen-kampus/                 # semua PDF/DOCX di folder
    python scripts/ekstrak_teks.py referensi/pdf/jurnal-a.pdf      # satu berkas
    python scripts/ekstrak_teks.py referensi/pdf/ --paksa          # ekstrak ulang

Lokasi hasil:
    referensi/pdf/x.pdf        -> referensi/teks/x.md
    dokumen-kampus/y.pdf/.docx -> dokumen-kampus/teks/y.md
    (lainnya)                  -> <folder berkas>/teks/<nama>.md

Teks PDF diberi penanda <!-- halaman N --> agar bisa dirujuk. PDF hasil scan (berupa gambar)
tidak punya teks; perlu OCR terlebih dulu.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from common import ROOT, setup_stdout

DIDUKUNG = {".pdf", ".docx"}


def tujuan(path: Path) -> Path:
    if path.parent.name.lower() == "pdf" and path.parent.parent.name.lower() == "referensi":
        return ROOT / "referensi" / "teks" / f"{path.stem}.md"
    return path.parent / "teks" / f"{path.stem}.md"


def pdf_ke_teks(path: Path):
    """Kembalikan (teks, jumlah_halaman). Coba pypdf, lalu pdftotext."""
    halaman = []
    try:
        from pypdf import PdfReader
        r = PdfReader(str(path))
        for i, pg in enumerate(r.pages, start=1):
            t = pg.extract_text() or ""
            halaman.append(t)
    except ImportError:
        exe = shutil.which("pdftotext")
        if not exe:
            raise RuntimeError("Paket pypdf belum terpasang. Jalankan: pip install -r requirements.txt")
        out = subprocess.run([exe, "-layout", str(path), "-"], capture_output=True, check=True)
        halaman = out.stdout.decode("utf-8", errors="replace").split("\f")
        if halaman and not halaman[-1].strip():
            halaman.pop()
    bagian = []
    for i, t in enumerate(halaman, start=1):
        t = re.sub(r"[ \t]+\n", "\n", t)
        t = re.sub(r"\n{3,}", "\n\n", t).strip()
        bagian.append(f"<!-- halaman {i} -->\n{t}")
    return "\n\n".join(bagian) + "\n", len(halaman)


def docx_ke_teks(path: Path):
    from docx_ke_md import konversi
    return konversi(path), None


def proses(path: Path, paksa: bool):
    out = tujuan(path)
    if out.exists() and not paksa and out.stat().st_mtime >= path.stat().st_mtime:
        print(f"⏭️  lewati (sudah terbaru): {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
        return True
    try:
        if path.suffix.lower() == ".pdf":
            teks, n = pdf_ke_teks(path)
        else:
            teks, n = docx_ke_teks(path)
    except Exception as e:  # noqa: BLE001
        print(f"❌ gagal: {path.name}: {e}")
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(teks, encoding="utf-8")
    kata = len(teks.split())
    info = f"{n} halaman, " if n else ""
    peringatan = ""
    if path.suffix.lower() == ".pdf" and n and kata < 40 * n:
        peringatan = "  ⚠️ teks sangat sedikit: kemungkinan PDF hasil scan (butuh OCR)"
    rel = out.relative_to(ROOT) if out.is_relative_to(ROOT) else out
    print(f"✅ {path.name} → {rel} ({info}±{kata} kata){peringatan}")
    return True


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description="Ekstrak teks PDF/DOCX → Markdown agar terbaca agent.")
    ap.add_argument("sumber", help="berkas .pdf/.docx atau folder yang berisi berkas tsb")
    ap.add_argument("--paksa", action="store_true", help="ekstrak ulang walau hasilnya sudah ada")
    a = ap.parse_args()
    p = Path(a.sumber)
    if not p.exists():
        print(f"Tidak ditemukan: {p}")
        sys.exit(2)
    berkas = [p] if p.is_file() else sorted(f for f in p.iterdir()
                                          if f.is_file() and f.suffix.lower() in DIDUKUNG
                                          and not f.name.startswith(("~$", "_")))
    if not berkas:
        print("Tidak ada berkas .pdf/.docx di sana.")
        sys.exit(0)
    for f in berkas:
        if f.suffix.lower() not in DIDUKUNG:
            print(f"⏭️  format tidak didukung: {f.name}")
            continue
        proses(f, a.paksa)


if __name__ == "__main__":
    main()
