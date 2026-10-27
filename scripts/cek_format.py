#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cek_format.py - Memeriksa format dokumen Word (.docx) terhadap Buku Pedoman TA
FTI ITB Widya Gama Lumajang 2026-2027.

Contoh:
    python scripts/cek_format.py draft/proposal.docx
    python scripts/cek_format.py draft/proposal.docx --tahap laporan

Hasil: laporan Markdown di folder output/ + ringkasan di layar.

Yang DIPERIKSA : ukuran kertas, margin, font, ukuran font, spasi baris, indentasi
                 paragraf, format judul bab/subbab, struktur judul wajib, rujukan
                 "tabel/gambar di atas/bawah", kata tidak baku, garis vertikal tabel,
                 posisi judul tabel/gambar, keberadaan nomor halaman, estimasi halaman.
Yang TIDAK bisa: halaman sebenarnya per bab, cetak miring istilah asing, warna sampul,
                 kualitas isi. Itu dicek manual / oleh agent.
"""
import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Length
from docx.table import Table
from docx.text.paragraph import Paragraph

import config
from common import (BAB_RE, SUBJUDUL_RE, bab_number, ensure_output_dir,
                    looks_like_toc_line, normalize, setup_stdout,
                    strip_numbering, today_str)

OK, WARN, FAIL, INFO = "OK", "PERINGATAN", "GAGAL", "INFO"
EMOJI = {OK: "✅", WARN: "⚠️", FAIL: "❌", INFO: "ℹ️"}


class Hasil:
    def __init__(self):
        self.items = []

    def add(self, status, aspek, detail, rujukan=""):
        self.items.append((status, aspek, detail, rujukan))

    def hitung(self):
        c = Counter(s for s, *_ in self.items)
        return c


# ---------------------------------------------------------------------------
# Pembaca atribut efektif (mengikuti rantai style Word)
# ---------------------------------------------------------------------------
def _docdefaults(doc):
    out = {"font": None, "size": None, "spasi": 1.0}
    dd = doc.styles.element.find(qn("w:docDefaults"))
    if dd is None:
        return out
    rpr_d = dd.find(qn("w:rPrDefault"))
    if rpr_d is not None:
        rpr = rpr_d.find(qn("w:rPr"))
        if rpr is not None:
            rf = rpr.find(qn("w:rFonts"))
            if rf is not None:
                out["font"] = rf.get(qn("w:ascii"))
            sz = rpr.find(qn("w:sz"))
            if sz is not None and sz.get(qn("w:val")):
                out["size"] = int(sz.get(qn("w:val"))) / 2.0
    ppr_d = dd.find(qn("w:pPrDefault"))
    if ppr_d is not None:
        ppr = ppr_d.find(qn("w:pPr"))
        if ppr is not None:
            sp = ppr.find(qn("w:spacing"))
            if sp is not None and sp.get(qn("w:line")) and sp.get(qn("w:lineRule"), "auto") == "auto":
                out["spasi"] = int(sp.get(qn("w:line"))) / 240.0
    return out


def eff_font_name(run, para, dd):
    if run.font.name:
        return run.font.name
    try:
        if run.style is not None and run.style.font.name:
            return run.style.font.name
    except Exception:
        pass
    st = para.style
    while st is not None:
        if st.font.name:
            return st.font.name
        st = st.base_style
    return dd["font"]  # bisa None bila mengikuti tema


def eff_font_size(run, para, dd):
    if run.font.size:
        return run.font.size.pt
    try:
        if run.style is not None and run.style.font.size:
            return run.style.font.size.pt
    except Exception:
        pass
    st = para.style
    while st is not None:
        if st.font.size:
            return st.font.size.pt
        st = st.base_style
    return dd["size"]


def eff_bold(run, para):
    if run.bold is not None:
        return bool(run.bold)
    try:
        if run.style is not None and run.style.font.bold is not None:
            return bool(run.style.font.bold)
    except Exception:
        pass
    st = para.style
    while st is not None:
        if st.font.bold is not None:
            return bool(st.font.bold)
        st = st.base_style
    return False


def eff_alignment(para):
    if para.alignment is not None:
        return para.alignment
    st = para.style
    while st is not None:
        if st.paragraph_format.alignment is not None:
            return st.paragraph_format.alignment
        st = st.base_style
    return None


def eff_line_spacing(para, dd):
    """Kembalikan (nilai, jenis). jenis = 'kelipatan' atau 'pasti'."""
    val = para.paragraph_format.line_spacing
    st = para.style
    while val is None and st is not None:
        val = st.paragraph_format.line_spacing
        st = st.base_style
    if val is None:
        return dd["spasi"], "kelipatan"
    if isinstance(val, Length):
        return val.pt, "pasti"
    return float(val), "kelipatan"


def eff_first_indent_cm(para):
    val = para.paragraph_format.first_line_indent
    st = para.style
    while val is None and st is not None:
        val = st.paragraph_format.first_line_indent
        st = st.base_style
    return (val.cm if val is not None else 0.0)


def is_caption(text):
    return bool(re.match(r"^\s*(tabel|gambar)\s+\d+([.\-]\d+)?", text, re.IGNORECASE))


def snippet(text, n=60):
    t = re.sub(r"\s+", " ", text).strip()
    return (t[:n] + "…") if len(t) > n else t


# ---------------------------------------------------------------------------
# Pemeriksaan
# ---------------------------------------------------------------------------
def cek_halaman_dan_margin(doc, cfg, hasil):
    F = config.FORMAT
    tol = config.TOL_CM
    n = len(doc.sections)
    salah_kertas, salah_margin = [], []
    for i, s in enumerate(doc.sections, start=1):
        w, h = s.page_width.cm, s.page_height.cm
        if abs(w - F["page_width_cm"]) > tol or abs(h - F["page_height_cm"]) > tol:
            salah_kertas.append(f"seksi {i}: {w:.1f} × {h:.1f} cm")
        marg = {
            "atas": (s.top_margin.cm, F["margin_top_cm"]),
            "kiri": (s.left_margin.cm, F["margin_left_cm"]),
            "kanan": (s.right_margin.cm, F["margin_right_cm"]),
            "bawah": (s.bottom_margin.cm, F["margin_bottom_cm"]),
        }
        salah = [f"{k} {a:.2f} cm (harus {b:.0f})" for k, (a, b) in marg.items() if abs(a - b) > tol]
        if salah:
            salah_margin.append(f"seksi {i}: " + ", ".join(salah))
    if salah_kertas:
        hasil.add(FAIL, "Ukuran kertas", "; ".join(salah_kertas[:4]) + ". Seharusnya A4 (21,0 × 29,7 cm).",
                  "Bab 5.1.A")
    else:
        hasil.add(OK, "Ukuran kertas", f"A4 ({n} seksi).", "Bab 5.1.A")
    if salah_margin:
        hasil.add(FAIL, "Margin", "; ".join(salah_margin[:4]) +
                  ". Aturan: atas 4, kiri 4, kanan 3, bawah 3 cm.", "Bab 5.1.A")
    else:
        hasil.add(OK, "Margin", f"Atas 4, kiri 4, kanan 3, bawah 3 cm ({n} seksi).", "Bab 5.1.A")


def kumpulkan_paragraf(doc):
    """Daftar (Paragraph) tubuh dokumen, di luar tabel, beserta urutan blok."""
    blok = list(doc.iter_inner_content())
    return blok


def cek_font(doc, cfg, hasil, dd):
    F = config.FORMAT
    nama = Counter()
    ukuran = Counter()
    tak_pasti = 0
    total = 0
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        for r in p.runs:
            n = len(r.text.strip())
            if not n:
                continue
            total += n
            fn = eff_font_name(r, p, dd)
            fs = eff_font_size(r, p, dd)
            if fn is None:
                tak_pasti += n
            else:
                nama[fn] += n
            if fs is not None:
                ukuran[fs] += n
    if total == 0:
        hasil.add(WARN, "Font", "Tidak ada teks yang bisa dibaca.", "Bab 5.1.A")
        return
    salah_font = {k: v for k, v in nama.items() if k.lower() != F["font_name"].lower()}
    pct_salah = 100.0 * sum(salah_font.values()) / total
    if pct_salah > 2:
        rinci = ", ".join(f"{k} ({100.0 * v / total:.0f}%)" for k, v in Counter(salah_font).most_common(4))
        hasil.add(FAIL, "Jenis huruf",
                  f"{pct_salah:.0f}% teks bukan {F['font_name']}: {rinci}.", "Bab 5.1.A")
    else:
        extra = ""
        if tak_pasti:
            extra = f" ({100.0 * tak_pasti / total:.0f}% teks mengikuti font tema Word; pastikan juga TNR)"
        hasil.add(OK, "Jenis huruf", f"{F['font_name']}.{extra}", "Bab 5.1.A")
    salah_uk = {k: v for k, v in ukuran.items() if abs(k - F["font_size_pt"]) > 0.01}
    pct_uk = 100.0 * sum(salah_uk.values()) / max(1, sum(ukuran.values()))
    if pct_uk > 5:
        rinci = ", ".join(f"{k:g} pt ({100.0 * v / sum(ukuran.values()):.0f}%)" for k, v in
                          sorted(salah_uk.items(), key=lambda x: -x[1])[:4])
        hasil.add(WARN, "Ukuran huruf",
                  f"{pct_uk:.0f}% teks bukan 12 pt: {rinci}. (Sampul boleh 12–16 pt.)", "Bab 5.1.A")
    else:
        hasil.add(OK, "Ukuran huruf", "12 pt.", "Bab 5.1.A")


def klasifikasi_paragraf(doc):
    """Beri label tiap paragraf: 'bab', 'sub', 'caption', 'toc', 'badan', 'lain', 'pustaka'."""
    hasil = []
    di_pustaka = False
    for p in doc.paragraphs:
        t = p.text.strip()
        sn = p.style.name if p.style is not None else ""
        if not t:
            hasil.append((p, "kosong"))
            continue
        if looks_like_toc_line(p.text, sn):
            hasil.append((p, "toc"))
            continue
        norm = normalize(t)
        if len(t) <= 120 and BAB_RE.match(t):
            di_pustaka = False
            hasil.append((p, "bab"))
            continue
        if len(t) <= 40 and (norm.startswith("daftar pustaka") or norm.startswith("lampiran")):
            di_pustaka = norm.startswith("daftar pustaka")
            hasil.append((p, "bab"))
            continue
        if len(t) <= 120 and SUBJUDUL_RE.match(t) and not t.rstrip().endswith((",", ";")):
            hasil.append((p, "sub"))
            continue
        if sn.lower().startswith("heading") and len(t) <= 120:
            hasil.append((p, "sub"))
            continue
        if is_caption(t):
            hasil.append((p, "caption"))
            continue
        if di_pustaka:
            hasil.append((p, "pustaka"))
            continue
        if sn.lower().startswith(("list", "title", "caption", "header", "footer")):
            hasil.append((p, "lain"))
            continue
        if len(t) >= 80:
            hasil.append((p, "badan"))
        else:
            hasil.append((p, "lain"))
    return hasil


def cek_paragraf_badan(klas, cfg, hasil, dd):
    F = config.FORMAT
    target = cfg["spasi"]
    badan = [p for p, k in klas if k == "badan"]
    if not badan:
        hasil.add(INFO, "Paragraf isi", "Tidak ada paragraf isi panjang yang terdeteksi.", "")
        return
    salah_spasi, salah_indent, tanpa_indent_tab = [], [], 0
    for p in badan:
        val, jenis = eff_line_spacing(p, dd)
        if jenis == "pasti" or abs(val - target) > config.TOL_SPASI:
            salah_spasi.append((p, val, jenis))
        ind = eff_first_indent_cm(p)
        if abs(ind - F["first_line_indent_cm"]) > 0.15:
            if p.text.startswith(("\t", "    ")):
                tanpa_indent_tab += 1
            salah_indent.append((p, ind))
    n = len(badan)
    # Spasi
    if salah_spasi:
        contoh = "; ".join(
            f"“{snippet(p.text, 40)}” → " + (f"{v:.2f}×" if j == "kelipatan" else f"tepat {v:.0f} pt")
            for p, v, j in salah_spasi[:3])
        hasil.add(FAIL if len(salah_spasi) / n > 0.2 else WARN, "Spasi baris",
                  f"{len(salah_spasi)} dari {n} paragraf isi tidak {target:g} spasi. Contoh: {contoh}",
                  "Bab 5.1.A")
    else:
        hasil.add(OK, "Spasi baris", f"Semua {n} paragraf isi {target:g} spasi.", "Bab 5.1.A")
    # Indentasi
    if salah_indent:
        contoh = "; ".join(f"“{snippet(p.text, 40)}” → {v:.2f} cm" for p, v in salah_indent[:3])
        cat = ""
        if tanpa_indent_tab:
            cat = (f" {tanpa_indent_tab} paragraf tampaknya diindentasi dengan Tab/spasi; "
                   "gunakan Paragraph → Special → First line 0,75 cm.")
        hasil.add(FAIL if len(salah_indent) / n > 0.2 else WARN, "Indentasi paragraf",
                  f"{len(salah_indent)} dari {n} paragraf isi tidak berindentasi 0,75 cm. "
                  f"Contoh: {contoh}.{cat}", "Bab 5.1.A")
    else:
        hasil.add(OK, "Indentasi paragraf", f"Semua {n} paragraf isi berindentasi 0,75 cm.", "Bab 5.1.A")


def cek_judul(klas, hasil, dd):
    bab_salah, sub_salah = [], []
    jumlah_bab = jumlah_sub = 0
    for p, k in klas:
        if k not in ("bab", "sub"):
            continue
        t = p.text.strip()
        runs = [r for r in p.runs if r.text.strip()]
        if not runs:
            continue
        bold = sum(len(r.text) for r in runs if eff_bold(r, p)) >= 0.7 * sum(len(r.text) for r in runs)
        al = eff_alignment(p)
        if k == "bab":
            jumlah_bab += 1
            masalah = []
            huruf = re.sub(r"[^A-Za-z]", "", t)
            if huruf and huruf != huruf.upper():
                masalah.append("bukan HURUF KAPITAL")
            if al is None or int(al) != 1:  # 1 = CENTER
                masalah.append("tidak rata tengah")
            if not bold:
                masalah.append("tidak bold")
            if masalah:
                bab_salah.append(f"“{snippet(t, 35)}” ({', '.join(masalah)})")
        else:
            jumlah_sub += 1
            masalah = []
            if not bold:
                masalah.append("tidak bold")
            if al is not None and int(al) in (1, 2):  # CENTER / RIGHT
                masalah.append("tidak rata kiri")
            if t.rstrip().endswith("."):
                masalah.append("diakhiri titik")
            if masalah:
                sub_salah.append(f"“{snippet(t, 35)}” ({', '.join(masalah)})")
    if jumlah_bab == 0:
        hasil.add(WARN, "Judul bab", "Tidak ada judul 'BAB …' yang terdeteksi.", "Bab 5.1.F.11")
    elif bab_salah:
        hasil.add(FAIL, "Judul bab", "; ".join(bab_salah[:5]) +
                  ". Aturan: kapital, rata tengah, bold.", "Bab 5.1.F.11")
    else:
        hasil.add(OK, "Judul bab", f"{jumlah_bab} judul bab: kapital, rata tengah, bold.", "Bab 5.1.F.11")
    if jumlah_sub == 0:
        hasil.add(INFO, "Judul subbab", "Tidak ada subjudul bernomor yang terdeteksi.", "Bab 5.1.F.11")
    elif sub_salah:
        hasil.add(WARN, "Judul subbab", "; ".join(sub_salah[:6]) +
                  ". Aturan: bold, rata kiri, tanpa titik di akhir.", "Bab 5.1.F.11")
    else:
        hasil.add(OK, "Judul subbab", f"{jumlah_sub} subjudul: bold, rata kiri, tanpa titik.",
                  "Bab 5.1.F.11")


def cek_struktur(klas, cfg, hasil):
    kandidat = []
    for p, k in klas:
        if k in ("bab", "sub") or (p.style is not None and p.style.name.lower().startswith("heading")):
            kandidat.append(strip_numbering(p.text))
    # judul bab/pustaka yang lolos dari klasifikasi 'sub' tetap tercakup di atas
    hilang = []
    for item in cfg["judul_wajib"]:
        if not any(any(t.startswith(k) for k in item["kunci"]) for t in kandidat):
            hilang.append(item["tampil"])
    if hilang:
        hasil.add(FAIL if len(hilang) > 3 else WARN, "Struktur judul wajib",
                  f"{len(hilang)} judul belum ditemukan: " + "; ".join(hilang) +
                  ". (Pastikan ditulis sebagai judul tersendiri, bukan di dalam kalimat.)", "Bab 4.1 / 4.2")
    else:
        hasil.add(OK, "Struktur judul wajib",
                  f"Semua {len(cfg['judul_wajib'])} judul wajib {cfg['label']} ada.", "Bab 4.1 / 4.2")
    # bagian awal (INFO)
    semua = [normalize(p.text) for p, k in klas if k != "toc"]
    tak_ada = [b for b in cfg["bagian_awal"] if not any(s.startswith(b) and len(s) < 40 for s in semua)]
    if tak_ada:
        hasil.add(INFO, "Bagian awal",
                  "Belum ada di berkas ini: " + ", ".join(tak_ada) +
                  ". Wajar bila disusun terpisah (halaman pengesahan/persetujuan diunduh dari SIAKAD).",
                  "Bab 4.1")


def cek_teks(doc, hasil):
    teks = [p.text for p in doc.paragraphs if p.text.strip()]
    # rujukan "tabel di atas/bawah"
    pola = re.compile(r"\b(tabel|gambar)\s+di\s+(atas|bawah)(\s+ini)?\b", re.IGNORECASE)
    temuan = []
    for t in teks:
        for m in pola.finditer(t):
            temuan.append(f"“{snippet(t[max(0, m.start() - 20): m.end() + 20], 60)}”")
    if temuan:
        hasil.add(WARN, "Rujukan tabel/gambar",
                  f"{len(temuan)} rujukan memakai 'di atas/di bawah': " + "; ".join(temuan[:4]) +
                  ". Gunakan nomor, mis. “Berdasarkan Tabel 3.1 …”.", "Bab 5.1.D.6 / E.4")
    else:
        hasil.add(OK, "Rujukan tabel/gambar", "Tidak ada rujukan 'di atas/di bawah ini'.", "Bab 5.1.D.6 / E.4")
    # kata tidak baku
    ketemu = Counter()
    for t in teks:
        low = t.lower()
        for salah in config.KATA_TIDAK_BAKU:
            for _ in re.finditer(r"\b" + re.escape(salah) + r"\w*", low):
                ketemu[salah] += 1
    if ketemu:
        rinci = ", ".join(f"{k}→{config.KATA_TIDAK_BAKU[k]} ({v}×)" for k, v in ketemu.most_common(6))
        hasil.add(WARN, "Kata tidak baku",
                  rinci + ". (Abaikan bila bagian dari nama mata kuliah/judul sumber.)", "Bab 5.1.F.10")
    else:
        hasil.add(OK, "Kata tidak baku", "Tidak ada kata tidak baku dari daftar pantauan.", "Bab 5.1.F.10")


def _tabel_punya_garis_vertikal(tbl: Table):
    tblpr = tbl._tbl.tblPr
    borders = tblpr.find(qn("w:tblBorders")) if tblpr is not None else None
    if borders is not None:
        for tag in ("left", "right", "insideV"):
            e = borders.find(qn(f"w:{tag}"))
            if e is not None and e.get(qn("w:val")) not in (None, "nil", "none"):
                return True
        return False
    nama = (tbl.style.name if tbl.style is not None else "") or ""
    if "grid" in nama.lower():
        return True
    # cek tcBorders
    for tc in tbl._tbl.iter(qn("w:tc")):
        tcpr = tc.find(qn("w:tcPr"))
        if tcpr is None:
            continue
        b = tcpr.find(qn("w:tcBorders"))
        if b is None:
            continue
        for tag in ("left", "right"):
            e = b.find(qn(f"w:{tag}"))
            if e is not None and e.get(qn("w:val")) not in (None, "nil", "none"):
                return True
    return False


def cek_tabel_gambar(doc, hasil):
    blok = list(doc.iter_inner_content())
    n_tabel = n_gambar = 0
    salah_posisi, vertikal = [], 0
    for i, b in enumerate(blok):
        if isinstance(b, Table):
            n_tabel += 1
            if _tabel_punya_garis_vertikal(b):
                vertikal += 1
            # cari paragraf tak kosong sebelumnya
            j = i - 1
            while j >= 0 and isinstance(blok[j], Paragraph) and not blok[j].text.strip():
                j -= 1
            prev = blok[j].text.strip() if j >= 0 and isinstance(blok[j], Paragraph) else ""
            if not re.match(r"^tabel\s+\d", prev, re.IGNORECASE):
                salah_posisi.append(f"tabel ke-{n_tabel}: judul tabel tidak ada tepat di atasnya")
        elif isinstance(b, Paragraph) and b._p.xpath(".//w:drawing | .//w:pict"):
            n_gambar += 1
            j = i + 1
            while j < len(blok) and isinstance(blok[j], Paragraph) and not blok[j].text.strip() \
                    and not blok[j]._p.xpath(".//w:drawing"):
                j += 1
            nxt = blok[j].text.strip() if j < len(blok) and isinstance(blok[j], Paragraph) else ""
            if not re.match(r"^gambar\s+\d", nxt, re.IGNORECASE):
                salah_posisi.append(f"gambar ke-{n_gambar}: judul gambar tidak ada tepat di bawahnya")
    if n_tabel == 0 and n_gambar == 0:
        hasil.add(INFO, "Tabel dan gambar", "Tidak ada tabel/gambar di berkas ini.", "Bab 5.1.D–E")
        return
    if salah_posisi:
        hasil.add(WARN, "Posisi judul tabel/gambar", "; ".join(salah_posisi[:5]) +
                  ". Aturan: judul tabel DI ATAS tabel, judul gambar DI BAWAH gambar.", "Bab 5.1.D.2 / E.2")
    else:
        hasil.add(OK, "Posisi judul tabel/gambar",
                  f"{n_tabel} tabel dan {n_gambar} gambar: posisi judul sesuai.", "Bab 5.1.D.2 / E.2")
    if n_tabel:
        if vertikal:
            hasil.add(WARN, "Garis tabel", f"{vertikal} dari {n_tabel} tabel memakai garis vertikal "
                      "(mis. gaya Table Grid). Aturan: hanya garis horizontal.", "Bab 5.1.D.8")
        else:
            hasil.add(OK, "Garis tabel", "Tidak ada garis vertikal terdeteksi.", "Bab 5.1.D.8")


def cek_nomor_halaman(doc, hasil):
    ada = False
    for s in doc.sections:
        for bagian in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            try:
                xml = bagian._element.xml
            except Exception:
                continue
            if "PAGE" in xml:
                ada = True
    if ada:
        hasil.add(INFO, "Nomor halaman",
                  "Ada field nomor halaman. Posisi (kanan atas 1,5 cm; judul bab di tengah bawah 1 cm) "
                  "dan format angka perlu dicek manual.", "Bab 5.1.B")
    else:
        hasil.add(WARN, "Nomor halaman", "Tidak ditemukan field nomor halaman di header/footer.", "Bab 5.1.B")


def cek_estimasi_halaman(doc, klas, cfg, hasil):
    wpp = config.WORDS_PER_PAGE_15 * 1.5 / cfg["spasi"]
    kata = Counter()
    sekarang = None
    for p, k in klas:
        if k == "toc":
            continue
        t = p.text.strip()
        if k == "bab":
            n = bab_number(t)
            if n is not None:
                sekarang = n
                continue
            sekarang = None  # Daftar Pustaka / Lampiran
            continue
        if sekarang is not None and t:
            kata[sekarang] += len(t.split())
    if not kata:
        hasil.add(INFO, "Estimasi halaman", "Tidak bisa memperkirakan (judul bab tidak terdeteksi).", "Bab 4.1")
        return
    baris, total = [], 0
    status = OK
    for bab, batas in cfg["max_halaman"].items():
        if bab not in kata:
            continue
        est = kata[bab] / wpp
        total += est
        tanda = ""
        if est > batas * 1.1:
            status = FAIL if status != FAIL else status
            tanda = " ❌"
        elif est > batas * 0.9:
            status = WARN if status == OK else status
            tanda = " ⚠️"
        baris.append(f"Bab {bab}: ±{math.ceil(est)} hlm (batas {batas}){tanda}")
    if cfg.get("max_total") and total > cfg["max_total"]:
        status = FAIL
        baris.append(f"Total ±{math.ceil(total)} hlm (batas {cfg['max_total']}) ❌")
    hasil.add(status, "Estimasi halaman per bab",
              "; ".join(baris) + f". Perkiraan kasar dari jumlah kata (±{int(wpp)} kata/halaman); "
              "teks di tabel dan gambar belum dihitung. Pastikan lagi di Word.", "Bab 4.1 / 4.2")


# ---------------------------------------------------------------------------
def tulis_laporan(hasil, berkas, cfg, path_keluar):
    c = hasil.hitung()
    baris = [
        f"# Laporan Cek Format — {cfg['label']}",
        "",
        f"- Berkas: `{berkas}`",
        f"- Tanggal: {today_str()}",
        f"- Acuan: Buku Pedoman TA FTI ITB Widya Gama Lumajang 2026-2027",
        f"- Ringkasan: ✅ {c[OK]} sesuai | ⚠️ {c[WARN]} peringatan | ❌ {c[FAIL]} gagal | ℹ️ {c[INFO]} info",
        "",
        "| Status | Aspek | Temuan | Rujukan pedoman |",
        "|---|---|---|---|",
    ]
    urut = {FAIL: 0, WARN: 1, INFO: 2, OK: 3}
    for s, a, d, r in sorted(hasil.items, key=lambda x: urut[x[0]]):
        baris.append(f"| {EMOJI[s]} {s} | {a} | {d.replace('|', '/')} | {r} |")
    baris += [
        "",
        "## Yang tidak bisa dicek otomatis (cek manual)",
        "",
        "- Posisi dan format angka nomor halaman, serta halaman sebenarnya per bab (tekan Ctrl+End di Word atau lihat PDF).",
        "- Istilah asing sudah dicetak miring.",
        "- Sampul: logo terbaru, kapital 12–16 pt, warna Biru Muda; halaman pengesahan dari SIAKAD.",
        "- Isi: kecukupan permasalahan, konsistensi tujuan–rumusan masalah, dsb. (gunakan prompt review-bab).",
    ]
    path_keluar.write_text("\n".join(baris) + "\n", encoding="utf-8")


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description="Cek format .docx terhadap pedoman TA FTI ITB Widya Gama.")
    ap.add_argument("berkas", help="path file .docx")
    ap.add_argument("--tahap", choices=list(config.TAHAP), default="proposal")
    ap.add_argument("--keluar", help="path laporan .md (default: output/laporan-format-<nama>-<tanggal>.md)")
    a = ap.parse_args()

    path = Path(a.berkas)
    if not path.exists():
        print(f"Berkas tidak ditemukan: {path}")
        sys.exit(2)
    if path.suffix.lower() != ".docx":
        print("Hanya mendukung .docx. Simpan dulu dari Word sebagai .docx (File → Save As).")
        sys.exit(2)

    cfg = config.TAHAP[a.tahap]
    doc = Document(str(path))
    dd = _docdefaults(doc)
    hasil = Hasil()

    cek_halaman_dan_margin(doc, cfg, hasil)
    cek_font(doc, cfg, hasil, dd)
    klas = klasifikasi_paragraf(doc)
    cek_paragraf_badan(klas, cfg, hasil, dd)
    cek_judul(klas, hasil, dd)
    cek_struktur(klas, cfg, hasil)
    cek_teks(doc, hasil)
    cek_tabel_gambar(doc, hasil)
    cek_nomor_halaman(doc, hasil)
    cek_estimasi_halaman(doc, klas, cfg, hasil)

    out = Path(a.keluar) if a.keluar else ensure_output_dir() / f"laporan-format-{path.stem}-{today_str()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    tulis_laporan(hasil, path.as_posix(), cfg, out)

    c = hasil.hitung()
    print(f"Cek format {cfg['label']} untuk {path.name}")
    print(f"  ✅ {c[OK]} sesuai | ⚠️ {c[WARN]} peringatan | ❌ {c[FAIL]} gagal | ℹ️ {c[INFO]} info")
    for s, asp, det, _ in sorted(hasil.items, key=lambda x: {FAIL: 0, WARN: 1, INFO: 2, OK: 3}[x[0]]):
        if s in (FAIL, WARN):
            print(f"  {EMOJI[s]} {asp}: {det}")
    print(f"Laporan lengkap: {out}")


if __name__ == "__main__":
    main()
