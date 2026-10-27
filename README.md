# skripsi-agent — Starter Project Asisten Proposal Skripsi

Proyek ini membuat agent AI di VS Code (atau tools lain) bisa **mereview draf, memandu penyusunan bab,
mengecek format dan referensi**, lalu menghasilkan keluaran `.md`, `.docx`, dan `.pdf` ke folder `output/`.
Acuannya: *Buku Pedoman Tugas Akhir FTI ITB Widya Gama Lumajang 2026-2027*, khusus bidang
**Software Engineering → Programming**.

**Tahap aktif: Proposal (Bab 1–3).** Bab 4–5 disiapkan belakangan (lihat "Naik tahap" di bawah).

---

## 0. Panduan cepat — langkah pertama (±15 menit)

1. **Buka foldernya**: VS Code → File → Open Folder → pilih `skripsi-agent`. Buka Terminal (Ctrl+`).
2. **Pasang Python paket** (sekali saja): ikuti Bagian 2 di bawah.
3. **Ekstrak dokumen kampus** supaya agent bisa membaca PDF-nya:
   `python scripts/ekstrak_teks.py dokumen-kampus/`
4. **Isi `knowledge/konteks-penelitian.md`** (judul sementara, masalah, objek, metode, dosen pembimbing). Kosongkan yang belum tahu.
5. **Buka Chat → mode Agent**, lalu tes dengan mengetik:
   *"Baca AGENTS.md. Sebutkan tahap aktif dan tiga aturan terpenting yang kamu pegang."*
   Jika jawabannya menyebut Proposal/Bab 1–3 dan larangan mengarang referensi, berarti agent sudah memakai file-filenya.
6. **Masukkan jurnal**: ketik `/tambah-sumber` lalu tempel link/DOI (atau taruh PDF di `referensi/pdf/` dan sebut namanya).
   Perlu ide sumber? Ketik `/cari-referensi`. Setelah kamu membuka dan mencocokkan sumbernya, ubah `status:` di catatannya menjadi `terverifikasi`.
7. **Taruh draf** di `draft/`, lalu pakai `/review-bab`, `/cek-format`, `/cek-referensi`, dan seterusnya (lihat Bagian 3).
8. **Hasil** selalu ada di `output/`. Buka file-nya dari sana.

## 1. Struktur

```
skripsi-agent/
├── AGENTS.md                  aturan utama agent (dibaca otomatis oleh banyak tools)
├── CLAUDE.md                  penunjuk ke AGENTS.md (untuk Claude Code)
├── .github/
│   ├── copilot-instructions.md   instruksi otomatis GitHub Copilot di VS Code
│   └── prompts/                  perintah siap pakai (diketik dengan "/")
│       ├── review-bab · susun-outline · cek-format · cek-referensi · buat-dokumen
│       └── tambah-sumber · cari-referensi
├── knowledge/
│   ├── pedoman-ta-software-engineering-programming.md   ringkasan aturan dari pedoman
│   ├── konteks-penelitian.md                            judul, masalah, objek, metode (ISI DULU)
│   └── gaya-bahasa.md                                   preferensi gaya tulismu (isi bagian [ISI])
├── dokumen-kampus/            berkas ASLI dari kampus (.pdf/.docx) + teks/ hasil ekstraksi
├── referensi/                 jurnal & artikel
│   ├── catatan/               satu .md per sumber (ringkasan kata-katamu + link/DOI)
│   ├── pdf/  teks/            PDF jurnal asli + hasil ekstraksinya
│   └── daftar-sumber.md       indeks otomatis + progres menuju target
├── draft/                     naskahmu (.docx / .md) — agent tidak boleh menimpa
├── scripts/                   skrip Python
├── templates/                 sampul/pengesahan dari SIAKAD (opsional)
└── output/                    semua hasil agent: laporan, outline, .docx, .pdf
```

## 2. Persiapan (sekali saja)

Butuh **Python 3.10+**. Buka folder `skripsi-agent` di VS Code (**File → Open Folder**; agent hanya "melihat" isi folder yang dibuka), lalu di terminal VS Code:

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # jika diblokir: Set-ExecutionPolicy -Scope Process Bypass
pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Untuk membuat **PDF** otomatis, pasang salah satu: LibreOffice (gratis), atau Microsoft Word + `pip install docx2pdf`.
Tanpa keduanya, `.docx` tetap jadi; PDF bisa disimpan manual dari Word (File → Save As → PDF).

**Uji cepat** (memakai naskah contoh):
```
python scripts/buat_docx.py draft/_contoh-uji-pipeline.md
python scripts/cek_format.py output/_contoh-uji-pipeline.docx
```
Hasil: `output/_contoh-uji-pipeline.docx` dan `output/laporan-format-….md`. Hapus naskah contoh setelah paham alurnya.

## 3. Cara memakai bersama agent

1. Taruh drafmu di `draft/` (misal `proposal.docx` atau `proposal.md`).
2. Buka Chat di VS Code, pilih mode **Agent**.
3. Ketik `/` lalu pilih prompt, atau langsung beri perintah biasa. Contoh:
   - `/review-bab` → review Bab 1 (atau 2, 3) terhadap aspek kecukupan.
   - `/susun-outline` → kerangka dan pertanyaan pemandu per subbab.
   - `/cek-format` → cek margin, font, spasi, judul, tabel, lalu cara memperbaikinya di Word.
   - `/cek-referensi` → jumlah, % jurnal, % ≤ 10 tahun, urutan abjad, kutipan vs daftar pustaka.
   - `/buat-dokumen` → Markdown → `.docx`/`.pdf` berformat pedoman.
   - `/tambah-sumber` → masukkan jurnal/artikel (link, DOI, atau PDF) ke `referensi/catatan/`.
   - `/cari-referensi` → kandidat sumber untuk bab/topik tertentu (dengan tautan, belum diverifikasi).
   - Perintah bebas: *"Review Bab 3 di draft/proposal.docx, fokus aspek pengujian"*.
4. Agent membaca `knowledge/`, membaca drafmu, menjalankan skrip, lalu menulis hasil ke `output/`.

> Nama fitur (prompt file `.prompt.md`, `AGENTS.md`, `/create-agent`) dan sintaks `${input:…}` dapat berbeda antarversi VS Code.
> Jika `/` tidak menampilkan prompt, cek dokumentasi VS Code tentang *prompt files* dan *custom instructions* versi yang kamu pakai.
> Jika perintah slash tidak bekerja, ketik perintahnya langsung — `AGENTS.md` tetap mengarahkan agent.

**Tools lain:** Claude Code membaca `CLAUDE.md` (yang menunjuk `AGENTS.md`); Cursor, Codex, dan sejenisnya umumnya membaca `AGENTS.md`.
Jika tools-mu tidak membaca otomatis, sertakan `AGENTS.md` sebagai konteks di awal percakapan.

## 4. Skrip (jalankan dari root proyek)

| Skrip | Fungsi | Keluaran |
|---|---|---|
| `docx_ke_md.py draft/x.docx` | Mengubah Word jadi Markdown agar agent bisa membaca (agent tidak bisa membaca `.docx`) | `output/teks/x.md` |
| `cek_format.py draft/x.docx` | Kertas A4, margin 4-4-3-3, TNR 12, spasi 1,5, indentasi 0,75, judul bab/subbab, struktur judul wajib, tabel/gambar, kata tidak baku, estimasi halaman | `output/laporan-format-*.md` |
| `cek_referensi.py draft/x.docx` | ≥ 15 referensi, ≥ 60% jurnal/prosiding, ≥ 10 jurnal, ≥ 80% ≤ 10 tahun, urutan A–Z, kutipan ↔ pustaka | `output/laporan-referensi-*.md` |
| `buat_docx.py draft/x.md [--pdf]` | Markdown → `.docx` berformat pedoman (+ PDF) | `output/x.docx`, `output/x.pdf` |
| `ekstrak_teks.py <file/folder>` | PDF/DOCX → teks Markdown (dokumen kampus, jurnal) | `dokumen-kampus/teks/`, `referensi/teks/` |
| `buat_daftar_sumber.py [--pustaka]` | Indeks sumber + progres target; draf Daftar Pustaka APA dari sumber terverifikasi | `referensi/daftar-sumber.md`, `output/daftar-pustaka-draf.md` |

Opsi umum: `--tahap proposal` (default) atau `--tahap laporan`; `buat_docx.py` juga punya `--romawi`, `--judul`, `--penulis`.

**Sintaks Markdown untuk `buat_docx.py`**
```
# BAB 1 PENDAHULUAN              judul bab (mulai halaman baru)
## 1.1 Latar Belakang Masalah    subbab ( ### untuk anak subbab )
Paragraf biasa. **tebal** *miring*
- butir bullet        1. butir bernomor
Tabel 3.1 Judul Tabel            ← judul tabel di ATAS tabel
| No. | Kolom A | Kolom B |
|---|---|---|
| 1 | ... | ... |
![Gambar 3.1 Judul Gambar](gbr/diagram.png)    ← judul gambar otomatis di BAWAH gambar
# DAFTAR PUSTAKA                 entri sesudahnya: spasi 1, menjorok 1,5 cm
```

## 5. Alur yang disarankan

```
tulis draf (Word atau .md) → /cek-format & /cek-referensi → /review-bab (per bab)
→ revisi sendiri → konsultasi dosen pembimbing → /buat-dokumen → gabung sampul & pengesahan SIAKAD
```

## 6. Naik tahap: dari Proposal ke Laporan (Bab 4–5)

Setelah proposal disetujui:
1. Di `AGENTS.md` Bagian 2, ubah tahap aktif menjadi **Laporan Skripsi (Bab 1–5)**.
2. Skrip sudah punya konfigurasi `laporan` di `scripts/config.py` (spasi 2, Bab 4 ≤ 30 hlm, Bab 5 ≤ 5 hlm, total ≤ 70 hlm, judul wajib Bab 4–5). Pakai dengan `--tahap laporan`. **Konfigurasi ini belum diuji pada draf nyata**; periksa dan sesuaikan.
3. Tambahkan prompt baru di `.github/prompts/` (mis. `review-hasil-pembahasan.prompt.md`) berdasarkan Bagian 5 file pedoman (aspek kecukupan laporan: deskripsi data, analisis, penyajian hasil, pengujian dan validasi).
4. Perbarui `knowledge/` bila ada revisi pedoman. Aturan angka cukup diubah di `scripts/config.py`.

## 7. Batasan yang perlu kamu tahu

- Skrip hanya memeriksa yang **bisa diukur dari berkas .docx**. Halaman sebenarnya per bab, posisi nomor halaman, istilah miring, sampul, dan mutu isi tetap dicek manual / lewat review agent.
- `cek_referensi.py` memakai kata kunci dan pola APA, jadi klasifikasi jenis sumber dan pencocokan kutipan **heuristik**. Verifikasi sendiri tiap sumber.
- Pedoman memuat beberapa angka yang tidak seragam (jumlah/usia referensi, penomoran halaman Bab 1–5 "Romawi"). Lihat Bagian 12 file pedoman dan konfirmasi ke dosen pembimbing. Default `buat_docx.py` memakai angka Arab; gunakan `--romawi` bila pembimbing meminta angka Romawi.
- Pedoman membatasi penggunaan AI (Bab 5.5). Agent diatur untuk **membimbing**, bukan menulis seluruh bab. Kamu tetap penulis utama dan harus bisa mempertanggungjawabkan isinya.
- **Sumber ilmiah**: agent dilarang mengarang referensi (AGENTS.md Bagian 10). Rekomendasinya selalu `belum-diverifikasi` sampai kamu sendiri membuka dan mencocokkan sumbernya. Jika agent-mu tidak punya akses web, ia hanya akan memberi kata kunci pencarian.
- PDF hasil scan (gambar) tidak punya teks; `ekstrak_teks.py` akan memberi peringatan. Halaman awal pedoman (SK Rektor) memang hasil scan berkualitas rendah; Bab 1–5 terbaca baik.
- Track Changes: terima semua perubahan sebelum `docx_ke_md.py`, karena revisi yang belum diterima tidak ikut terbaca.

## 8. Pemecahan masalah

| Gejala | Solusi |
|---|---|
| `ModuleNotFoundError: docx` | Aktifkan `.venv`, lalu `pip install -r requirements.txt` |
| `python` tidak dikenali (Windows) | Coba `py` atau `py -3` sebagai ganti `python` |
| PDF tidak terbentuk | Pasang LibreOffice, atau simpan PDF manual dari Word |
| Karakter aneh di terminal | Skrip sudah memakai UTF-8; pakai Windows Terminal / VS Code terminal |
| Agent tidak melihat file | Pastikan folder `skripsi-agent` dibuka sebagai workspace |
| Agent bilang tidak bisa membaca PDF | Jalankan `python scripts/ekstrak_teks.py <folder>` lalu minta ia membaca folder `teks/` |
| Agent mencoba menulis seluruh bab | Ingatkan: "ikuti AGENTS.md Bagian 6"; minta outline dan pertanyaan pemandu |
