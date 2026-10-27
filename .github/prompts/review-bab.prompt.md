---
description: Review satu bab proposal skripsi (Bab 1, 2, atau 3) terhadap pedoman dan aspek kecukupan
---
Tugas: review **${input:bab:Nomor bab yang direview (1, 2, atau 3)}** dari draf **${input:file:Nama file di folder draft/, mis. proposal.docx}**.

Pegangan: [AGENTS.md](../../AGENTS.md), [pedoman](../../knowledge/pedoman-ta-software-engineering-programming.md), [gaya bahasa](../../knowledge/gaya-bahasa.md).

Langkah:
1. Baca pedoman (khusus Bagian 3.4, 4, 6, dan 7). Sebutkan bagian yang kamu pakai.
2. Jika file `.docx`, jalankan `python scripts/docx_ke_md.py draft/<file>`, lalu baca `output/teks/<nama>.md`. Jika `.md`, baca langsung.
3. Ambil hanya bab yang diminta, lalu nilai sesuai bab:
   - **Bab 1** → aspek *Kecukupan Permasalahan* (Bagian 4.1): fenomena/data bersumber, research gap, rumusan masalah jelas dan bisa dijawab, relevan dengan Informatika, batasan spesifik. Cek juga: **tujuan sejajar satu-satu dengan rumusan masalah**, manfaat teoretis dan praktis, dan batas ≤ 5 halaman.
   - **Bab 2** → *Landasan Teori* (4.3) dan *Penelitian Terdahulu*: relevansi teori dengan topik Programming, hubungan teori–variabel–metode–tujuan, tabel penelitian terdahulu dengan kolom perbedaan, dan **indikator pembeda** (metode / objek / mekanisme pengujian; Bagian 6). Batas ≤ 15 halaman.
   - **Bab 3** → *Objek* (4.2) dan *Metode Penelitian* (4.4) **plus empat aspek topik Programming** (Bagian 3.4): desain/perancangan, implementasi, pengujian terukur kuantitatif, inovasi. Cek metode pengembangan sistem, jadwal, dan batas ≤ 15 halaman.
4. Jalankan `python scripts/cek_referensi.py draft/<file>` bila bab memuat kutipan dan bagian Daftar Pustaka sudah ada; gabungkan temuannya.
   Cocokkan kutipan di bab dengan catatan di `referensi/catatan/` (AGENTS.md Bagian 10): tandai kutipan yang sumbernya belum ada atau belum terverifikasi.
5. Tulis laporan ke `output/review-bab<N>-<nama>-<YYYYMMDD>.md` dengan format di AGENTS.md Bagian 8.

Aturan: jangan menulis ulang seluruh bab. Contoh perbaikan hanya 1–2 kalimat sebagai ilustrasi.
Akhiri dengan ringkasan temuan utama di chat dan path file laporan.
