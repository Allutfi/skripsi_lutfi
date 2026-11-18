#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cek_gaya_bahasa.py - Memeriksa draf tulisan terhadap kaidah Anti-AI Slop,
pola teks artifisial, dan panduan gaya bahasa Buku Pedoman TA FTI ITB WiGa.

Fitur:
- Deteksi frasa klise AI Indonesia (AI slop tells) yang overused oleh LLM.
- Deteksi penggunaan em dash (—) berlebih.
- Deteksi kalimat terlalu panjang (> 30 kata).
- Deteksi rujukan terlarang ("tabel/gambar di atas/bawah").
- Deteksi kata ganti orang pertama ("saya", "kami").
- Menghasilkan laporan evaluasi dan saran perbaikan konkret.

Penggunaan:
    python scripts/cek_gaya_bahasa.py draft/proposal.md
    python scripts/cek_gaya_bahasa.py draft/proposal.docx
    python scripts/cek_gaya_bahasa.py output/teks/proposal.md --simpan
"""
import argparse
import re
import sys
from pathlib import Path

from common import ROOT, ensure_output_dir, setup_stdout, today_str

# ---------------------------------------------------------------------------
# Katalog Pola AI Slop & Pola Tulisan Kaku
# ---------------------------------------------------------------------------

AI_SLOP_PATTERNS = [
    # 1. Frasa Pembuka & Klise AI
    {
        "regex": r"\b(di era digital (yang serba cepat|saat ini)?|dalam era globalisasi (yang serba cepat)?)\b",
        "kategori": "Klise AI (Pembuka)",
        "bobot": "tinggi",
        "pesan": "Frasa pembuka klise AI generator. Hilangkan atau ganti dengan konteks tahun/fakta lapangan spesifik.",
        "contoh": "Ganti: 'Di era digital yang serba cepat ini...' -> 'Berdasarkan data operasional kantor desa tahun 2024...'"
    },
    {
        "regex": r"\b(di tengah (pesatnya|gempuran|hiruk-pikuk) (perkembangan|arus|modernisasi))\b",
        "kategori": "Klise AI (Metafora)",
        "bobot": "tinggi",
        "pesan": "Metafora dramatis khas AI. Sebutkan kondisi faktual langsung pada objek penelitian.",
        "contoh": "Ganti: 'Di tengah pesatnya perkembangan...' -> 'Seiring kebutuhan administrasi desa yang meningkat...'"
    },
    {
        "regex": r"\b(tidak dapat di(pungkiri|mungkiri)|tak dapat disangkal)\b\s*(bahwa)?",
        "kategori": "Klise AI (Penegas Kosong)",
        "bobot": "sedang",
        "pesan": "Frasa penegas retoris khas AI. Hapus frasa ini dan langsung tuliskan klaim ilmiah didukung sitasi.",
        "contoh": "Ganti: 'Tidak dapat dipungkiri bahwa sistem manual lambat' -> 'Pencatatan manual membutuhkan rata-rata waktu 15 menit (Sutrisno, 2023)'"
    },
    {
        "regex": r"\b(bagaikan (dua sisi mata uang|pisau bermata dua))\b",
        "kategori": "Klise AI (Metafora)",
        "bobot": "tinggi",
        "pesan": "Perumpamaan klise generik AI. Uraikan dampak positif dan negatif secara teknis/spesifik.",
        "contoh": "Jelaskan secara eksplisit manfaat sistem serta risiko batasan pengujiannya."
    },
    {
        "regex": r"\b(perlu digarisbawahi|patut di(catat|garisbawahi))\s+bahwa\b",
        "kategori": "Klise AI (Penegas)",
        "bobot": "sedang",
        "pesan": "Frasa transisi berbunga-bunga khas AI. Tuliskan argumen inti secara lugas.",
        "contoh": "Hapus frasa tersebut, jadikan inti argumen sebagai subjek utama kalimat."
    },
    {
        "regex": r"\b(membawa angin segar|lompatan kuantum|merevolusi (cara|sistem))\b",
        "kategori": "Klise AI (Hiperbola)",
        "bobot": "tinggi",
        "pesan": "Klaim hiperbolis/dramatis yang tidak terukur untuk konteks skripsi Software Engineering.",
        "contoh": "Ganti dengan metrik terukur: 'meningkatkan efisiensi waktu pemrosesan sebesar 40%'"
    },
    {
        "regex": r"\b(fondasi yang kokoh|tulang punggung|jantung dari sistem)\b",
        "kategori": "Klise AI (Metafora)",
        "bobot": "sedang",
        "pesan": "Metafora kiasan AI. Dalam Software Engineering, gunakan istilah arsitektur teknis yang tepat.",
        "contoh": "Ganti: 'Basis data adalah tulang punggung sistem' -> 'Basis data MySQL bertindak sebagai media persistensi data utama'"
    },
    {
        "regex": r"\b(menyelami lebih dalam|menguak rahasia|merangkul perubahan)\b",
        "kategori": "Klise AI (Sensasional)",
        "bobot": "tinggi",
        "pesan": "Diksi naratif novel/blog non-akademik khas AI. Gunakan kata kerja operasional penelitian.",
        "contoh": "Ganti dengan: 'menganalisis', 'mengidentifikasi', 'mengembangkan', 'menguji'"
    },

    # 2. Kata Slop Spesifik (sering overused tanpa konteks terukur)
    {
        "regex": r"\bkrusial\b",
        "kategori": "Diksi Overused (AI Slop)",
        "bobot": "rendah",
        "pesan": "Kata 'krusial' sangat sering diulang oleh AI. Pertimbangkan padanan alami seperti 'penting', 'esensial', atau 'mendasar'.",
        "contoh": "Ganti 'faktor krusial' menjadi 'faktor penentu' atau 'komponen utama'."
    },
    {
        "regex": r"\blanskap\b",
        "kategori": "Diksi Overused (AI Slop)",
        "bobot": "sedang",
        "pesan": "Terjemahan harfiah 'landscape' oleh AI. Di skripsi teknik, gunakan konteks 'ekosistem', 'kondisi', atau 'lingkungan'.",
        "contoh": "Ganti 'lanskap pelayanan publik' menjadi 'pelayanan administrasi di tingkat desa'."
    },
    {
        "regex": r"\bhiruk-pikuk\b",
        "kategori": "Diksi Overused (AI Slop)",
        "bobot": "tinggi",
        "pesan": "Kata puitis yang tidak relevan untuk penulisan karya ilmiah rekayasa perangkat lunak.",
        "contoh": "Ganti dengan deskripsi beban kerja nyata, misal 'volume permohonan surat'."
    },

    # 3. Frasa Triada / Triplet Klise
    {
        "regex": r"\b(cepat, tepat,( dan)? akurat|efektif, efisien,( dan)? transparan)\b",
        "kategori": "Triada Klise AI",
        "bobot": "sedang",
        "pesan": "Pola susunan tiga kata sifat berima (triad) khas AI tanpa menyertakan tolok ukur kuantitatif.",
        "contoh": "Ganti dengan metrik yang diuji di Bab 3, misalnya: 'mengurangi waktu tunggu pelayanan dari 2 hari menjadi 15 menit'."
    },

    # 4. Pelanggaran Pedoman Kampus (Bab 5.1.F)
    {
        "regex": r"\b(tabel|gambar|grafik|diagram)\s+di\s+(atas|bawah)(\s+ini)?\b",
        "kategori": "Pelanggaran Pedoman (Rujukan Posisi)",
        "bobot": "tinggi",
        "pesan": "Pedoman Bab 5.1.F melarang rujukan 'di atas/di bawah ini'. Wajib sebutkan nomor tabel/gambar secara eksplisit.",
        "contoh": "Ganti: 'sebagaimana terlihat pada tabel di bawah ini' -> 'sebagaimana disajikan pada Tabel 3.1'"
    },
    {
        "regex": r"\b(menurut (hemat )?saya|kami berasumsi|penulis merasa|menurut kami)\b",
        "kategori": "Pelanggaran Bahasa Akademik (Subjektif)",
        "bobot": "tinggi",
        "pesan": "Karya ilmiah menggunakan gaya kalimat pasif/objektif, bukan sudut pandang orang pertama.",
        "contoh": "Ganti: 'Menurut saya sistem ini efektif' -> 'Hasil pengujian menunjukkan sistem mampu meningkatkan efisiensi...'"
    }
]


def split_sentences(text: str):
    """Pecah paragraf menjadi kalimat-kalimat."""
    # Bersihkan markdown links dan heading
    t = re.sub(r"^#+.*$", "", text)
    # Split dengan pemisah titik/tanda tanya/seru diikuti spasi
    raw_sents = re.split(r"(?<=[.!?])\s+", t)
    sents = []
    for s in raw_sents:
        s_clean = s.strip()
        if len(s_clean) > 5 and not s_clean.startswith("|") and not s_clean.startswith("```"):
            sents.append(s_clean)
    return sents


def periksa_teks(teks: str):
    """Analisis teks draf dan kumpulkan temuan."""
    baris_list = teks.splitlines()
    semua_temuan = []
    total_kalimat = 0
    total_kata = 0
    em_dash_count = 0

    for no_baris, baris in enumerate(baris_list, 1):
        stripped = baris.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--") or stripped.startswith("|"):
            continue

        # Cek em-dash (— atau -- berlebih)
        dash_found = len(re.findall(r"(—|--)", stripped))
        em_dash_count += dash_found
        if dash_found >= 2:
            semua_temuan.append({
                "baris": no_baris,
                "kategori": "Tanda Baca (Em Dash Berlebih)",
                "bobot": "sedang",
                "pesan": f"Ditemukan {dash_found} tanda pisah em-dash (—) dalam satu baris. Pola ini sering dihasilkan AI. Gunakan kalimat majemuk terstruktur.",
                "kalimat": stripped[:120] + "..." if len(stripped) > 120 else stripped,
                "contoh": "Pecah klausa menjadi dua kalimat atau gunakan kata hubung resmi (seperti 'yang', 'sehingga')."
            })

        kalimat_baris = split_sentences(stripped)
        total_kalimat += len(kalimat_baris)

        for kalimat in kalimat_baris:
            kata_kalimat = kalimat.split()
            total_kata += len(kata_kalimat)

            # Cek panjang kalimat (> 30 kata)
            if len(kata_kalimat) > 30:
                semua_temuan.append({
                    "baris": no_baris,
                    "kategori": "Kalimat Terlalu Panjang (>30 kata)",
                    "bobot": "rendah",
                    "pesan": f"Kalimat terdiri dari {len(kata_kalimat)} kata (panduan: maks. ±30 kata). Kalimat berpotensi ambigu atau berbelit.",
                    "kalimat": kalimat[:130] + "...",
                    "contoh": "Pecah menjadi 2 gagasan pokok kalimat efektif."
                })

            # Cek terhadap pola-pola AI Slop
            for p in AI_SLOP_PATTERNS:
                m = re.search(p["regex"], kalimat, re.IGNORECASE)
                if m:
                    semua_temuan.append({
                        "baris": no_baris,
                        "kategori": p["kategori"],
                        "bobot": p["bobot"],
                        "pesan": p["pesan"],
                        "kalimat": kalimat,
                        "match": m.group(0),
                        "contoh": p["contoh"]
                    })

    # Hitung estimasi skor kealamian tulisan (Human-score heuristic)
    kalimat_terkena = len(set(f["baris"] for f in semua_temuan if f["bobot"] in ("tinggi", "sedang")))
    skor_alami = 100.0
    if total_kalimat > 0:
        penalti = (kalimat_terkena / total_kalimat) * 100
        skor_alami = max(0.0, min(100.0, 100.0 - penalti))

    return {
        "total_baris": len(baris_list),
        "total_kalimat": total_kalimat,
        "total_kata": total_kata,
        "em_dash_count": em_dash_count,
        "temuan": semua_temuan,
        "skor_alami": round(skor_alami, 1)
    }


def buat_laporan_markdown(nama_file: str, hasil: dict) -> str:
    """Format hasil analisis ke dalam laporan Markdown lengkap."""
    tgl = today_str()
    skor = hasil["skor_alami"]
    
    if skor >= 85:
        status_skor = "🟢 SANGAT BAIK (Tulisan alami, minim indikasi artifisial AI)"
    elif skor >= 70:
        status_skor = "🟡 CUKUP (Beberapa frasa klise AI dan kalimat panjang terdeteksi)"
    else:
        status_skor = "🔴 PERLU PERBAIKAN (Banyak pola tulisan AI slop terdeteksi)"

    laporan = [
        f"# Laporan Pengecekan Gaya Bahasa & Anti-AI Slop",
        f"",
        f"- **Dokumen yang diperiksa:** `{nama_file}`",
        f"- **Tanggal pemeriksaan:** {tgl}",
        f"- **Indikator kealamian tulisan:** **{skor}%** — {status_skor}",
        f"- **Statistik:** {hasil['total_kata']} kata | {hasil['total_kalimat']} kalimat | {len(hasil['temuan'])} catatan perbaikan",
        f"",
        f"---",
        f"",
        f"## 1. Ringkasan Evaluasi",
        f"",
        f"Pengecekan ini memastikan draf Anda bebas dari pola penulisan mesin generatif (AI Slop),",
        f"mematuhi kaidah penulisan akademik ilmiah, dan mematuhi batasan integritas pedoman kampus (Bab 5.1 & Bab 5.5).",
        f"",
    ]

    if not hasil["temuan"]:
        laporan.append("✅ **Luar biasa!** Tidak ditemukan frasa klise AI, rujukan terlarang, atau kalimat bertele-tele pada dokumen ini.")
        return "\n".join(laporan)

    laporan.append("## 2. Rincian Temuan dan Saran Perbaikan")
    laporan.append("")
    laporan.append("| Baris | Jenis Temuan | Bobot | Potongan Teks / Masalah | Rekomendasi Solusi |")
    laporan.append("|---|---|---|---|---|")

    for f in hasil["temuan"]:
        bobot_icon = "🔴" if f["bobot"] == "tinggi" else ("🟡" if f["bobot"] == "sedang" else "ℹ️")
        cuplikan = f["kalimat"].replace("\n", " ").replace("|", "\\|")
        if len(cuplikan) > 90:
            cuplikan = cuplikan[:87] + "..."
        saran = f["contoh"].replace("\n", " ").replace("|", "\\|")
        pesan = f["pesan"].replace("|", "\\|")
        laporan.append(f"| L{f['baris']} | {f['kategori']} | {bobot_icon} {f['bobot'].capitalize()} | *\"{cuplikan}\"*<br><small>{pesan}</small> | {saran} |")

    laporan.append("")
    laporan.append("---")
    laporan.append("## 3. Prinsip Menulis Alami (Anti-AI Slop) untuk Mahasiswa")
    laporan.append("1. **Langsung ke Inti (To the Point):** Hindari kalimat pembuka mengambang seperti 'Di era modern yang serba cepat ini...'. Langsung sebutkan fakta atau masalah di instansi penelitian.")
    laporan.append("2. **Gunakan Data & Metrik:** Jangan gunakan kata sifat berlebihan seperti 'sangat krusial' atau 'hasil yang revolusioner'. Gantilah dengan angka konkret.")
    laporan.append("3. **Sebutkan Nomor Objek:** Jangan gunakan rujukan posisi 'tabel di atas' atau 'gambar di bawah'. Selalu gunakan 'Tabel X.X' atau 'Gambar X.X'.")
    laporan.append("4. **Kalimat Efektif:** Batasi panjang kalimat maksimal ±30 kata agar alur logika dapat dipertanggungjawabkan saat sidang skripsi.")

    return "\n".join(laporan)


def main():
    setup_stdout()
    parser = argparse.ArgumentParser(
        description="Pengecek gaya bahasa, Anti-AI Slop, dan kesesuaian pedoman naskah skripsi."
    )
    parser.add_argument("file", help="Path file draf (.md atau .docx)")
    parser.add_argument("--simpan", action="store_true", help="Simpan laporan markdown ke folder output/")

    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"[!] Berkas tidak ditemukan: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Tangani .docx jika diberikan
    teks = ""
    if file_path.suffix.lower() == ".docx":
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            teks = "\n\n".join(paragraphs)
        except Exception as e:
            print(f"[!] Gagal membaca .docx ({e}). Coba ubah dulu ke markdown dengan python scripts/docx_ke_md.py", file=sys.stderr)
            sys.exit(1)
    else:
        teks = file_path.read_text(encoding="utf-8", errors="replace")

    print(f"[*] Memeriksa gaya bahasa & pola AI slop pada: {file_path.name}...")
    hasil = periksa_teks(teks)

    print(f"\n[+] Hasil Evaluasi Gaya Bahasa:")
    print(f"    Total Kata      : {hasil['total_kata']}")
    print(f"    Total Kalimat   : {hasil['total_kalimat']}")
    print(f"    Indikator Alami : {hasil['skor_alami']}%")
    print(f"    Jumlah Catatan  : {len(hasil['temuan'])}")
    print("-" * 75)

    if not hasil["temuan"]:
        print("✅ Tidak ditemukan pola AI slop atau pelanggaran gaya bahasa pokok. Bagus!")
    else:
        for idx, f in enumerate(hasil["temuan"][:8], 1):
            icon = "🔴" if f["bobot"] == "tinggi" else ("🟡" if f["bobot"] == "sedang" else "ℹ️")
            print(f"{idx}. {icon} [Baris {f['baris']}] {f['kategori']}")
            print(f"   Kalimat: \"{f['kalimat'][:100]}...\"" if len(f['kalimat']) > 100 else f"   Kalimat: \"{f['kalimat']}\"")
            print(f"   Saran  : {f['contoh']}")
            print()

        if len(hasil["temuan"]) > 8:
            print(f"   ... dan {len(hasil['temuan']) - 8} catatan lainnya.")

    # Simpan laporan
    out_dir = ensure_output_dir()
    laporan_md = buat_laporan_markdown(file_path.name, hasil)
    nama_laporan = f"laporan-gaya-bahasa-{file_path.stem}-{today_str()}.md"
    laporan_path = out_dir / nama_laporan
    laporan_path.write_text(laporan_md, encoding="utf-8")
    print(f"[+] Laporan lengkap disimpan ke: output/{nama_laporan}")


if __name__ == "__main__":
    main()
