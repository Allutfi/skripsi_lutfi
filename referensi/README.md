# referensi/ — Jurnal, Artikel, dan Sumber Pustaka

Tempat semua bahan bacaan untuk proposal. Agent membaca folder ini untuk mengutip, membandingkan,
dan mengisi tabel *Penelitian Terdahulu* **tanpa mengarang sumber**.

```
referensi/
├── daftar-sumber.md   indeks otomatis semua sumber + progres menuju target (jangan diedit manual)
├── catatan/           SATU file .md per jurnal/artikel (ringkasan kata-katamu + link/DOI)
│   └── _TEMPLATE.md   salin file ini untuk sumber baru
├── pdf/               (opsional) PDF jurnal asli yang kamu unduh
└── teks/              hasil ekstraksi otomatis dari pdf/ (dibuat oleh skrip, jangan diedit)
```

## Tiga cara memasukkan sumber
1. **Kamu punya link/DOI** → ketik `/tambah-sumber` lalu tempel link. Agent membuat file di `catatan/` dari data yang bisa ia verifikasi.
2. **Kamu punya PDF** → taruh di `pdf/`, jalankan `python scripts/ekstrak_teks.py referensi/pdf/`, lalu `/tambah-sumber` dan sebut nama filenya. Agent meringkas dari teks yang benar-benar dibaca.
3. **Minta rekomendasi** → `/cari-referensi` (sebut bab/topiknya). Agent memberi kandidat **dengan tautan**, ditandai `rekomendasi-agent` + `belum-diverifikasi`.

## Aturan penting
- Status `belum-diverifikasi` berarti **kamu belum membuka sumbernya**. Ubah ke `terverifikasi` hanya setelah kamu mencocokkan penulis, judul, tahun, jurnal, volume/halaman, dan DOI.
- Hanya sumber `terverifikasi` yang dihitung ke target (≥ 15 referensi, ≥ 60% jurnal/prosiding, ≥ 10 jurnal, ≥ 80% ≤ 10 tahun) dan masuk ke draf Daftar Pustaka.
- Ringkasan memakai **kata-katamu sendiri**. Bagian yang belum dibaca tetap `[belum dibaca]`.
- PDF jurnal sering berhak cipta. Simpan untuk pemakaian pribadi; folder `pdf/` dan `teks/` tidak ikut ke Git.

## Memperbarui indeks
```
python scripts/buat_daftar_sumber.py             # perbarui daftar-sumber.md
python scripts/buat_daftar_sumber.py --pustaka   # + draf Daftar Pustaka APA di output/
```
