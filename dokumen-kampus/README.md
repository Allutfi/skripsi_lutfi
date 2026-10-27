# dokumen-kampus/ — Berkas Resmi dari Kampus

Simpan berkas asli dari kampus/prodi/fakultas di sini (format `.pdf` atau `.docx`), misalnya:
- Buku Pedoman Tugas Akhir (sudah ada)
- Panduan penulisan, SK, jadwal, formulir bimbingan, template resmi
- Contoh proposal/skripsi dari prodi

```
dokumen-kampus/
├── Pedoman_Tugas_Akhir_FTI_ITB_WIGA_2026-2027.pdf   ← berkas asli
└── teks/                                              ← hasil ekstraksi otomatis (dibaca agent)
    └── Pedoman_Tugas_Akhir_FTI_ITB_WIGA_2026-2027.md
```

Agent tidak bisa membaca PDF/DOCX langsung. Setiap menambah berkas baru, jalankan:
```
python scripts/ekstrak_teks.py dokumen-kampus/
```
Hasilnya berupa teks dengan penanda `<!-- halaman N -->` supaya aturan bisa dirujuk per halaman.

**Mana yang menjadi acuan?** Ringkasan di `knowledge/pedoman-ta-software-engineering-programming.md` dipakai untuk kerja sehari-hari.
Jika ada keraguan atau perbedaan, **berkas asli di sini yang menang**; agent diminta membuka versi teksnya di `teks/` dan menyebut halamannya.
Jika pedoman direvisi, ganti PDF-nya, jalankan ulang `ekstrak_teks.py --paksa`, lalu perbarui ringkasan di `knowledge/`.
