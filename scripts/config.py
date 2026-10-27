# -*- coding: utf-8 -*-
"""
config.py - Aturan dari Buku Pedoman Tugas Akhir 2026-2027
FTI ITB Widya Gama Lumajang, dipusatkan di satu tempat.

Kalau pedoman direvisi, atau kamu naik tahap dari proposal ke laporan skripsi,
cukup ubah file ini. Semua skrip lain membaca angka dari sini.
"""

# ---------------------------------------------------------------------------
# Format dasar (Bab 5.1 pedoman)
# ---------------------------------------------------------------------------
FORMAT = {
    "page_width_cm": 21.0,       # A4
    "page_height_cm": 29.7,
    "margin_top_cm": 4.0,
    "margin_left_cm": 4.0,
    "margin_right_cm": 3.0,
    "margin_bottom_cm": 3.0,
    "font_name": "Times New Roman",
    "font_size_pt": 12,
    "first_line_indent_cm": 0.75,   # indentasi paragraf baru
    "header_distance_cm": 1.5,      # nomor halaman: 1,5 cm dari tepi atas
    "right_offset_cm": 1.5,         # ... dan 1,5 cm dari tepi kanan
    "footer_distance_cm": 1.0,      # nomor halaman judul bab: 1 cm dari tepi bawah
    "pustaka_hanging_cm": 1.5,      # baris kedua daftar pustaka menjorok 1,5 cm
    "table_font_pt": 12,
}

# Pedoman tidak mengatur rata teks. "justify" lazim di skripsi; ganti "left" bila perlu.
ALIGN_BODY = "justify"

# Toleransi pengecekan
TOL_CM = 0.1          # margin / ukuran kertas / indentasi
TOL_SPASI = 0.05      # spasi baris

# Estimasi kasar jumlah kata per halaman pada 1,5 spasi, TNR 12, margin 4-4-3-3.
# Dipakai HANYA untuk memperkirakan jumlah halaman per bab. Selalu cek ulang di Word.
WORDS_PER_PAGE_15 = 300

# ---------------------------------------------------------------------------
# Tahap penulisan
# ---------------------------------------------------------------------------
# kunci = kata awal judul (setelah nomor dibuang, huruf kecil). Beberapa alternatif
# dipakai karena mahasiswa bisa menulis judul sedikit berbeda ("dan" vs "&", dst.).
_BAB1 = [
    {"nomor": "BAB 1", "kunci": ["pendahuluan"], "tampil": "BAB 1 PENDAHULUAN"},
    {"nomor": "1.1", "kunci": ["latar belakang"], "tampil": "1.1 Latar Belakang Masalah"},
    {"nomor": "1.2", "kunci": ["batasan masalah"], "tampil": "1.2 Batasan Masalah"},
    {"nomor": "1.3", "kunci": ["rumusan masalah"], "tampil": "1.3 Rumusan Masalah"},
    {"nomor": "1.4", "kunci": ["tujuan penelitian"], "tampil": "1.4 Tujuan Penelitian"},
    {"nomor": "1.5", "kunci": ["manfaat penelitian"], "tampil": "1.5 Manfaat Penelitian"},
]
_BAB2 = [
    {"nomor": "BAB 2", "kunci": ["tinjauan pustaka"], "tampil": "BAB 2 TINJAUAN PUSTAKA"},
    {"nomor": "2.1", "kunci": ["landasan teori"], "tampil": "2.1 Landasan Teori"},
    {"nomor": "2.2", "kunci": ["penelitian terdahulu"], "tampil": "2.2 Penelitian Terdahulu"},
]
_BAB3_COMMON = [
    {"nomor": "BAB 3", "kunci": ["metode penelitian"], "tampil": "BAB 3 METODE PENELITIAN"},
    {"nomor": "3.1", "kunci": ["jenis dan pendekatan", "jenis & pendekatan", "jenis penelitian"],
     "tampil": "3.1 Jenis dan Pendekatan Penelitian"},
    {"nomor": "3.2", "kunci": ["objek/sumber data", "objek dan sumber data", "objek penelitian", "sumber data"],
     "tampil": "3.2 Objek/Sumber Data Penelitian"},
    {"nomor": "3.3", "kunci": ["teknik pengumpulan data"], "tampil": "3.3 Teknik Pengumpulan Data"},
    {"nomor": "3.4", "kunci": ["tahapan penelitian", "alur penelitian"], "tampil": "3.4 Tahapan Penelitian"},
    {"nomor": "3.5", "kunci": ["desain sistem", "perancangan sistem"], "tampil": "3.5 Desain Sistem"},
    {"nomor": "3.6", "kunci": ["alat penelitian", "alat dan bahan", "alat bantu"], "tampil": "3.6 Alat Penelitian"},
    {"nomor": "3.7", "kunci": ["teknik analisis data", "teknik analisa data"], "tampil": "3.7 Teknik Analisis Data"},
]
_PUSTAKA = [{"nomor": "-", "kunci": ["daftar pustaka"], "tampil": "DAFTAR PUSTAKA"}]

TAHAP = {
    # ---- AKTIF: proposal skripsi (Bab 4.1 pedoman) ----
    "proposal": {
        "label": "Proposal Skripsi",
        "spasi": 1.5,                                  # Bab 5.1.A
        "max_halaman": {1: 5, 2: 15, 3: 15},           # Bab 4.1
        "max_total": None,
        "judul_wajib": _BAB1 + _BAB2 + _BAB3_COMMON + [
            {"nomor": "3.8", "kunci": ["jadwal penelitian", "waktu pelaksanaan", "waktu penelitian"],
             "tampil": "3.8 Jadwal Penelitian"},
        ] + _PUSTAKA,
        # Bagian awal: hanya diberi INFO bila tidak ada (sering dibuat terpisah dari SIAKAD)
        "bagian_awal": ["kata pengantar", "daftar isi", "daftar tabel", "daftar gambar"],
    },
    # ---- BELUM AKTIF / SIAP DIPAKAI NANTI: laporan skripsi (Bab 4.2 pedoman) ----
    # Belum diuji pada draf nyata. Pakai dengan: --tahap laporan
    "laporan": {
        "label": "Laporan Skripsi",
        "spasi": 2.0,
        "max_halaman": {1: 5, 2: 15, 3: 15, 4: 30, 5: 5},
        "max_total": 70,                               # Bab I sampai V
        "judul_wajib": _BAB1 + _BAB2 + _BAB3_COMMON + [
            {"nomor": "3.8", "kunci": ["waktu pelaksanaan", "jadwal penelitian", "waktu penelitian"],
             "tampil": "3.8 Waktu Pelaksanaan Penelitian"},
            {"nomor": "BAB 4", "kunci": ["hasil dan pembahasan"], "tampil": "BAB 4 HASIL DAN PEMBAHASAN"},
            {"nomor": "4.1", "kunci": ["hasil penelitian", "hasil"], "tampil": "4.1 Hasil Penelitian"},
            {"nomor": "4.2", "kunci": ["pembahasan"], "tampil": "4.2 Pembahasan"},
            {"nomor": "BAB 5", "kunci": ["penutup"], "tampil": "BAB 5 PENUTUP"},
            {"nomor": "5.1", "kunci": ["kesimpulan"], "tampil": "5.1 Kesimpulan"},
            {"nomor": "5.2", "kunci": ["saran"], "tampil": "5.2 Saran"},
        ] + _PUSTAKA,
        "bagian_awal": ["kata pengantar", "abstrak", "abstract", "daftar isi", "daftar tabel",
                        "daftar gambar", "daftar lampiran"],
    },
}

# ---------------------------------------------------------------------------
# Referensi (Bab 1.4, 3.3, 5.1.G pedoman)
# ---------------------------------------------------------------------------
REFERENSI = {
    "min_total": 15,            # Bab 3.3: 15-20 referensi
    "saran_max_total": 20,
    "min_pct_jurnal_prosiding": 60,
    "min_jurnal": 10,           # Bab 1.4: minimal 10 sumber dari jurnal ilmiah
    "min_pct_terbaru": 80,      # >= 80% terbit dalam 10 tahun terakhir
    "tahun_batas": 10,
    "tahun_preferensi": 5,      # Bab 1.4 menyebut 5 hingga 10 tahun terakhir
}

# ---------------------------------------------------------------------------
# Kata tidak baku yang disebut / sejenis dengan contoh di pedoman (Bab 5.1.F)
# ---------------------------------------------------------------------------
KATA_TIDAK_BAKU = {
    "obyek": "objek",
    "analisa": "analisis",
    "aktifitas": "aktivitas",
    "resiko": "risiko",
    "kwalitas": "kualitas",
    "sistim": "sistem",
    "merubah": "mengubah",
    "mengkonsumsi": "mengonsumsi",
}
