## Apa benda ni?

Alahai, ini cuma satu skrip/alat Python yang tolong korang cari dan muat turun video YouTube. Direka untuk macOS, sesuai kalau korang nak buat automasi atau cepat-cepat grab beberapa video.

**🆕 NEW: Web Interface Available!** - Sekarang ada interface web macam ChatGPT! Lagi senang guna dengan visual thumbnails, real-time progress, dan history page. Tengok `README_WEB.md` untuk details.

Kalau korang nak cuba cepat: 
- **Web Mode (Recommended)**: `./start_web.sh` — Interface web yang cantik!
- **CLI Mode (Original)**: `./run_downloader.sh` — Command line cara lama

## Ciri-ciri (Ringkas)

### Web Interface (NEW! 🎉)
- Interface ChatGPT-style yang cantik dan mudah guna
- Sidebar dengan New Chat button & conversation history
- Download history dengan video thumbnails
- Settings page untuk adjust konfig
- Real-time download progress
- Visual video selection

### CLI Mode (Original)
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

### 1) Clone repo

```bash
git clone https://github.com/rohaizanr/ai-youtube-downloader.git
cd youtube-downloader-automation
```

### 2) Setup Backend (Python)

```bash
# Jalankan setup script (install dependencies & create virtual environment)
./setup.sh

# Aktifkan virtual environment
source venv/bin/activate
```

### 3) Konfigurasi AI (Optional tapi recommended)

Edit `config/config.yaml` dan masukkan Gemini API key:
```yaml
ai_enabled: true
ai_provider: "gemini"
gemini_api_key: "YOUR_API_KEY_HERE"  # Get from https://makersuite.google.com/app/apikey
```

### 4) Pilih Mode

#### **Web Interface (RECOMMENDED 🌟)**

```bash
# Setup frontend (first time only)
cd frontend
npm install
cd ..

# Start both backend and frontend
./start_web.sh
```

Kemudian buka browser: **http://localhost:3000**

Atau start manually:

```bash
# Terminal 1: Start backend
source venv/bin/activate
cd src
python app.py  # Backend runs on http://localhost:5001

# Terminal 2: Start frontend
cd frontend
npm start  # Frontend runs on http://localhost:3000
```

#### **CLI Mode (Original)**

```bash
# Activate environment
source venv/bin/activate

# Interactive mode
python src/main.py

# Batch mode
python src/main.py -q "funny cat videos" -n 5
```

Atau guna shortcut script:

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

### Backend Issues
- **`No module named 'rich'`**: Run `source venv/bin/activate` dan `pip install -r requirements.txt`
- **`ffmpeg not found`**: Install with `brew install ffmpeg`
- **Port 5001 already in use**: Kill process with `lsof -ti:5001 | xargs kill -9`
- **AI not working**: Check `config/config.yaml` has valid `gemini_api_key` and `ai_enabled: true`
- **No videos found in web UI**: Make sure backend has config file - check backend logs for AI initialization messages

### Frontend Issues
- **Port 3000 already in use**: Kill process with `lsof -ti:3000 | xargs kill -9`
- **Connection errors**: Ensure backend is running on http://localhost:5001
- **Timeout errors**: Search taking too long - check backend logs and AI API status
- **Thumbnails not showing**: Clear browser cache or check network tab for errors

### General
- **Download slow**: Reduce `concurrent_downloads` in config or check internet connection
- **Video unavailable**: May be region-restricted or require authentication
- **Web UI shows no results but CLI works**: Backend not loading config properly - restart with `cd src && python app.py`

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
# Setup (once only)
./setup.sh

# Interactive
./run_downloader.sh

# Muat turun cepat
./run_downloader.sh -q "your search" -n 5

# Tunjuk log AI terkini
./show_latest_ai_log.sh
```
