---
description: Cari kandidat jurnal/artikel untuk bab atau topik tertentu (dengan tautan, belum diverifikasi)
---
Tugas: carikan kandidat referensi untuk **${input:topik:Topik/bab yang butuh referensi, mis. "pengujian unit pada aplikasi web untuk Bab 2.1"}**.

Pegangan: [AGENTS.md](../../AGENTS.md) Bagian 10, [daftar sumber](../../referensi/daftar-sumber.md), [konteks penelitian](../../knowledge/konteks-penelitian.md), [pedoman](../../knowledge/pedoman-ta-software-engineering-programming.md) (Bagian 4.5, 12).

Langkah:
1. Baca `referensi/daftar-sumber.md` agar tidak merekomendasikan yang sudah ada, dan lihat kekurangan terhadap target
   (jumlah, % jurnal/prosiding, jumlah jurnal, % ≤ 10 tahun).
2. **Jika kamu punya alat pencarian/akses web**: cari sumber ilmiah (jurnal/prosiding terindeks, terbit ≤ 10 tahun, relevan dengan topik Programming-ku).
   Untuk tiap kandidat, buka halaman sumbernya dan pastikan penulis, judul, tahun, jurnal, dan **tautan/DOI** benar-benar ada.
   Buang kandidat yang tidak bisa kamu verifikasi.
3. **Jika kamu tidak punya akses web**: katakan terus terang, **jangan menyebut judul/penulis dari ingatan**.
   Berikan saja kata kunci pencarian (Indonesia dan Inggris), operator pencarian, dan mesin pencari yang cocok
   (Google Scholar, Garuda, SINTA, IEEE Xplore, ScienceDirect, ACM Digital Library), lalu tunggu saya menempel hasilnya.
4. Sajikan maksimal 5–8 kandidat dalam tabel: sitasi APA, jenis, tahun, tautan, dan **satu kalimat alasan relevansi**
   (berdasarkan apa yang benar-benar terbaca: judul/abstrak).
5. Setelah saya memilih, jalankan alur `/tambah-sumber` untuk yang saya pilih. Kandidat yang kamu rekomendasikan diberi
   `asal: rekomendasi-agent` dan `status: belum-diverifikasi`.

Aturan: jangan pernah menyatakan sebuah sumber "terverifikasi" atau "sudah dibaca" bila kamu hanya melihat metadata.
