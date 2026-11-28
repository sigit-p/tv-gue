# 📺 TV-Gue — Automated Live TV & VOD M3U Playlist

Repositori ini berisi daftar saluran **Live TV** dan katalog **VOD (Film & Series)** berformat `.m3u` yang diambil, dibersihkan, dan dikelompokkan secara otomatis setiap 6 jam menggunakan **Python** dan **GitHub Actions**, lengkap dengan **Modern Web Player** berbasis GitHub Pages.

---

## 🌐 Tonton Langsung di Browser (GitHub Pages)

Buka pemutar TV & VOD online langsung melalui browser HP Android maupun Desktop tanpa instalasi aplikasi tambahan:
👉 **[https://sigit-p.github.io/tv-gue/](https://sigit-p.github.io/tv-gue/)**

### Fitur Utama Web Player:
* **Dua Pilihan Sumber Playlist:** Dapat beralih langsung antara **`Web Ready (CORS Safe)`** (`web_ready.m3u`) untuk pemutaran mulus di browser atau **`Full Playlist`** (`daftar2_full.m3u`) untuk melihat seluruh daftar.
* **🔍 Scan Kategori & Auto-Hide CORS:** Tombol pemindai paralel langsung dari browser untuk menyaring saluran mati/terblokir CORS secara *real-time*, ditambah fitur otomatis menyembunyikan saluran yang gagal diputar (dapat dipulihkan kapan saja via tombol **↺ Reset**).
* **Ramah Android & Mobile:** Pemutar video *sticky* 16:9 di bagian atas layar, navigasi kapsul geser horizontal, mode tampilan **List** & **Grid Poster** (untuk VOD), tombol **Prev/Next**, serta penyimpanan **⭐ Favorit** lokal.

---

## 🔗 Link Playlist M3U (Siap Pakai)

Salin tautan di bawah ini dan masukkan ke aplikasi pemutar IPTV favorit Anda (**OTT Navigator**, **IPTVnator**, **TiviMate**, **Kodi**, dll.):

### 1. Playlist Lengkap — Live TV + VOD (Untuk OTT Navigator / VLC / MPV)
Berisi seluruh saluran lengkap termasuk yang memakai DRM (`#KODIPROP`) maupun header khusus (`#EXTVLCOPT`):
```text
https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/daftar2_full.m3u
```

### 2. Playlist Web Ready — Bebas DRM & Lolos CORS (Untuk Browser / IPTVnator)
Sudah disaring otomatis oleh scanner Python agar kompatibel dengan pemutar berbasis web/browser:
```text
[https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/web_ready.m3u](https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/web_ready.m3u)
```

### 3. Playlist Pilihan Per Kategori (Folder `playlist/grup/`)
Jika ingin memuat kategori tertentu saja agar daftar saluran lebih ringan dan ringkas:

| Kategori | Link Raw M3U |
| :--- | :--- |
| 🎬 **VOD Film Series** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/vod_film_series.m3u` |
| 🇮🇩 **Indonesia (Nasional)** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_indonesia.m3u` |
| ⭐ **Indonesia VIP** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_indonesia_vip.m3u` |
| 🗺️ **TV Daerah** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_daerah.m3u` |
| 🕌 **Religi** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_religi.m3u` |
| ⚽ **Sports** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_sports.m3u` |
| 🏆 **beIN Sports** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_bein_sport.m3u` |
| 🎞️ **Movies** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_movies.m3u` |
| 🍿 **HBO Group** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_hbo_grub.m3u` |
| 🧸 **Kids** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_kids.m3u` |
| 📰 **News** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_news.m3u` |
| 🎭 **Entertainment** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_entertainment.m3u` |
| 🧠 **Knowledge** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_knowledge.m3u` |
| 🎵 **Music** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_music.m3u` |
| 🇲🇾 **Malaysia** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_malaysia.m3u` |
| 🇸🇬 **Singapore** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_singapore.m3u` |
| 🇰🇷 **Korea** | `https://raw.githubusercontent.com/sigit-p/tv-gue/main/playlist/grup/channel_korea.m3u` |

*(Daftar kategori lainnya seperti kategori VOD tambahan, Live Liga Inggris, UCL, LaLiga, Serie A, MotoGP, F1, Timnas, hingga Proliga tersedia lengkap di dalam folder [`playlist/grup/`](./playlist/grup)).*

---

## ⚙️ Fitur Otomatisasi

* **Penggabungan Live TV & VOD:** Mengambil siaran langsung dan katalog film/series dari beberapa sumber publik sekaligus, menyatukannya ke dalam `playlist/daftar2_full.m3u`, serta memecahnya per kategori ke folder `playlist/grup/`.
* **CORS & Compatibility Scanner:** Memindai link stream secara paralel untuk menghasilkan `playlist/web_ready.m3u` yang aman diputar di browser tanpa hambatan CORS maupun DRM.
* **Pembersihan & Standarisasi Metadata:** Mendekode karakter HTML/JSON, menghapus entri duplikat, mempertahankan direktif `#KODIPROP` (DRM) dan `#EXTVLCOPT` (User-Agent/Referer), serta membersihkan nama grup agar terbaca rapi di semua player.
* **Auto-Sync 6 Jam Sekali:** Berjalan otomatis via GitHub Actions setiap 6 jam (`0 */6 * * *`) atau dapat dipicu manual melalui tab **Actions $\rightarrow$ Run workflow**.

---

## 📁 Struktur Repositori

```text
tv-gue/
├── .github/
│   └── workflows/
│       └── update_playlist.yml   # Konfigurasi jadwal cron GitHub Actions
├── playlist/
│   ├── daftar2_full.m3u          # Playlist gabungan lengkap (Live TV + VOD)
│   ├── web_ready.m3u             # Playlist hasil filter CORS-safe untuk browser
│   └── grup/                     # Pecahan file .m3u per kategori Live TV & VOD
├── scripts/
│   └── update_m3u.py             # Skrip Python parser, scanner & pengelompok saluran
├── index.html                    # Antarmuka Modern Web Player (GitHub Pages)
└── README.md                     # Dokumentasi repositori
```

---

## 📱 Cara Penggunaan

### Di OTT Navigator (Android)
1. Buka **Pengaturan** $\rightarrow$ **Penyedia** $\rightarrow$ **Tambah Penyedia** $\rightarrow$ **Daftar Putar**.
2. Tempel URL `playlist/daftar2_full.m3u` di atas.
3. Siaran langsung akan otomatis masuk ke tab **TV Langsung**, sementara katalog VOD masuk ke tab **Film**.

### Di IPTVnator (Desktop / Web)
1. Klik **Add Playlist** $\rightarrow$ pilih **Add by URL**.
2. Gunakan URL `playlist/web_ready.m3u` jika memakai pemutar bawaan browser, atau gunakan `playlist/daftar2_full.m3u` jika sudah mengatur **Video Player** di Settings IPTVnator ke **MPV / VLC**.

### Di Chrome Android (Sebagai Web App)
1. Buka **[https://sigit-p.github.io/tv-gue/](https://sigit-p.github.io/tv-gue/)** di Chrome Android.
2. Ketuk menu **titik tiga (`⋮`)** $\rightarrow$ pilih **Tambahkan ke layar utama** (*Add to Home Screen*) untuk mengaksesnya layar penuh seperti aplikasi.

---

## 👤 Author & Copyright

* **Created & Maintained by:** **sigitpbw** ([@sigit-p](https://github.com/sigit-p))
* **Copyright:** © 2026 **sigitpbw**. All rights reserved.
* **Lisensi & Ketentuan Penggunaan:** Seluruh tautan playlist maupun stream dalam repositori ini dikumpulkan dari **sumber publik (*public sources*)** yang tersedia secara terbuka di internet. Dibagikan gratis khusus untuk keperluan pribadi dan pembelajaran — **tidak untuk diperjualbelikan (non-komersial)**.
