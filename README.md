# 📺 TV-Gue — Automated IPTV M3U Playlist

Repositori ini berisi daftar saluran IPTV berformat `.m3u` yang diperbarui, dibersihkan, dan dikelompokkan secara otomatis setiap 6 jam menggunakan **Python** dan **GitHub Actions**.

---

## 🔗 Link Playlist (Siap Pakai)

Salin tautan di bawah ini dan masukkan ke aplikasi pemutar IPTV favorit Anda (**OTT Navigator**, **IPTVnator**, **TiviMate**, **Kodi**, dll.):

### 1. Playlist Lengkap (Semua Kategori dalam 1 File)
Cocok untuk **OTT Navigator** maupun **IPTVnator** (sudah dilengkapi atribut `group-title` dan `#EXTGRP`):
```text
[https://raw.githubusercontent.com/sigit-p/tv-gue/main/daftar2_full.m3u](https://raw.githubusercontent.com/sigit-p/tv-gue/main/daftar2_full.m3u)
```

### 2. Playlist Pilihan Per Kategori (Folder `grup/`)
Jika ingin memuat kategori tertentu saja agar daftar saluran lebih ringan dan ringkas di **IPTVnator**:

| Kategori | Link Raw M3U |
| :--- | :--- |
| 🇮🇩 **Indonesia (Nasional)** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_indonesia.m3u` |
| ⭐ **Indonesia VIP** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_indonesia_vip.m3u` |
| 🗺️ **TV Daerah** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_daerah.m3u` |
| 🕌 **Religi** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_religi.m3u` |
| ⚽ **Sports** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_sports.m3u` |
| 🏆 **beIN Sports** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_bein_sport.m3u` |
| 🎬 **Movies** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_movies.m3u` |
| 🎞️ **HBO Group** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_hbo_grub.m3u` |
| 🧸 **Kids** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_kids.m3u` |
| 📰 **News** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_news.m3u` |
| 🎭 **Entertainment** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_entertainment.m3u` |
| 🧠 **Knowledge** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_knowledge.m3u` |
| 🎵 **Music** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_music.m3u` |
| 🇲🇾 **Malaysia** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_malaysia.m3u` |
| 🇸🇬 **Singapore** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_singapore.m3u` |
| 🇰🇷 **Korea** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/grup/channel_korea.m3u` |

*(Daftar kategori lainnya seperti Live Liga Inggris, UCL, LaLiga, Serie A, MotoGP, F1, Timnas, hingga Proliga tersedia lengkap di dalam folder [`grup/`](./grup)).*

---

## ⚙️ Fitur Otomatisasi

* **Ekstraksi & Pembersihan Otomatis:** Mengekstrak blok `#EXTM3U` mentah, mendekode karakter HTML/JSON, serta menghapus entri duplikat.
* **Standarisasi Metadata:** Mempertahankan direktif `#KODIPROP` (DRM ClearKey/Widevine) dan `#EXTVLCOPT` (User-Agent/Referer) serta memastikan setiap saluran memiliki `group-title` dan `#EXTGRP`.
* **Auto-Sync 6 Jam Sekali:** Berjalan otomatis via GitHub Actions setiap 6 jam (`0 */6 * * *`) atau dapat dipicu manual melalui tab **Actions $\rightarrow$ Run workflow**.

---

## 📁 Struktur Repositori

```text
tv-gue/
├── .github/
│   └── workflows/
│       └── update_playlist.yml   # Konfigurasi jadwal cron GitHub Actions
├── grup/                         # Pecahan file .m3u per kategori saluran
├── daftar2_full.m3u              # Playlist gabungan seluruh saluran
├── update_m3u.py                 # Skrip Python parser & pengelompok saluran
└── README.md                     # Dokumentasi repositori
```

---

## 📱 Cara Penggunaan

### Di OTT Navigator (Android)
1. Buka **Pengaturan** $\rightarrow$ **Penyedia** $\rightarrow$ **Tambah Penyedia** $\rightarrow$ **Daftar Putar**.
2. Tempel URL `daftar2_full.m3u` di atas.
3. Aktifkan pembaruan otomatis playlist agar saluran selalu sinkron dengan pembaruan dari GitHub.

### Di IPTVnator (Desktop / Web)
1. Klik **Add Playlist** $\rightarrow$ pilih **Add by URL**.
2. Tempel URL `daftar2_full.m3u` (untuk melihat semua grup di panel kiri) atau pilih salah satu URL dari folder `grup/` di atas.
3. Gunakan tombol **Refresh** pada daftar playlist kapan saja untuk menarik pembaruan terbaru.
