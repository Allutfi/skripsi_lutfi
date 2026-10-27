#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cek_referensi.py - Memeriksa kecukupan daftar pustaka terhadap pedoman TA
FTI ITB Widya Gama Lumajang 2026-2027 (Bab 1.4, 3.3, 5.1.G, 5.1.H).

Contoh:
    python scripts/cek_referensi.py draft/proposal.docx
    python scripts/cek_referensi.py draft/proposal.md --tahun-sekarang 2026

Yang diperiksa:
  - jumlah referensi (min. 15; saran 15-20)
  - persentase jurnal/prosiding (min. 60%) dan jumlah jurnal (min. 10)
  - persentase terbit <= 10 tahun terakhir (min. 80%)
  - urutan abjad daftar pustaka
  - kutipan di teks yang tidak ada di daftar pustaka, dan sebaliknya

PENTING: klasifikasi jenis sumber dan pencocokan kutipan bersifat HEURISTIK
(berdasarkan kata kunci dan pola APA). Hasilnya petunjuk, bukan keputusan akhir.
Verifikasi tiap sumber secara manual.
"""
import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import config
from common import (ensure_output_dir, normalize, read_plain_lines,
                    setup_stdout, today_str)

YEAR = r"(?:19|20)\d{2}[a-z]?"
PAREN = re.compile(r"\(([^()]*?" + YEAR + r"[^()]*?)\)")
NARASI = re.compile(r"([A-Z][\w'’\-]+)(?:\s+(?:dan|&|and)\s+[A-Z][\w'’\-]+|\s+et\s+al\.?)?\s*\(\s*(" + YEAR + r")")


def baca_paragraf(path: Path):
    if path.suffix.lower() == ".docx":
        from docx import Document
        doc = Document(str(path))
        return [p.text for p in doc.paragraphs]
    return read_plain_lines(path)


def bersihkan_md(t: str) -> str:
    t = re.sub(r"^\s*(?:[-*]|\d+[.)])\s+", "", t)
    t = t.replace("**", "").replace("`", "")
    t = re.sub(r"(?<!\w)[*_](.+?)[*_](?!\w)", r"\1", t)
    return t.strip()


def pisah_bagian(paragraf):
    """Kembalikan (teks_isi, entri_pustaka)."""
    idx = None
    for i, t in enumerate(paragraf):
        n = normalize(re.sub(r"^#+\s*", "", t))
        if n in ("daftar pustaka", "daftar referensi", "references") or \
                (len(n) < 30 and n.startswith("daftar pustaka")):
            idx = i  # ambil kemunculan TERAKHIR (menghindari daftar isi)
    if idx is None:
        return None, None
    isi = [t for t in paragraf[:idx]]
    entri = []
    for t in paragraf[idx + 1:]:
        n = normalize(re.sub(r"^#+\s*", "", t))
        if n.startswith("lampiran") and len(n) < 40:
            break
        t2 = bersihkan_md(t)
        if len(t2) >= 25:
            entri.append(t2)
    return isi, entri


def parse_entri(e: str, tahun_skrg: int):
    m = re.search(r"\(\s*((?:19|20)\d{2})([a-z]?)\s*[,)\s]", e) or re.search(r"\b((?:19|20)\d{2})\b", e)
    tahun = int(m.group(1)) if m else None
    low = e.lower()
    head = low[:100]
    if re.search(r"skripsi|tesis|thesis|disertasi|dissertation|tugas akhir", low):
        jenis = "skripsi/tesis"
    elif re.search(r"prosiding|proceeding|proc\.|conference|konferensi|symposium|simposium|"
                   r"seminar nasional|workshop|\bsnati\b|\bsemnas", low):
        jenis = "prosiding"
    elif re.search(r"jurnal|journal|transactions|\bletters\b|ieee access|\bvol\.|"
                   r"\b\d{1,4}\s*\(\s*\d{1,3}\s*\)\s*[,:]\s*\d", low):
        jenis = "jurnal"
    elif re.search(r"diperoleh|retrieved|accessed|https?://|www\.", low) and not re.search(r"doi", low):
        jenis = "web"
    else:
        jenis = "buku/lainnya"
    return {
        "teks": e,
        "tahun": tahun,
        "jenis": jenis,
        "head": head,
        "terbaru": (tahun is not None and tahun_skrg - tahun <= config.REFERENSI["tahun_batas"]),
        "sangat_baru": (tahun is not None and tahun_skrg - tahun <= config.REFERENSI["tahun_preferensi"]),
    }


def kutipan_di_teks(isi):
    teks = "\n".join(isi)
    kunci = set()
    for m in NARASI.finditer(teks):
        kunci.add((m.group(1).lower(), m.group(2)[:4]))
    for m in PAREN.finditer(teks):
        for bagian in m.group(1).split(";"):
            mm = re.search(r"([A-Z][\w'’\-]+)[^()]*?,?\s*(" + YEAR + r")", bagian)
            if mm:
                kunci.add((mm.group(1).lower(), mm.group(2)[:4]))
    return kunci


def cocok(kunci, ref):
    sn, th = kunci
    return ref["tahun"] is not None and str(ref["tahun"]) == th and sn in ref["head"]


def urutan_abjad(entri):
    kunci = [re.sub(r"[^a-z0-9 ]", "", normalize(e["teks"]))[:40] for e in entri]
    salah = []
    for i in range(1, len(kunci)):
        if kunci[i] < kunci[i - 1]:
            salah.append(f"#{i} “{entri[i]['teks'][:35]}…” muncul setelah “{entri[i - 1]['teks'][:35]}…”")
    return salah


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description="Cek kecukupan daftar pustaka (heuristik).")
    ap.add_argument("berkas", help="file .docx / .md / .txt yang memuat Daftar Pustaka")
    ap.add_argument("--tahun-sekarang", type=int, default=datetime.now().year)
    ap.add_argument("--keluar", help="path laporan .md")
    a = ap.parse_args()

    path = Path(a.berkas)
    if not path.exists():
        print(f"Berkas tidak ditemukan: {path}")
        sys.exit(2)
    paragraf = baca_paragraf(path)
    isi, entri_teks = pisah_bagian(paragraf)
    if entri_teks is None:
        print("Judul 'DAFTAR PUSTAKA' tidak ditemukan di berkas. Tambahkan judulnya, lalu jalankan lagi.")
        sys.exit(2)
    if not entri_teks:
        print("Daftar Pustaka kosong.")
        sys.exit(2)

    R = config.REFERENSI
    entri = [parse_entri(e, a.tahun_sekarang) for e in entri_teks]
    n = len(entri)
    jenis = Counter(e["jenis"] for e in entri)
    n_jurnal = jenis["jurnal"]
    n_ilmiah = jenis["jurnal"] + jenis["prosiding"]
    pct_ilmiah = 100.0 * n_ilmiah / n
    n_terbaru = sum(1 for e in entri if e["terbaru"])
    pct_terbaru = 100.0 * n_terbaru / n
    n_5 = sum(1 for e in entri if e["sangat_baru"])
    tanpa_tahun = [e for e in entri if e["tahun"] is None]

    baris_cek = []

    def cek(ok, nama, nilai, target, rujukan):
        baris_cek.append(("✅" if ok else "❌", nama, nilai, target, rujukan))

    cek(n >= R["min_total"], "Jumlah referensi", f"{n}",
        f"≥ {R['min_total']} (saran {R['min_total']}–{R['saran_max_total']})", "Bab 3.3")
    cek(pct_ilmiah >= R["min_pct_jurnal_prosiding"], "Jurnal/prosiding",
        f"{n_ilmiah} dari {n} ({pct_ilmiah:.0f}%)", f"≥ {R['min_pct_jurnal_prosiding']}%", "Bab 3.3")
    cek(n_jurnal >= R["min_jurnal"], "Jumlah sumber jurnal", f"{n_jurnal}",
        f"≥ {R['min_jurnal']}", "Bab 1.4")
    cek(pct_terbaru >= R["min_pct_terbaru"], f"Terbit ≤ {R['tahun_batas']} tahun terakhir",
        f"{n_terbaru} dari {n} ({pct_terbaru:.0f}%)", f"≥ {R['min_pct_terbaru']}%", "Bab 3.3 / 5.1.G")

    urut_salah = urutan_abjad(entri)

    # kutipan di teks <-> daftar pustaka
    kunci = kutipan_di_teks(isi) if isi else set()
    tanpa_pustaka = sorted(k for k in kunci if not any(cocok(k, e) for e in entri))
    tak_dikutip = [e for e in entri
                   if not any(cocok(k, e) for k in kunci)]

    L = [
        "# Laporan Cek Referensi (heuristik)",
        "",
        f"- Berkas: `{path.as_posix()}`",
        f"- Tanggal: {today_str()} (tahun acuan: {a.tahun_sekarang})",
        "- Catatan: klasifikasi jenis sumber dan pencocokan kutipan memakai kata kunci/pola APA. "
        "Verifikasi manual tetap wajib.",
        "",
        "## Ringkasan kecukupan",
        "",
        "| Status | Aspek | Nilai | Target | Rujukan |",
        "|---|---|---|---|---|",
    ]
    for r in baris_cek:
        L.append("| " + " | ".join(r) + " |")
    L += [
        "",
        f"Terbit ≤ {R['tahun_preferensi']} tahun terakhir: {n_5} dari {n} ({100.0 * n_5 / n:.0f}%) "
        "(Bab 1.4 menyebut 5–10 tahun terakhir; makin baru makin aman).",
        "",
        "Komposisi jenis: " + ", ".join(f"{k} {v}" for k, v in jenis.most_common()),
        "",
    ]
    if tanpa_tahun:
        L += ["## Entri tanpa tahun terdeteksi", ""] + [f"- {e['teks'][:90]}…" for e in tanpa_tahun] + [""]
    L += ["## Urutan abjad (Bab 5.1.H.c)", ""]
    L += (["- ⚠️ " + s for s in urut_salah] if urut_salah else ["- ✅ Urutan A–Z tampak benar."])
    L += ["", "## Kutipan di teks tanpa entri daftar pustaka (heuristik)", ""]
    if not isi:
        L.append("- (tidak ada teks isi untuk diperiksa)")
    elif tanpa_pustaka:
        L += [f"- ⚠️ {sn.title()} ({th})" for sn, th in tanpa_pustaka[:30]]
        L.append("- Bisa berupa salah deteksi (mis. nama produk + tahun). Cek satu per satu.")
    else:
        L.append("- ✅ Tidak ada temuan.")
    L += ["", "## Entri daftar pustaka yang tidak terdeteksi dikutip di teks (heuristik)", ""]
    if not isi:
        L.append("- (tidak ada teks isi untuk diperiksa)")
    elif tak_dikutip:
        L += [f"- ⚠️ {e['teks'][:90]}…" for e in tak_dikutip[:30]]
        L.append("- Pedoman: setiap sumber yang dikutip harus ada di daftar pustaka, dan sebaliknya "
                 "sebaiknya setiap entri benar-benar dikutip.")
    else:
        L.append("- ✅ Semua entri terdeteksi dikutip.")
    L += ["", "## Rincian per entri", "", "| No | Tahun | Jenis | ≤10 th | Entri |", "|---|---|---|---|---|"]
    for i, e in enumerate(entri, 1):
        L.append(f"| {i} | {e['tahun'] or '?'} | {e['jenis']} | {'ya' if e['terbaru'] else 'tidak'} | "
                 f"{e['teks'][:80].replace('|', '/')}… |")

    out = Path(a.keluar) if a.keluar else ensure_output_dir() / f"laporan-referensi-{path.stem}-{today_str()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"Cek referensi: {n} entri")
    for r in baris_cek:
        print(f"  {r[0]} {r[1]}: {r[2]} (target {r[3]})")
    if urut_salah:
        print(f"  ⚠️ {len(urut_salah)} entri tidak urut abjad")
    if tanpa_pustaka:
        print(f"  ⚠️ {len(tanpa_pustaka)} kutipan di teks tidak ditemukan di daftar pustaka (heuristik)")
    print(f"Laporan lengkap: {out}")


if __name__ == "__main__":
    main()
