---
description: Cari kandidat jurnal/artikel untuk bab atau topik tertentu (dengan tautan, belum diverifikasi)
---
Tugas: carikan kandidat referensi untuk **${input:topik:Topik/bab yang butuh referensi, mis. "pengujian unit pada aplikasi web untuk Bab 2.1"}**.

Pegangan: [AGENTS.md](../../AGENTS.md) Bagian 10, [daftar sumber](../../referensi/daftar-sumber.md), [konteks penelitian](../../knowledge/konteks-penelitian.md), [pedoman](../../knowledge/pedoman-ta-software-engineering-programming.md) (Bagian 4.5, 12).

Langkah:
1. Baca `referensi/daftar-sumber.md` agar tidak merekomendasikan yang sudah ada, dan lihat kekurangan terhadap target
   (jumlah, % jurnal/prosiding, jumlah jurnal, % ≤ 5 tahun).
2. **Pencarian ilmiah otomatis**: jalankan `python scripts/cari_openalex.py "<topik>" --tahun-mulai 2022 --limit 5`
   untuk mengambil metadata jurnal terindeks (5 tahun terakhir sesuai catatan pembimbing).
   Jika butuh langsung membuat draft catatan, tambahkan argumen `--buat-catatan`.
   Untuk pencarian web tambahan, buka halaman sumber dan pastikan penulis, judul, tahun, jurnal, dan **tautan/DOI** valid.
   Buang kandidat yang tidak bisa diverifikasi.
3. **Jika tidak ada koneksi**: katakan terus terang, **jangan menyebut judul/penulis dari ingatan**.
   Berikan kata kunci pencarian (Indonesia dan Inggris), operator pencarian, dan rekomendasi mesin pencari
   (Google Scholar, Garuda, SINTA, IEEE Xplore, ScienceDirect), lalu tunggu mahasiswa menempelkan hasilnya.
4. Sajikan maksimal 5–8 kandidat dalam tabel: sitasi APA, jenis, tahun, tautan, dan **satu kalimat alasan relevansi**
   (berdasarkan apa yang benar-benar terbaca: judul/abstrak).
5. Setelah saya memilih, jalankan alur `/tambah-sumber` untuk yang saya pilih. Kandidat yang kamu rekomendasikan diberi
   `asal: rekomendasi-agent` dan `status: belum-diverifikasi`.

Aturan: jangan pernah menyatakan sebuah sumber "terverifikasi" atau "sudah dibaca" bila kamu hanya melihat metadata.
