---
description: Tambahkan jurnal/artikel ke referensi/catatan dari link, DOI, atau file PDF di referensi/pdf
---
Tugas: tambahkan sumber ini ke folder referensi: **${input:sumber:Tempel link/DOI, atau nama file PDF di referensi/pdf/}**

Pegangan: [AGENTS.md](../../AGENTS.md) Bagian 10 (Aturan sumber & referensi), [README referensi](../../referensi/README.md), [template](../../referensi/catatan/_TEMPLATE.md).

Bagian bab yang akan memakai sumber ini (boleh kosong): ${input:bab:mis. bab 2.1, bab 2.2}

Langkah:
1. **Jika file PDF**: jalankan `python scripts/ekstrak_teks.py referensi/pdf/<file>`, lalu baca `referensi/teks/<nama>.md`.
   **Jika link/DOI**: buka halamannya dengan alat web yang tersedia. Jika kamu **tidak punya akses web**, katakan terus terang,
   buat file dengan data yang saya berikan saja, dan biarkan sisanya `[belum dibaca]`.
2. Ambil metadata **hanya dari sumber yang benar-benar kamu baca** (penulis, judul, tahun, nama jurnal, volume/nomor, halaman, DOI). Jangan melengkapi dari ingatan.
3. Buat `referensi/catatan/<id>.md` dari template (`id` = nama belakang penulis pertama + tahun, huruf kecil). Isi:
   - frontmatter lengkap, sitasi APA mengikuti Bagian 9 pedoman, `asal: dari-saya`, `status: belum-diverifikasi`
     (**jangan mengubahnya ke terverifikasi; itu keputusan saya** setelah mencocokkan sumbernya);
   - ringkasan singkat dengan **kata-katamu sendiri** hanya untuk bagian yang benar-benar terbaca dari teks/abstrak.
     Bagian lain tetap `[belum dibaca]`. Jangan menyalin paragraf asli.
4. Jalankan `python scripts/buat_daftar_sumber.py` untuk memperbarui indeks.
5. Laporkan: file yang dibuat, apa yang sudah terisi, apa yang masih perlu saya verifikasi, dan progres menuju target (≥ 15 referensi, dst.).
