# Laporan Implementasi UNeed Personal Project

**Tanggal:** 27 Oktober 2026  
**Basis implementasi:** `UNeed-Project(2).zip` yang diunggah pada percakapan ini, dipertahankan dengan arsitektur yang sudah tersedia.  
**Status:** fitur baru telah ditambahkan dan diuji secara terarah; beberapa tes warisan masih perlu diselaraskan dengan API aplikasi SQLite saat ini.

## 1. Arsitektur dan perlindungan data

Implementasi mempertahankan dua aplikasi Flask:

- **Website pengguna:** `website_user/app_user.py` (default `http://127.0.0.1:5000/`).
- **Konsol pengelola:** `website_dev/app_dev.py` (default `http://127.0.0.1:5001/dev/login`).
- **Komponen bersama:** `shared/` untuk katalog, DSS, validasi lokasi, membership, dan skema komunitas.
- **Dataset:** lima file CSV di `website_user/uploads_excel/`.
- **Database pengguna:** SQLite di `website_user/instance/uneed_users.sqlite3` sesuai konfigurasi.
- **Konfigurasi DSS:** tetap berbagi konfigurasi yang ada; konfigurasi membership ditambahkan secara terpisah.

Tidak ada migrasi framework. Perubahan skema menggunakan `CREATE TABLE IF NOT EXISTS` dan penambahan kolom yang belum tersedia. Tabel lama tidak dihapus oleh migrasi ini. Dalam paket hasil, database sumber dan lima CSV dipertahankan tanpa perubahan isi; folder virtual environment, cache, `.env`, dan kredensial tidak dibundel. Saat aplikasi dijalankan, skema tambahan akan dibuat secara aditif.

## 2. Fitur yang dipertahankan

- Autentikasi, profil, pengaturan, OTP/reset password, dan pembatasan akses yang telah tersedia.
- Katalog lima kategori: kos, warung/tempat makan, café/working space, klinik, dan ATK/percetakan.
- Pencarian, filter kategori, detail tempat, pengajuan data, dashboard pengelola, maintenance, dan konfigurasi DSS.
- Flask, Jinja2, Tailwind CSS dari CDN, Alpine.js, SQLite, serta file dataset yang sudah ada.
- SAW dan Bayesian Average Rating yang telah menjadi bagian identitas matematis proyek.

## 3. Lokasi aktual, jarak, DSS, dan Google Maps

- Tombol **Gunakan Lokasi Saya** meminta izin eksplisit melalui Geolocation API. **Perbarui Lokasi** meminta pembacaan baru; **Ikuti Lokasi Saya** hanya memulai `watchPosition()` setelah pengguna mengaktifkannya dan dihentikan saat dinonaktifkan atau halaman ditinggalkan.
- Jarak garis lurus memakai Haversine dengan radius rata-rata Bumi sekitar 6.371 km. Pilihan radius 1/3/5/10 km atau semua hasil digunakan untuk memfilter hasil. Pengurutan terdekat dibuat dari jarak numerik aktual; tempat tanpa koordinat valid tidak diberi jarak rekaan.
- Koordinat baru dikirim hanya ketika pengguna meminta lokasi dan aplikasi perlu menghitung ulang skor DSS. Pengiriman dilakukan melalui endpoint POST `/api/location-dss`, divalidasi, dilindungi CSRF, dan diberi header `no-store`. Koordinat tidak disimpan sebagai profil pengguna, session, URL, atau log aktivitas.
- Endpoint menghitung ulang data jarak serta skor DSS/SAW menggunakan posisi perangkat saat ini. Saat lokasi belum diberikan, algoritma tidak memakai pusat kota/kampus sebagai lokasi pengguna; kriteria jarak tidak boleh dianggap sebagai jarak aktual.
- Kartu dan halaman detail menggunakan tautan **Lihat/Buka di Google Maps** dan **Petunjuk Arah** apabila nama, alamat, atau koordinat tujuan valid. Navigasi rute diserahkan ke Google Maps; angka Haversine bukan jarak jalan maupun estimasi durasi perjalanan.
- Peta interaktif tersedia secara opsional melalui Leaflet + OpenStreetMap, aktifkan dengan `UNEED_ENABLE_INTERACTIVE_MAP=true`. Tanpa konfigurasi tersebut, website tidak menampilkan peta palsu; fitur pencarian dan tautan Google Maps tetap dapat digunakan.
- Geolocation produksi membutuhkan HTTPS atau konteks aman seperti localhost. Data lokasi dan ketersediaan tempat masih bergantung pada data katalog yang ada, yang wilayahnya belum nasional.

## 4. DSS dan kredibilitas rating

- SAW tetap memakai kriteria yang terkonfigurasi dan memperlakukan harga/jarak sebagai cost serta rating sebagai benefit sesuai konfigurasi DSS proyek.
- Perubahan lokasi memicu penghitungan jarak dan skor ulang, sementara skor organik tidak dinaikkan oleh tier atau pembayaran membership.
- Bayesian Average Rating menggunakan jumlah ulasan apabila memang tersedia. Jika jumlah ulasan tidak ada pada sumber, sistem tidak mengarang jumlah review.
- Hasil merupakan alat bantu keputusan berdasarkan data yang tersedia, bukan jaminan bahwa satu tempat terbaik bagi semua pengguna.

## 5. Rekomendasi komunitas dan moderasi

- Anggota dapat membuat rekomendasi yang dikaitkan dengan salah satu dari lima kategori. Pengajuan berstatus `pending` dan tidak ditampilkan sebagai rekomendasi yang telah disetujui sampai dimoderasi.
- Feed menampilkan rekomendasi yang telah disetujui; pengguna dapat menandai rekomendasi membantu, menyimpan rekomendasi, atau melaporkan informasi keliru/duplikat/spam. Batasan database mencegah pengguna memberi vote atau laporan berulang pada rekomendasi yang sama.
- Kontributor ditampilkan menggunakan identitas publik/pseudonim pada area komunitas.
- Konsol pengelola memiliki antrean moderasi rekomendasi dan laporan. Persetujuan mengeluarkan poin melalui ledger satu kali, bukan berdasarkan submit berulang.
- Penyimpanan tempat dan rekomendasi komunitas tersedia tanpa alur checkout atau transaksi tempat.

## 6. Membership dan reward

- Struktur keanggotaan Basic/Premium, status, masa berlaku, manfaat yang dapat dikonfigurasi, serta riwayat perubahan membership ditambahkan. Pengelola dapat mengubah tier/status/masa berlaku secara manual melalui konsol; setiap perubahan dicatat pada tabel riwayat.
- Harga/manfaat Premium tidak ditentukan secara otomatis, dan tidak ada tombol atau gateway pembayaran palsu. Gateway berbayar belum diaktifkan karena metode pembayaran dan siklus langganan belum ditentukan.
- Program kontribusi menyimpan event poin pada ledger, menunjukkan badge/leaderboard per periode mingguan, bulanan, atau keseluruhan sesuai konfigurasi. Poin dan penyesuaian administrator dapat diaudit.
- Konsol dapat mencatat penghargaan per anggota/periode, mengubah status penghargaan, dan menyimpan riwayat perubahan status. Constraint unik mencegah pemberian penghargaan dengan kombinasi anggota/periode/jenis yang sama secara berulang.
- Model pendapatan yang direncanakan hanya membership. Tidak ada komisi, pemesanan, checkout, atau banner iklan sebagai sumber pendapatan produk.

## 7. Perubahan file utama

- `shared/location.py`: validasi koordinat, Haversine, URL pencarian serta petunjuk arah Google Maps.
- `shared/community_schema.py`: migrasi aditif untuk komunitas, suara/laporan, koleksi, ledger poin, riwayat membership, penghargaan, dan audit penghargaan.
- `shared/membership.py`: konfigurasi membership dan periode leaderboard.
- `website_user/app_user.py`: jarak berbasis origin eksplisit, endpoint `/api/location-dss`, komunitas, penyimpanan, membership, reward/leaderboard.
- `website_user/static/js/geolocation.js`: alur GPS, radius, urutkan jarak, lokasi opsional pada peta, dan penghitungan ulang DSS saat lokasi diberikan.
- `website_user/templates/`: kontrol lokasi, penjelasan jarak, link Maps/petunjuk arah, halaman komunitas/membership/daftar pilihan; label “Keranjang” diperjelas menjadi “Daftar Pilihan”.
- `website_dev/app_dev.py`: moderasi komunitas, konfigurasi dan pengelolaan membership, penghargaan, serta koreksi poin dengan audit.
- `website_dev/templates/`: navigasi konsol dan halaman reward/membership.
- `tests/test_location_membership_features.py`, `tests/test_community_routes.py`, `tests/test_app_logic.py`: pengujian fitur baru dan penyesuaian uji lokasi yang sebelumnya mengasumsikan titik tetap.
- `README.md`, `IMPLEMENTATION_REPORT.md`: cara menjalankan, konfigurasi, privasi, fitur dan keterbatasan.

## 8. Pengujian aktual

Pada lingkungan verifikasi saat ini:

- **26 pengujian lulus** pada `tests/test_app_logic.py`, `tests/test_location_membership_features.py`, dan `tests/test_community_routes.py`. Secara terpisah, **26 pengujian lulus** pada `tests/test_kos_redesign.py` dan `tests/test_catalog_dss.py`.
- Python `compileall` dan pemeriksaan sintaks JavaScript `node --check website_user/static/js/geolocation.js` lulus.
- Migrasi diuji terhadap salinan database: akun dan pengajuan lama tetap ada, dan tabel fitur baru ditambahkan. Database sumber dalam paket tetap dipertahankan.
- **Suite lengkap belum hijau:** `python -m pytest -q` menghasilkan `52 passed, 22 failed`. Kegagalan tersebut berasal dari `tests/test_user_app.py` dan `tests/test_dev_app.py` yang memanggil atribut/penyimpanan lama (`M.PENDING`, `M._attempts`, `USERS_FILE`, `REVIEWS_FILE`) dari arsitektur JSON yang berbeda dari source saat ini yang menggunakan SQLite dan sesi Flask. Tes tersebut tidak dihapus; penyelarasannya perlu dikerjakan terpisah agar tidak mengubah ekspektasi keamanan secara sembarangan.
- Pengujian tersebut bukan pengganti pengujian browser end-to-end: GPS pada perangkat nyata, persetujuan lokasi lintas browser, tampilan ponsel, SMTP nyata, dan navigasi eksternal Google Maps belum diverifikasi langsung dalam sesi ini.

## 9. Menjalankan aplikasi

Dari folder root proyek:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Salin `.env.example` ke `.env`, lalu ganti semua secret/kunci dengan nilai lokal yang acak. Jangan membagikan `.env`. Jalankan dua aplikasi pada terminal terpisah:

```bash
python website_user/app_user.py
python website_dev/app_dev.py
```

Website pengguna default di `http://127.0.0.1:5000/`; konsol pengelola di `http://127.0.0.1:5001/dev/login`. Untuk peta interaktif, tetapkan `UNEED_ENABLE_INTERACTIVE_MAP=true`. Penggunaan lokasi di deployment membutuhkan HTTPS. Jangan membuka konsol pengelola ke jaringan publik tanpa konfigurasi autentikasi dan jaringan yang sesuai.

## 10. Keterbatasan dan tindak lanjut

1. Wilayah hasil tetap terbatas pada katalog yang tersedia. Perlu validasi berkala terhadap alamat/koordinat serta penambahan dataset yang sah, bukan pengisian data contoh.
2. Tidak ada integrasi pembayaran membership aktif; keputusan harga, manfaat premium, siklus langganan, dan metode pembayaran harus dibuat sebelum mengembangkan gateway.
3. Upload foto kontribusi, moderasi konten gambar, dan integrasi peta berbasis Google Maps JavaScript API belum diaktifkan. Peta opsional saat ini menggunakan Leaflet/OpenStreetMap.
4. Perlu menyelaraskan 22 tes lama yang mengacu ke API JSON versi berbeda, lalu menjalankan suite penuh hingga hijau.
5. Perlu pengujian browser/perangkat nyata, aksesibilitas, performa, dan validasi konfigurasi deployment sebelum dipublikasikan.
