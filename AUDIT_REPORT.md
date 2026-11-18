# Laporan Audit dan Perbaikan UNeed Malang

Tanggal pengerjaan: 16 Oktober 2026

## 1. Ringkasan kondisi awal

Proyek awal sudah memiliki dua aplikasi Flask terpisah, lima dataset kategori, template halaman pengguna/developer, dan komponen DSS. Namun, beberapa alur belum aman atau belum tersambung ke data aktual.

Temuan utama sebelum perbaikan:

- Login pengguna tidak membuktikan bahwa pasangan email dan kata sandi cocok dengan akun yang terdaftar.
- Kunci developer ditanam di JavaScript, dan route dashboard serta konfigurasi DSS developer tidak dibatasi oleh autentikasi.
- Secret key serta kredensial email menggunakan nilai placeholder di source code.
- Alur OTP dan reset kata sandi tidak tersambung secara utuh ke backend yang dapat menyelesaikan prosesnya.
- Pengaturan DSS belum divalidasi dan dipakai secara konsisten oleh kedua aplikasi.
- Dashboard memuat rekomendasi statis sementara sumber kategori telah tersedia sebagai CSV.
- URL kategori pada beberapa navigasi tidak konsisten, dan beberapa tombol/UI menyiratkan tindakan yang tidak diimplementasikan.
- Belum tersedia dokumentasi dependensi, konfigurasi, serta suite tes terstruktur.

## 2. Perubahan yang diterapkan

### Autentikasi dan keamanan

- Autentikasi pengguna memakai SQLite lokal; kata sandi disimpan dengan hash dari Werkzeug.
- Login memeriksa hash kata sandi dan membatasi percobaan berulang per alamat email. Setelah lima kegagalan dalam jendela 15 menit, login diblokir selama 10 menit.
- Pendaftaran memakai OTP email dengan masa berlaku 10 menit, maksimal lima percobaan verifikasi, dan jeda minimal 60 detik sebelum meminta ulang OTP untuk email yang sama.
- Reset kata sandi menggunakan token acak, menyimpan hash token, dan memberi masa berlaku satu jam.
- Form POST pada aplikasi pengguna serta konsol developer memeriksa token CSRF. Logout juga menggunakan POST.
- Penghapusan akun meminta konfirmasi kata sandi saat ini.
- Kunci developer dibaca dari `UNEED_DEV_KEY`, tidak lagi ditanam di JavaScript. Dashboard developer dan perubahan konfigurasi DSS memerlukan sesi developer yang sah.
- Secret key, SMTP, port, dan pengaturan environment dibaca dari variabel lingkungan. Mode produksi menolak berjalan jika secret key yang disyaratkan belum diatur.
- Endpoint unggah dataset melalui HTTP tetap dinonaktifkan sehingga file kategori tidak dapat ditimpa melalui route tersebut.

### Dataset dan DSS

- Loader CSV menangani UTF-8 BOM serta fallback encoding, dan mengabaikan baris kosong/footer ringkasan jika kolom `No` mengidentifikasi baris data.
- Harga, rating, koordinat, URL eksternal, dan jarak divalidasi sebelum dipakai. URL tautan hanya diterima bila skemanya HTTP atau HTTPS.
- Dashboard, kartu kategori, tabel kategori, dan halaman detail membaca baris sumber dataset, bukan rekomendasi bernama/rating statis.
- Filter harga dan pengurutan rating, harga, jarak, serta skor DSS tersambung ke backend.
- Konfigurasi Bayesian dan bobot SAW disimpan pada `instance/dss_config.json` dan dibaca oleh kedua aplikasi.
- Harga dan jarak diperlakukan sebagai kriteria cost, rating sebagai benefit, nilai normalisasi dijaga pada rentang 0–1, dan bobot yang tersedia dinormalisasi ulang untuk baris dengan nilai kriteria hilang.
- Dataset yang tidak memiliki jumlah ulasan tidak diberi jumlah ulasan buatan. Dalam kasus itu, rating yang tercatat dipakai sebagaimana dinyatakan dalam README.
- Jarak dihitung sebagai jarak garis lurus Haversine dari koordinat ke titik acuan pusat Kota Malang, bukan posisi aktual pengguna atau jarak jalan.

### UI/UX dan dokumentasi

- Tampilan dasar, komponen navigasi/sidebar/footer, pesan notifikasi, fokus keyboard, preferensi tema/font, dan aturan responsif dirapikan.
- Halaman dashboard, kategori, detail, login/register/OTP, lupa/reset kata sandi, profil, pengaturan, serta dashboard dan konfigurasi developer diperbarui.
- Menu kategori diperbaiki agar menuju route yang sesuai; duplikasi pemuatan Alpine.js dan pola login palsu pada sisi klien dihapus.
- `README.md`, `.env.example`, `requirements.txt`, `.gitignore`, dan `tests/` ditambahkan.
- Kelima file CSV asli dipertahankan byte-for-byte.

## 3. Snapshot dataset

Jumlah baris data bermakna setelah membuang baris kosong/footer, berdasarkan file yang tersedia:

| Kategori | Baris | Kolom |
|---|---:|---:|
| Kos dan kontrakan | 16 | 14 |
| Tempat makan dan warung | 20 | 13 |
| Café dan working space | 20 | 15 |
| Layanan kesehatan | 20 | 13 |
| ATK dan percetakan | 9 | 12 |
| **Total** | **85** | — |

Jumlah ini adalah jumlah baris yang terbaca di file saat audit, bukan klaim bahwa seluruh entri masih aktif atau telah diverifikasi di lapangan.

## 4. Pengujian yang benar-benar dijalankan

| Pemeriksaan | Hasil | Catatan |
|---|---|---|
| Kompilasi sintaks dua aplikasi dan file tes dengan `py_compile` | Lulus | Tidak ada syntax error Python. |
| Parsing seluruh template Jinja2 | Lulus | 16 template pengguna dan 4 template developer berhasil diparsing. |
| Pemeriksaan literal `url_for()` pada template | Lulus | Tidak ada endpoint literal yang tak ditemukan dari fungsi route. |
| Pemeriksaan form POST terhadap token CSRF di template | Lulus | Seluruh form POST yang diperiksa menyertakan token. |
| Pemeriksaan pola kunci developer/secret lama dan shortcut login | Lulus | Pola kunci lama, shortcut `localStorage`, dan log OTP lama tidak ditemukan. |
| Baca CSV dan penanganan footer/baris kosong | Lulus | Kelima file berhasil dibaca; jumlah baris tercantum di atas. |
| Perbandingan file CSV terhadap arsip awal | Lulus | Lima file CSV cocok byte-for-byte dengan sumber ZIP. |
| Suite `pytest` yang memuat tes route/integrasi | **Terhalang lingkungan** | Pengumpulan tes gagal karena modul `flask` tidak terpasang. Instalasi dependensi dicoba tetapi gagal karena jaringan/DNS tidak tersedia di lingkungan ini. Tidak ada klaim bahwa tes route/integrasi telah lulus. |
| Uji browser/responsivitas interaktif dan SMTP nyata | Belum dijalankan | Memerlukan dependensi aplikasi, browser, dan kredensial SMTP yang dapat digunakan. |

Suite pengujian disertakan di `tests/`. Jalankan `python -m pip install -r requirements.txt`, kemudian `python -m pytest -q` di lingkungan yang menyediakan akses ke paket dependensi.

## 5. Batasan dan tindakan sebelum deployment

- Konfigurasikan `.env` dengan secret acak tersendiri untuk `UNEED_SECRET_KEY`, `UNEED_DEV_SECRET_KEY`, dan `UNEED_DEV_KEY`. Jangan memakai nilai contoh.
- Pendaftaran OTP dan email reset memerlukan konfigurasi SMTP yang valid; fitur tersebut tidak dapat diverifikasi sepenuhnya tanpa akun email pengirim yang sah.
- Tidak ada akun pengguna atau kunci developer bawaan yang dikemas. Pengguna mendaftar melalui OTP setelah SMTP disiapkan.
- Konsol developer secara default hanya bind ke `127.0.0.1`. Jangan mengeksposnya ke jaringan publik tanpa kontrol akses jaringan tambahan, HTTPS, pemantauan, dan hardening operasional.
- Karena data tidak menyediakan kolom jumlah ulasan yang konsisten, pengaruh formula Bayesian terbatas pada baris yang benar-benar memiliki jumlah ulasan. Parameter tetap tersedia untuk dataset yang mendukungnya.
- Pengujian visual akhir pada lebar 360–390 px, 768 px, 1366 px, dan 1920 px tetap perlu dikonfirmasi di browser setelah dependensi dan aset CDN dapat dimuat.

## 6. Menjalankan aplikasi

Panduan instalasi lengkap, konfigurasi environment, menjalankan aplikasi pengguna pada port 5000 dan konsol developer pada port 5001, serta catatan DSS tersedia di `README.md`.


## 7. Pembaruan UI/UX setelah umpan balik pengguna

- Navigasi atas dan hamburger kini menggunakan komponen bersama pada dashboard, kategori, profil, dan pengaturan. Logo UNeed ditampilkan konsisten pada header dan diperkuat pada halaman akun/pengaturan.
- Lima kategori tidak lagi menjadi tombol horizontal di dashboard/halaman kategori; akses kategori disentralisasi ke hamburger.
- Dashboard menampilkan satu grid rekomendasi lintas kategori untuk khalayak umum, bukan lima bagian kategori yang menumpuk.
- Halaman kategori menambahkan pencarian teks yang bekerja pada backend dan dapat digabungkan dengan filter harga, sorting, serta mode kartu/tabel.
- Pengaturan tema dan ukuran teks memiliki pratinjau langsung; tombol simpan tetap menyimpan preferensi akun melalui backend. Tema gelap serta aksen warna diperluas agar terlihat pada lebih banyak komponen.
- Referensi jarak khusus kampus dihapus dari UI DSS. Titik acuan jarak kini disebut secara terbuka sebagai pusat Kota Malang, bukan lokasi pribadi pengguna.
- Pemeriksaan ulang sintaks Python dan parsing 16 template pengguna selesai tanpa kesalahan. Pengujian browser dan tes route memerlukan instalasi Flask pada lingkungan lokal dan masih perlu dijalankan di komputer pengguna.
