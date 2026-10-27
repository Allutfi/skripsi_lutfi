---
description: Ubah naskah Markdown menjadi .docx (dan PDF) berformat pedoman, lalu cek formatnya
---
Tugas: ubah naskah **${input:file:Nama file .md di folder draft/, mis. proposal.md}** menjadi dokumen Word berformat pedoman.

Pegangan: [AGENTS.md](../../AGENTS.md), [pedoman](../../knowledge/pedoman-ta-software-engineering-programming.md) (Bagian 7, 8).

Langkah:
1. Pastikan naskah memakai sintaks yang dikenali `scripts/buat_docx.py` (lihat komentar di bagian atas skrip): `# BAB …`, `## 1.1 …`, tabel pipa, judul tabel di atas tabel, judul gambar di bawah gambar, `# DAFTAR PUSTAKA`.
   Jika ada yang tidak sesuai, beri tahu saya (jangan diam-diam mengubah isi).
2. Jalankan `python scripts/buat_docx.py draft/<file> --pdf`. Jika PDF gagal dibuat, jelaskan penyebabnya
   (LibreOffice/Word tidak ditemukan) dan beri cara menyimpan PDF manual dari Word.
3. Jalankan `python scripts/cek_format.py output/<nama>.docx` dan ringkas hasilnya.
4. Beri tahu path file `.docx` dan `.pdf` di `output/`, serta apa yang masih perlu saya lengkapi manual
   (sampul, halaman pengesahan dan persetujuan dari SIAKAD, kata pengantar, daftar isi/tabel/gambar).

Catatan: hasil hanya mencakup isi proposal (Bab 1–3 + Daftar Pustaka). Jangan menimpa file di `draft/`.
