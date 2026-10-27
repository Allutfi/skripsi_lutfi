# -*- coding: utf-8 -*-
"""Fungsi bantu yang dipakai bersama oleh semua skrip."""
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"

ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6}
BAB_RE = re.compile(r"^\s*bab\s+(\d+|[ivx]+)\b", re.IGNORECASE)
SUBJUDUL_RE = re.compile(r"^\s*(\d+(?:\.\d+)+)\.?\s+\S")


def setup_stdout():
    """Supaya karakter Indonesia/emoji aman dicetak di konsol Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\u00a0", " ")).strip().lower()


def strip_numbering(text: str) -> str:
    """Buang 'BAB 1', 'BAB I', '1.1', '1.1.1' di awal judul."""
    t = normalize(text)
    t = re.sub(r"^bab\s+(\d+|[ivx]+)\b[\s.:\-\u2013\u2014]*", "", t)
    t = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", t)
    return t.strip()


def bab_number(text: str):
    m = BAB_RE.match(text or "")
    if not m:
        return None
    v = m.group(1).lower()
    return int(v) if v.isdigit() else ROMAN.get(v)


def looks_like_toc_line(text: str, style_name: str = "") -> bool:
    """Baris daftar isi: ada titik-titik, atau diakhiri tab + nomor halaman."""
    if (style_name or "").lower().startswith("toc"):
        return True
    if re.search(r"\.{4,}", text or ""):
        return True
    if re.search(r"\t\s*\d+\s*$", text or ""):
        return True
    return False


def today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def read_plain_lines(path: Path):
    """Baca .md / .txt sebagai daftar baris."""
    return path.read_text(encoding="utf-8", errors="replace").splitlines()
