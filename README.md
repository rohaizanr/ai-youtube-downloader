## Apa benda ni?

Alahai, ini cuma satu skrip/alat Python yang tolong korang cari dan muat turun video YouTube dari command line. Direka untuk macOS, sesuai kalau korang nak buat automasi atau cepat-cepat grab beberapa video.

Kalau korang nak cuba cepat: jalankan `./setup.sh` sekali, aktifkan environment dan guna `./run_downloader.sh` — senang gila.

## Ciri-ciri (Ringkas)

- Carian yang pintar — boleh guna AI (optional) untuk hasil lebih relevan
- Muat turun berkumpulan (batch) dengan progress
- Elak muat turun pendua (duplicate detection)
- Simpan sejarah muat turun (JSON)
- Boleh tunjuk progress, speed, dan ETA
- Konfig boleh ubah (kualiti, format, durasi maksimum)

## Keperluan asas

- macOS
- Python 3.8+ (disyorkan)
- `ffmpeg` (boleh pasang guna Homebrew)
- Homebrew (disarankan untuk pasang ffmpeg)

## Mula cepat

1) Clone repo

```bash
git clone <your-repo-url>
cd youtube-downloader-automation
```

2) Jalankan setup (satu arahan)

```bash
./setup.sh
```

3) Aktifkan environment dan jalankan (atau guna skrip siap)

```bash
source activate_env.sh
python src/main.py   # untuk interactive
# atau
./run_downloader.sh # cara mudah
```

Contoh batch:

```bash
./run_downloader.sh -q "funny cat videos" -n 5
```

## Konfigurasi

File konfigurasi utama: `config/config.yaml`.

Beberapa pilihan penting:

- `downloads_dir`: folder simpanan (default: `downloads`)
- `video_quality`: contoh: `best[height<=720]` (hadkan kepada 720p)
- `max_duration`: dalam saat (contoh 1800 = 30 min)
- `concurrent_downloads`: berapa banyak serentak
- `log_level`: INFO / DEBUG

Edit `config/config.yaml` ikut keperluan korang.

## AI (Optional)

Kalau nak hasil carian lebih bagus, boleh guna AI (Gemini/ChatGPT). Langkah ringkas:

```bash
cp .env.example .env
# kemudian masukkan API key dalam .env (contoh: GEMINI_API_KEY=...)
```

JANGAN commit `.env` atau API keys ke git.

Rujuk `docs/AI_SETUP.md` untuk panduan penuh.

## Cara Guna (Ringkas)

- Interactive: `python src/main.py` — ikut arahan di skrin
- Batch: `python src/main.py -q "search query" -n 5` atau guna `./run_downloader.sh`

Contoh:

```bash
./run_downloader.sh -q "python tutorial" -n 3
```

Pilihan command-line utama:

```
   -q, --query      # query carian
   -n, --number     # bilangan video untuk muat turun
   -c, --config     # fail konfigurasi
   -i, --interactive
```

## Struktur projek (pendek)

`src/` - kod utama
`config/` - config.yaml
`downloads/` - tempat simpan video
`logs/` - log program
`setup.sh`, `run_downloader.sh`, `activate_env.sh` - helper scripts

## Troubleshooting cepat

- Kalau dapat error `No module named 'rich'`: aktifkan environment `source activate_env.sh` dan pasang requirements
- `ffmpeg not found`: `brew install ffmpeg`
- Muat turun perlahan: cuba kurangkan `concurrent_downloads` atau semak sambungan internet
- Video tak boleh dimainkan atau unavailable: mungkin region-restricted atau perlukan auth

Nak debug lebih mendalam? Tukar `log_level` ke `DEBUG` dalam `config/config.yaml` dan check folder `logs/`.

## Reset pemasangan

```bash
rm -rf venv
rm -f activate_env.sh run_downloader.sh
./setup.sh
```

## Etika & Undang-undang

Sila hormat hak cipta. Muat turun hanya jika anda dibenarkan. Patuh pada Terms of Service YouTube dan sokong pencipta kandungan.

## Sumbangan

Suka? Boleh buka isu (issue), hantar PR, atau cadangkan fitur. Semua dialu-alukan.

## Lesen

Projek ini bawah MIT License — lihat `LICENSE`.

## Arahan ringkas (quick cheatsheet)

```bash
# Jalankan setup
./setup.sh

# Interactive
./run_downloader.sh

# Muat turun cepat
./run_downloader.sh -q "your search" -n 5

# Tunjuk log AI terkini
./show_latest_ai_log.sh
```
