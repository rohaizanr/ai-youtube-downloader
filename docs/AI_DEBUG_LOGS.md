# 🔍 AI Debug Logging Guide

## Overview

The YouTube downloader now logs **all AI interactions** to JSON files for debugging and analysis. This helps you understand:

- 📝 What prompts are sent to Gemini/ChatGPT
- 💬 What responses come back from the AI
- 🐛 Any errors that occur during AI processing
- ⏱️ When each interaction happened

## Debug Log Location

All AI debug logs are saved in:
```
logs/ai_debug/
```

Each interaction creates a separate JSON file with timestamp.

## Log File Naming

Debug logs use this naming pattern:
```
ai_<operation_type>_<timestamp>.json
```

**Operation Types:**
- `query_enhancement` - AI optimizing your search query
- `result_filtering` - AI analyzing and ranking video results

**Example filenames:**
```
ai_query_enhancement_20251125_020810_582799.json
ai_result_filtering_20251125_020815_123456.json
```

## Log File Structure

Each log file contains:

```json
{
  "timestamp": "2025-11-25T02:08:10.582811",
  "operation": "query_enhancement",
  "provider": "gemini",
  "prompt": "You are a YouTube search expert...",
  "response": "artis malaysia takut kucing",
  "error": null
}
```

**Fields:**
- `timestamp` - ISO format timestamp
- `operation` - Type of AI operation
- `provider` - AI provider used ("gemini" or "chatgpt")
- `prompt` - Full prompt sent to AI
- `response` - AI's response text
- `error` - Error message if operation failed (null if successful)

## Viewing Logs

### Quick View Script

Use the provided helper script:
```bash
./view_ai_logs.sh
```

This shows:
- Total number of logs
- List of recent interactions
- Helpful commands for viewing logs

### Manual Commands

**View latest log (pretty formatted):**
```bash
cat $(ls -t logs/ai_debug/*.json | head -1) | python3 -m json.tool
```

**View all query enhancement logs:**
```bash
find logs/ai_debug -name 'ai_query_enhancement_*.json' -exec cat {} \;
```

**View all result filtering logs:**
```bash
find logs/ai_debug -name 'ai_result_filtering_*.json' -exec cat {} \;
```

**Count total interactions:**
```bash
find logs/ai_debug -name '*.json' | wc -l
```

**Search logs for specific text:**
```bash
grep -r "takut kucing" logs/ai_debug/
```

## Use Cases

### 1. Understanding Query Transformation

**See how AI transforms your natural language:**

```bash
# Run a search
./run_downloader.sh -q "saya nak video artis malaysia takut kucing" -n 3

# Check the query enhancement log
cat $(ls -t logs/ai_debug/ai_query_enhancement_*.json | head -1) | python3 -m json.tool
```

You'll see:
- **Your input:** "saya nak video artis malaysia takut kucing"
- **AI output:** "artis malaysia takut kucing"
- **The exact prompt** used to instruct the AI

### 2. Debugging Poor Results

If search results aren't good:

1. Check the query enhancement log - did AI extract the right keywords?
2. Check the result filtering log - which videos did AI select and why?
3. Review the prompt to see if it needs improvement

### 3. Analyzing AI Behavior

**Compare multiple searches:**
```bash
# Search for the same thing in different ways
./run_downloader.sh -q "artis takut kucing" -n 3
./run_downloader.sh -q "saya nak video artis yang takut kucing" -n 3
./run_downloader.sh -q "celebrities afraid of cats malaysia" -n 3

# Compare the AI responses
cat logs/ai_debug/ai_query_enhancement_*.json | grep -A1 '"response"'
```

### 4. Prompt Engineering

Use logs to improve AI prompts:

1. Run searches and collect logs
2. Analyze what works and what doesn't
3. Edit prompts in `src/ai_helper.py`
4. Test again and compare results

## Example Debugging Session

### Problem: AI not extracting good keywords

**Step 1: Run test search**
```bash
./run_downloader.sh -q "saya nak semua yang ada artis malaysia takut kucing" -n 5
```

**Step 2: Check query enhancement**
```bash
cat $(ls -t logs/ai_debug/ai_query_enhancement_*.json | head -1) | python3 -m json.tool
```

**What to look for:**
- Is the response too long/short?
- Did it keep important words?
- Did it remove the right filler words?

**Step 3: Review the prompt**
```bash
cat $(ls -t logs/ai_debug/ai_query_enhancement_*.json | head -1) | python3 -m json.tool | grep -A50 '"prompt"'
```

**Step 4: Adjust prompt if needed**
Edit `src/ai_helper.py` in the `enhance_search_query()` method.

### Problem: Wrong videos selected

**Step 1: Check result filtering log**
```bash
cat $(ls -t logs/ai_debug/ai_result_filtering_*.json | head -1) | python3 -m json.tool
```

**What to look for:**
- What videos were available?
- Which indices did AI select?
- Does the prompt give clear selection criteria?

**Step 2: Review selection criteria**
Look at the `filter_and_rank_results()` prompt in `src/ai_helper.py`.

## Log Management

### Cleaning Old Logs

**Remove logs older than 7 days:**
```bash
find logs/ai_debug -name '*.json' -mtime +7 -delete
```

**Remove all logs:**
```bash
rm -rf logs/ai_debug/*.json
```

**Keep only latest 50 logs:**
```bash
ls -t logs/ai_debug/*.json | tail -n +51 | xargs rm -f
```

### Log Size

Each log is typically:
- **Query enhancement:** ~1-2 KB
- **Result filtering:** ~5-15 KB (contains video metadata)

Expect ~10-20 KB per search (2 logs per search).

## Privacy Notes

Debug logs contain:
- ✅ Your search queries
- ✅ Video titles and metadata
- ✅ AI prompts and responses
- ❌ **NO** API keys
- ❌ **NO** video content
- ❌ **NO** personal data

Logs are stored **locally only** - never sent anywhere.

## Troubleshooting

### "No AI debug logs found"

**Cause:** AI features are disabled or not working.

**Solution:**
1. Check `config/config.yaml` - is `ai_enabled: true`?
2. Check main log: `tail -f logs/youtube_downloader_*.log`
3. Look for "Gemini AI initialized successfully"

### "Cannot read log file"

**Cause:** JSON syntax error in log file.

**Solution:**
```bash
# Validate JSON
python3 -c "import json; json.load(open('logs/ai_debug/<filename>'))"
```

### "Too many log files"

**Solution:** Clean old logs (see Log Management above).

## Integration with Main Logs

AI debug logs complement the main application log:

**Main log** (`logs/youtube_downloader_*.log`):
- Application flow
- Search/download status
- Error summaries

**AI debug logs** (`logs/ai_debug/ai_*.json`):
- Detailed AI prompts
- Full AI responses
- Structured JSON data

Use both together for complete debugging!

## Advanced: Parsing Logs Programmatically

**Python script to analyze logs:**
```python
import json
from pathlib import Path

debug_dir = Path('logs/ai_debug')

for log_file in sorted(debug_dir.glob('ai_query_enhancement_*.json')):
    with open(log_file) as f:
        data = json.load(f)
    
    print(f"Time: {data['timestamp']}")
    print(f"Input: {data['prompt'].split('User input: ')[1].split('\\n')[0]}")
    print(f"Output: {data['response']}")
    print("---")
```

## Summary

✅ **Automatic logging** - Every AI call is logged  
✅ **Structured data** - Easy to parse JSON format  
✅ **Debugging friendly** - See exactly what AI is doing  
✅ **Privacy safe** - All data stays local  
✅ **Easy cleanup** - Simple to manage old logs  

---

**Quick Commands Reference:**

```bash
# View logs overview
./view_ai_logs.sh

# Latest log (pretty)
cat $(ls -t logs/ai_debug/*.json | head -1) | python3 -m json.tool

# Find specific text
grep -r "search term" logs/ai_debug/

# Clean old logs
find logs/ai_debug -name '*.json' -mtime +7 -delete
```
