#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cari_openalex.py - Mencari kandidat referensi ilmiah terindeks dari OpenAlex API.

Fitur:
- Menyaring artikel/jurnal/prosiding berdasarkan kata kunci dan tahun terbit (default 2022-2026).
- Membentuk sitasi format APA secara otomatis dari metadata.
- Rekonstruksi abstrak dari inverted index OpenAlex.
- Opsional (--buat-catatan): otomatis membuat draft catatan di referensi/catatan/<id>.md
  dengan status "belum-diverifikasi" dan asal "rekomendasi-agent" sesuai aturan AGENTS.md.

Penggunaan:
    python scripts/cari_openalex.py "sistem informasi desa pelayanan surat"
    python scripts/cari_openalex.py "prototyping web application" --tahun-mulai 2022 --limit 5
    python scripts/cari_openalex.py "surat desa laravel" --buat-catatan
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from common import ROOT, setup_stdout

CATATAN_DIR = ROOT / "referensi" / "catatan"


def format_author_name(display_name: str) -> str:
    """Ubah 'Ahmad Dahlan' -> 'Dahlan, A.'"""
    parts = display_name.strip().split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    last = parts[-1]
    initials = ". ".join(p[0].upper() for p in parts[:-1]) + "."
    return f"{last}, {initials}"


def build_apa_citation(authors, year, title, source_name, volume=None, issue=None, pages=None, doi=None):
    """Bentuk sitasi APA dasar dari komponen metadata."""
    if not authors:
        auth_str = "Anonim"
    elif len(authors) == 1:
        auth_str = format_author_name(authors[0])
    elif len(authors) == 2:
        auth_str = f"{format_author_name(authors[0])}, & {format_author_name(authors[1])}"
    else:
        formatted = [format_author_name(a) for a in authors]
        if len(formatted) > 7:
            auth_str = ", ".join(formatted[:6]) + ", ... " + formatted[-1]
        else:
            auth_str = ", ".join(formatted[:-1]) + f", & {formatted[-1]}"

    # Bersihkan titik ganda pada akhir judul
    clean_title = (title or "").strip()
    if clean_title and not clean_title.endswith("."):
        clean_title += "."

    source_part = ""
    if source_name:
        source_part = f" *{source_name}*"
        if volume:
            source_part += f", {volume}"
            if issue:
                source_part += f"({issue})"
        if pages:
            source_part += f", {pages}"
        source_part += "."

    doi_part = f" {doi}" if doi else ""
    return f"{auth_str} ({year or 'n.d.'}). {clean_title}{source_part}{doi_part}".strip()


def reconstruct_abstract(inverted_index: dict) -> str:
    """Rekonstruksi teks abstrak dari abstract_inverted_index milik OpenAlex."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    positions = []
    for word, pos_list in inverted_index.items():
        for p in pos_list:
            positions.append((p, word))
    positions.sort(key=lambda x: x[0])
    text = " ".join(w for _, w in positions)
    return text.strip()


def generate_candidate_id(first_author: str, year: int or str) -> str:
    """Buat ID unik seperti 'pratama-2023'."""
    parts = first_author.strip().split()
    last = parts[-1] if parts else "penulis"
    clean_last = re.sub(r"[^a-zA-Z0-9]", "", last).lower() or "sumber"
    base_id = f"{clean_last}-{year}"
    target = CATATAN_DIR / f"{base_id}.md"
    if not target.exists():
        return base_id
    # Jika sudah ada, tambahkan suffix a, b, c...
    for char in "abcdefghijklmnopqrstuvwxyz":
        cand = f"{base_id}{char}"
        if not (CATATAN_DIR / f"{cand}.md").exists():
            return cand
    return f"{base_id}-{int(datetime.now().timestamp())}"


def search_openalex(query: str, tahun_mulai: int = 2022, tahun_akhir: int = None, limit: int = 5, hanya_oa: bool = False):
    """Panggil OpenAlex API untuk mengambil karya ilmiah yang relevan."""
    if tahun_akhir is None:
        tahun_akhir = datetime.now().year + 1

    encoded_query = urllib.parse.quote_plus(query)
    filter_params = [f"from_publication_date:{tahun_mulai}-01-01", f"to_publication_date:{tahun_akhir}-12-31"]
    if hanya_oa:
        filter_params.append("is_oa:true")

    filter_str = ",".join(filter_params)
    url = f"https://api.openalex.org/works?search={encoded_query}&filter={filter_str}&per-page={limit}&sort=relevance_score:desc"

    headers = {
        "User-Agent": "skripsi-agent/1.0 (mailto:skripsi@itbwiga.ac.id; Academic Research Helper)"
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("results", [])
    except urllib.error.URLError as e:
        print(f"[!] Gagal menghubungi OpenAlex API: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[!] Terjadi kesalahan saat memproses data OpenAlex: {e}", file=sys.stderr)
        return []


def parse_work(work: dict):
    """Ekstraksi metadata penting dari objek OpenAlex."""
    title = work.get("title") or "Tanpa Judul"
    year = work.get("publication_year") or datetime.now().year
    doi = work.get("doi") or ""
    
    # Authors
    authors = []
    for auth in work.get("authorships", []):
        dname = auth.get("author", {}).get("display_name")
        if dname:
            authors.append(dname)
            
    # Location / Source
    primary_loc = work.get("primary_location") or {}
    source = primary_loc.get("source") or {}
    source_name = source.get("display_name") or ""
    source_type = (source.get("type") or "").lower()
    
    if "conference" in source_type or "proceeding" in source_type:
        jenis = "prosiding"
    elif "journal" in source_type:
        jenis = "jurnal"
    elif "book" in source_type:
        jenis = "buku"
    else:
        jenis = "jurnal" if source_name else "lainnya"

    landing_page = primary_loc.get("landing_page_url") or doi or work.get("id") or ""
    is_oa = primary_loc.get("is_oa", False)
    pdf_url = primary_loc.get("pdf_url") or ""

    # Abstract
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    
    apa_citation = build_apa_citation(authors, year, title, source_name, doi=doi or landing_page)

    first_author = authors[0] if authors else "penulis"
    cid = generate_candidate_id(first_author, year)

    return {
        "id": cid,
        "title": title,
        "year": year,
        "authors": authors,
        "source_name": source_name,
        "jenis": jenis,
        "doi": doi,
        "tautan": landing_page,
        "pdf_url": pdf_url,
        "is_oa": is_oa,
        "abstract": abstract,
        "apa": apa_citation,
    }


def simpan_catatan(item: dict) -> Path:
    """Tulis file markdown draft di referensi/catatan/<id>.md."""
    CATATAN_DIR.mkdir(parents=True, exist_ok=True)
    target_path = CATATAN_DIR / f"{item['id']}.md"

    # Escape petik dua pada judul/apa
    safe_apa = item["apa"].replace('"', '\\"')

    konten = f"""---
id: {item['id']}
apa: "{safe_apa}"
jenis: {item['jenis']}
tahun: {item['year']}
tautan: {item['tautan']}
status: belum-diverifikasi
asal: rekomendasi-agent
dipakai_di: bab 2.1, bab 2.2
---

# Catatan: {item['title']}

> Sumber ini ditemukan otomatis melalui OpenAlex API.
> **PENTING:** Buka tautan/DOI di atas, baca dokumen aslinya, lalu ubah status menjadi `terverifikasi` jika data cocok.

## Masalah / tujuan penelitian
{item['abstract'] if item['abstract'] else '[belum dibaca: abstrak tidak tersedia di metadata]'}

## Metode (algoritma, teknologi, desain, cara pengujian)
[belum dibaca]

## Hasil / temuan utama (sertakan angka bila ada)
[belum dibaca]

## Kelebihan dan keterbatasan
[belum dibaca]

## Kaitan dengan penelitianku
[belum dibaca]

## Kutipan penting (opsional, maks. 1 kalimat pendek, < 15 kata) + halaman
[belum dibaca]
"""
    target_path.write_text(konten, encoding="utf-8")
    return target_path


def main():
    setup_stdout()
    parser = argparse.ArgumentParser(
        description="Cari kandidat jurnal ilmiah dari OpenAlex (sesuai target tahun kampus)."
    )
    parser.add_argument("query", help="Kata kunci pencarian, mis. 'sistem informasi desa' atau 'prototyping laravel'")
    parser.add_argument("--tahun-mulai", type=int, default=2022, help="Tahun terbit paling awal (default: 2022, 5 tahun terakhir)")
    parser.add_argument("--tahun-akhir", type=int, default=None, help="Tahun terbit paling akhir (default: tahun sekarang)")
    parser.add_argument("--limit", type=int, default=5, help="Jumlah hasil yang dicari (default: 5)")
    parser.add_argument("--hanya-oa", action="store_true", help="Hanya tampilkan sumber open-access (dapat diunduh bebas)")
    parser.add_argument("--buat-catatan", action="store_true", help="Otomatis buat file catatan draft di referensi/catatan/")

    args = parser.parse_args()

    print(f"[*] Mencari referensi di OpenAlex untuk kata kunci: '{args.query}'...")
    print(f"[*] Rentang tahun: {args.tahun_mulai} s.d. {args.tahun_akhir or 'sekarang'} (target 5 tahun terakhir)")

    raw_results = search_openalex(
        query=args.query,
        tahun_mulai=args.tahun_mulai,
        tahun_akhir=args.tahun_akhir,
        limit=args.limit,
        hanya_oa=args.hanya_oa,
    )

    if not raw_results:
        print("\n[-] Tidak ada hasil yang ditemukan atau koneksi ke OpenAlex API gagal.")
        print("    Saran kata kunci alternatif:")
        print("    - Gunakan istilah dalam bahasa Inggris (mis. 'village information system prototyping')")
        print("    - Perluas istilah pencarian (mis. 'layanan surat desa' -> 'e-government desa')")
        print("    - Cek juga secara manual di Google Scholar, SINTA Kemdikbud, atau Garuda.")
        return

    items = [parse_work(w) for w in raw_results]

    print(f"\n[+] Ditemukan {len(items)} kandidat karya ilmiah:\n" + "=" * 80)
    for idx, it in enumerate(items, 1):
        print(f"{idx}. [{it['jenis'].upper()}] {it['title']} ({it['year']})")
        print(f"   Penulis : {', '.join(it['authors'][:3])}{' dkk.' if len(it['authors']) > 3 else ''}")
        print(f"   Sumber  : {it['source_name'] or '-'}")
        print(f"   Tautan  : {it['tautan']}")
        if it['abstract']:
            ringkas = (it['abstract'][:180] + "...") if len(it['abstract']) > 180 else it['abstract']
            print(f"   Abstrak : {ringkas}")
        print(f"   Sitasi  : {it['apa']}")
        
        if args.buat_catatan:
            saved_file = simpan_catatan(it)
            print(f"   -> Draft catatan disimpan ke: {saved_file.name}")
        print("-" * 80)

    if args.buat_catatan:
        print("\n[!] Ingat aturan AGENTS.md Bagian 10:")
        print("    Semua draft catatan di atas berstatus 'belum-diverifikasi'.")
        print("    Buka berkas di referensi/catatan/, baca dokumen aslinya, lalu ubah status menjadi 'terverifikasi'.")
        print("    Setelah selesai, jalankan: python scripts/buat_daftar_sumber.py")
    else:
        print("\n[Tip] Jalankan dengan opsi --buat-catatan untuk langsung membuat draft catatan di referensi/catatan/")


if __name__ == "__main__":
    main()
