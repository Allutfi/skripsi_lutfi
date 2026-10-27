---
description: Cek format dokumen .docx terhadap pedoman (margin, font, spasi, judul, tabel, dsb.) lalu jelaskan cara memperbaikinya
---
Tugas: cek format **${input:file:Nama file .docx di folder draft/, mis. proposal.docx}**.

Pegangan: [AGENTS.md](../../AGENTS.md), [pedoman](../../knowledge/pedoman-ta-software-engineering-programming.md) (Bagian 8, 9, 14).

Langkah:
1. Jalankan `python scripts/cek_format.py draft/<file>` (tahap proposal; jangan menebak angka).
2. Baca laporan yang dihasilkan di `output/laporan-format-*.md`.
3. Untuk tiap temuan ⚠️/❌ jelaskan **cara memperbaikinya di Microsoft Word** secara konkret
   (mis. Layout → Margins → Custom; Paragraph → Special → First line 0,75 cm; Line spacing → Multiple 1,5),
   urut dari yang paling berdampak.
4. Daftarkan hal yang **tidak bisa dicek skrip** dan perlu saya cek manual: halaman sebenarnya per bab,
   posisi nomor halaman, istilah asing miring, sampul (warna Biru Muda, kapital 12–16 pt), halaman pengesahan dari SIAKAD.
5. Jika semua sesuai, katakan dengan jelas; jangan mengada-ada temuan.
6. Simpan ringkasan perbaikan ke `output/perbaikan-format-<nama>-<YYYYMMDD>.md`.

Jangan mengubah file di `draft/`.
