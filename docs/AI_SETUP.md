# 🤖 AI-Powered Search Setup Guide

## Overview

This YouTube downloader now includes **AI-powered search enhancement** using Google Gemini (or ChatGPT). The AI helps you:

- ✨ **Better understand your search intent** - AI enhances your query to find more relevant videos
- 🎯 **Filter and rank results** - AI analyzes video titles, channels, and metadata to select the best matches
- 🚀 **More accurate results** - Get videos that actually match what you're looking for

## Quick Setup (Gemini - FREE!)

### 1. Get Your Free Gemini API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key (it looks like: `AIzaSy...`)

### 2. Configure the Downloader

**Option A: Add to config file (Recommended)**

Edit `config/config.yaml`:

```yaml
# AI Integration Settings
ai_enabled: true
gemini_api_key: "YOUR_API_KEY_HERE"  # Paste your key here
```

**Option B: Use environment variable**

```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

Add to your `~/.zshrc` or `~/.bash_profile` to make it permanent:

```bash
echo 'export GEMINI_API_KEY="YOUR_API_KEY_HERE"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install AI Dependencies

```bash
# Activate your virtual environment first
source venv/bin/activate

# Install Gemini library
pip install google-generativeai
```

### 4. Test It Out!

```bash
./run_downloader.sh -q "artis malaysia takut kucing" -n 5
```

You should see:
```
✓ Gemini AI initialized successfully
🤖 AI-powered search enhancement enabled
AI enhanced query: 'artis malaysia takut kucing' → 'Malaysian celebrities scared of cats funny moments'
🤖 Using AI to analyze and rank search results...
AI selected 5 most relevant videos
```

## How It Works

### 1. **Search Query Enhancement**

**Before AI:**
```
Query: "artis celebriti malaysia takut kucing"
→ Searches YouTube exactly as typed (spelling errors, unclear intent)
```

**With AI:**
```
Query: "artis celebriti malaysia takut kucing"
→ AI understands: User wants Malaysian celebrities afraid of cats
→ Enhanced query: "Malaysian celebrities scared of cats funny moments"
→ Better YouTube results!
```

### 2. **Intelligent Result Filtering**

AI analyzes each video's:
- **Title** - Does it match the intent?
- **Channel** - Is it a quality source?
- **Duration** - Appropriate length?
- **Views** - Popular/relevant content?

Then ranks them by relevance to YOUR specific query.

## Configuration Options

Edit `config/config.yaml` to customize:

```yaml
# Enable/disable AI features
ai_enabled: true

# AI provider ("gemini" or "chatgpt")
ai_provider: "gemini"

# Your API keys
gemini_api_key: "YOUR_KEY_HERE"
openai_api_key: ""  # If using ChatGPT

# Enable specific features
ai_search_enhancement: true      # Enhance search queries
ai_result_filtering: true        # Filter and rank results
ai_max_results_to_analyze: 30    # How many results to analyze
```

## Using ChatGPT Instead

If you prefer ChatGPT (requires paid API access):

1. Get API key from: https://platform.openai.com/api-keys
2. Update config:
```yaml
ai_enabled: true
ai_provider: "chatgpt"
openai_api_key: "YOUR_OPENAI_KEY"
```
3. Install OpenAI library:
```bash
pip install openai
```

## Troubleshooting

### "Gemini API key not found"

**Solution:** Make sure you've added the key to either:
- `config/config.yaml` file, OR
- Environment variable: `export GEMINI_API_KEY="..."`

### "google-generativeai not installed"

**Solution:**
```bash
source venv/bin/activate
pip install google-generativeai
```

### "AI features disabled"

Check the logs for specific error messages:
```bash
tail -f logs/youtube_downloader_*.log
```

### Rate Limits

**Gemini Free Tier:**
- 60 requests per minute
- More than enough for typical use!

If you hit limits, you can:
- Disable AI temporarily: `ai_enabled: false`
- Reduce analysis: `ai_max_results_to_analyze: 10`

## Without AI

If you don't want to use AI, simply set:

```yaml
ai_enabled: false
```

The downloader will work perfectly fine with standard YouTube search!

## Examples

### Standard Search
```bash
./run_downloader.sh -q "kucing lucu" -n 5
# Without AI: Returns first 5 "kucing lucu" videos
```

### AI-Enhanced Search
```bash
./run_downloader.sh -q "kucing lucu" -n 5
# With AI: Analyzes results, picks 5 MOST relevant cute cat videos
```

### Complex Query
```bash
./run_downloader.sh -q "tutorial python machine learning pemula" -n 10
# AI understands: Beginner ML tutorials in Python
# Returns: Best beginner-friendly Python ML tutorials
```

## Privacy & Data

- **Gemini**: Only sends search queries and video metadata (titles, channels) to Google
- **No video content** is sent to AI
- **Your videos** stay private and local
- **API keys** are stored locally only

## Benefits

✅ **Better accuracy** - Find what you actually want  
✅ **Save time** - No manual filtering needed  
✅ **Smart ranking** - Best results first  
✅ **Free tier** - Gemini has generous free limits  
✅ **Optional** - Works great without AI too!

---

**Need help?** Check the logs or create an issue!

**API Key Resources:**
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys
