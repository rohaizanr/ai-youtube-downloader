# YouTube Downloader Automation

A powerful Python application for macOS that allows you to search and download YouTube videos based on search queries. Built with modern libraries and featuring a rich command-line interface.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🤖 AI-Powered Intelligence
- **AI-Powered Search**: Use Gemini or ChatGPT to find the most relevant videos
- **Intelligent Filtering**: AI analyzes and ranks results based on your intent
- **Natural Language Processing**: Works with Bahasa Malaysia, English, and more
- **Intent Understanding**: AI understands what you want, not just keywords
- **Debug Logging**: Complete visibility into AI decision-making

### � Download Features
- **Smart Search**: Search YouTube with any query and get relevant results
- **Batch Downloads**: Download multiple videos at once with progress tracking
- **Duplicate Detection**: Automatically skip already downloaded videos
- **Format Support**: Download in MP4 format with automatic quality selection
- **Progress Tracking**: Real-time download progress with speed and ETA
- **Resume Support**: Built-in retry mechanism for failed downloads
- **Download History**: Complete tracking of all downloaded videos

### ⚙️ Customization & Control
- **Configurable Settings**: Customize quality, format, duration limits, and more
- **Interactive Mode**: User-friendly CLI with rich formatting and progress bars
- **Batch Mode**: Command-line operation for automation and scripting
- **Quality Control**: Set maximum video quality (default: 720p)
- **Duration Limits**: Filter by maximum video length (default: 30 minutes)
- **Concurrent Downloads**: Control parallel download processes

### 🔧 Developer-Friendly
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Error Handling**: Graceful error recovery and user-friendly messages
- **Automated Setup**: One-command installation and configuration
- **Cross-Platform**: Optimized for macOS with Python 3.8+

## 🛠 Prerequisites

- **macOS** (tested on macOS 10.15+)
- **Python 3.8 or higher**
- **ffmpeg** (automatically installed via Homebrew)
- **Homebrew** (recommended for easy ffmpeg installation)

## � Security First

Before publishing or using this project:

1. **Never commit API keys** - Use `.env` file for sensitive data
2. **Review `.gitignore`** - Ensures sensitive files are excluded
3. **Check configuration** - Use `config.yaml.example` as template
4. **Read [SECURITY.md](SECURITY.md)** - Full security guidelines and best practices

## �🚀 Quick Start

### 1. Clone or Download

```bash
git clone <your-repo-url>
cd youtube-downloader-automation
```

Or download and extract the ZIP file to your desired location.

### 2. Run Setup

The setup script will handle everything automatically:

```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all required dependencies
- Install ffmpeg (if not present)
- Create necessary directories
- Set up activation scripts

### 3. Start Using

**Interactive Mode:**
```bash
# Activate the environment
source activate_env.sh

# Run the application
python src/main.py
```

**Or use the convenience script:**
```bash
./run_downloader.sh
```

**Batch Mode:**
```bash
./run_downloader.sh -q "funny cat videos" -n 5
```

## 🤖 AI-Powered Search (Optional)

Want more accurate search results? Enable AI-powered search enhancement!

**Quick Setup:**
1. Get free API key: https://makersuite.google.com/app/apikey
2. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```
3. Add your API key to `.env`:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```
4. Done! 🎉

**🔒 Security Note:** Never commit API keys to git! Use the `.env` file (git-ignored).

**📚 Full Guide:** See [docs/AI_SETUP.md](docs/AI_SETUP.md) for detailed instructions.

## 📖 Usage Guide

### Interactive Mode

When you run the application without arguments, it starts in interactive mode:

```bash
python src/main.py
```

Follow the prompts to:
1. Enter your search query (e.g., "python tutorials")
2. Specify how many videos to download
3. Review search results
4. Select videos to download
5. Confirm and start downloading

### Batch Mode

For automated or scripted usage:

```bash
# Basic usage
python src/main.py -q "search query" -n 5

# With custom config
python src/main.py -q "python tutorials" -n 3 -c config/custom.yaml

# Examples
python src/main.py -q "cooking recipes" -n 10
python src/main.py -q "guitar lessons" -n 5
python src/main.py -q "funny cats" -n 3
```

### Command Line Options

```
usage: main.py [-h] [-q QUERY] [-n NUMBER] [-c CONFIG] [-i] [--version]

YouTube Downloader Automation - Search and download YouTube videos

optional arguments:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        Search query for YouTube videos
  -n NUMBER, --number NUMBER
                        Number of videos to download (default: 5)
  -c CONFIG, --config CONFIG
                        Path to configuration file
  -i, --interactive     Run in interactive mode (default if no query provided)
  --version             show program's version number and exit
```

## ⚙️ Configuration

The application uses a YAML configuration file located at `config/config.yaml`. You can customize various settings:

```yaml
# Download settings
downloads_dir: "downloads"
video_quality: "best[height<=720]"  # 720p max quality
max_duration: 1800  # 30 minutes max
output_format: "mp4"

# Application settings
log_level: "INFO"
concurrent_downloads: 3

# Search settings
search_max_results: 50
filter_by_duration: true
```

### Key Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `downloads_dir` | Directory for downloaded videos | `downloads` |
| `video_quality` | Video quality preference | `best[height<=720]` |
| `max_duration` | Maximum video length (seconds) | `1800` (30 min) |
| `output_format` | Preferred output format | `mp4` |
| `log_level` | Logging verbosity | `INFO` |
| `concurrent_downloads` | Parallel downloads | `3` |

## 📁 Project Structure

```
youtube-downloader-automation/
├── src/
│   ├── main.py                 # CLI interface
│   └── youtube_downloader.py   # Core functionality
├── config/
│   └── config.yaml            # Configuration file
├── downloads/                 # Downloaded videos (created automatically)
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── setup.sh                   # macOS setup script
├── activate_env.sh           # Environment activation (created by setup)
├── run_downloader.sh         # Convenience run script (created by setup)
└── README.md                 # This file
```

## 🔧 Manual Installation

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install ffmpeg

**Via Homebrew (recommended):**
```bash
brew install ffmpeg
```

**Via MacPorts:**
```bash
sudo port install ffmpeg
```

**Manual installation:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## 📋 Dependencies

The application uses the following key libraries:

- **yt-dlp**: Modern YouTube downloading library
- **youtube-search-python**: YouTube search functionality  
- **rich**: Beautiful terminal output and progress bars
- **pyyaml**: Configuration file handling
- **requests**: HTTP requests
- **colorlog**: Colored logging output

See `requirements.txt` for the complete list with version numbers.

## 🎯 Examples

### Search and Download Tutorials

```bash
./run_downloader.sh -q "python programming tutorial" -n 5
```

### Download Music Videos

```bash
./run_downloader.sh -q "best music 2023" -n 10
```

### Interactive Session for Cooking Videos

```bash
./run_downloader.sh
# Then enter: "easy cooking recipes"
# Select: 3 videos
```

## 📊 Output and Logs

### Download Location

Videos are saved to the `downloads/` directory by default. Each video is saved with a sanitized filename based on its title.

### Logging

Logs are saved in the `logs/` directory with daily rotation:
- `logs/youtube_downloader_YYYYMMDD.log`

Log levels available: DEBUG, INFO, WARNING, ERROR

### Download History

The application maintains a download history in JSON format in the downloads directory, tracking:
- Video title and URL
- Download timestamp
- Local file path

## 🔍 Troubleshooting

### Common Issues

#### "No module named 'rich'" or similar import errors
- **Solution**: Make sure you activated the virtual environment: `source activate_env.sh`

#### "ffmpeg not found" errors
- **Solution**: Install ffmpeg via Homebrew: `brew install ffmpeg`

#### Downloads are very slow
- **Solution**: Try reducing `concurrent_downloads` in config.yaml or check your internet connection

#### "Video unavailable" errors
- **Solution**: Some videos may be region-restricted or require authentication. Try different search terms.

#### Python version errors
- **Solution**: Ensure you have Python 3.8+ installed: `python3 --version`

### Debug Mode

For detailed troubleshooting, edit `config/config.yaml`:

```yaml
log_level: "DEBUG"
```

Then check the logs in the `logs/` directory for detailed information.

### Reset Installation

If you encounter persistent issues:

```bash
# Remove virtual environment
rm -rf venv

# Remove generated scripts
rm -f activate_env.sh run_downloader.sh

# Run setup again
./setup.sh
```

## 🛡 Legal and Ethical Considerations

- **Respect Copyright**: Only download videos you have the right to download
- **Terms of Service**: Ensure your usage complies with YouTube's Terms of Service
- **Personal Use**: This tool is intended for personal, educational, or fair use purposes
- **Content Creator Rights**: Consider supporting content creators through official channels

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Report bugs
2. Suggest new features
3. Submit pull requests
4. Improve documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Quick Reference

### Common Commands
```bash
# Interactive mode
./run_downloader.sh

# Quick download
./run_downloader.sh -q "your search query" -n 5

# Skip duplicates (default)
./run_downloader.sh -q "python tips" -n 3

# Include already downloaded videos
./run_downloader.sh -q "python tips" -n 3 --include-downloaded

# View AI debug logs
./show_latest_ai_log.sh
./view_ai_logs.sh
```

### Helper Scripts
- `./setup.sh` - Initial setup and installation
- `./run_downloader.sh` - Run the downloader
- `./activate_env.sh` - Activate virtual environment
- `./show_latest_ai_log.sh` - View latest AI interaction
- `./view_ai_logs.sh` - Overview of all AI logs
- `./test_installation.py` - Test your installation

## �📚 Documentation

### Core Documentation
- **[AI Setup Guide](docs/AI_SETUP.md)** - Complete guide for setting up AI features (Gemini/ChatGPT)
- **[AI Debug Logging](docs/AI_DEBUG_LOGS.md)** - Debug logging guide for AI interactions
- **[Configuration Reference](config/config.yaml)** - All configuration options

### Feature Guides
- **[Success Story](docs/SUCCESS.md)** - Quick start guide and first-time setup walkthrough
- **[Duplicate Detection](docs/DUPLICATE_DETECTION.md)** - How the duplicate detection feature works
- **[AI Returns URLs](docs/AI_RETURNS_URLS.md)** - Understanding how AI returns video URLs

### Technical Resources
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Complete project overview and architecture

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful YouTube downloading library
- [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) - YouTube search API
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [FFmpeg](https://ffmpeg.org/) - Video processing capabilities
- [Google Gemini](https://ai.google.dev/) - AI-powered search enhancement

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the logs in the `logs/` directory
3. Ensure all dependencies are correctly installed
4. Try running the setup script again

---

**Happy downloading! 🎥✨**