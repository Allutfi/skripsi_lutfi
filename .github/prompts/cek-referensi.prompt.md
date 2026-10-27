---
description: Cek kecukupan daftar pustaka (jumlah, % jurnal, % ≤10 tahun, urutan, kutipan vs pustaka)
---
Tugas: cek daftar pustaka pada **${input:file:Nama file di folder draft/ (.docx atau .md) yang memuat DAFTAR PUSTAKA}**.

Pegangan: [AGENTS.md](../../AGENTS.md), [pedoman](../../knowledge/pedoman-ta-software-engineering-programming.md) (Bagian 4.5, 9, 12).

Langkah:
1. Jalankan `python scripts/cek_referensi.py draft/<file>`; baca `output/laporan-referensi-*.md`.
2. Jelaskan hasilnya terhadap target: ≥ 15 referensi (saran 15–20), ≥ 60% jurnal/prosiding, ≥ 10 sumber jurnal, ≥ 80% terbit ≤ 10 tahun.
   Pakai aturan paling ketat bila pedoman bertentangan (Bagian 12) dan sebutkan itu.
3. Bandingkan dengan `referensi/daftar-sumber.md`: entri yang ada di daftar pustaka tetapi belum punya catatan/belum terverifikasi perlu ditandai.
   Tinjau temuan heuristik (kutipan tanpa entri, entri tanpa kutipan, jenis sumber yang mungkin salah klasifikasi) dan **minta saya memverifikasinya**; skrip bukan keputusan akhir.
4. Periksa kesesuaian penulisan entri dengan gaya APA di pedoman (Bagian 9): urutan A–Z, nama penulis, tanda baca, tahun dalam kurung.
5. Jika kurang, sarankan **jenis sumber yang perlu ditambah** dan kata kunci pencarian. **Jangan menyebut atau membuat referensi spesifik** yang tidak bisa kamu verifikasi.
6. Simpan ringkasan ke `output/review-referensi-<nama>-<YYYYMMDD>.md`.
