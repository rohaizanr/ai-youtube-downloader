#!/bin/bash

# Script to view AI debug logs

LOG_DIR="logs/ai_debug"

if [ ! -d "$LOG_DIR" ]; then
    echo "❌ No AI debug logs found. Run a search with AI enabled first."
    exit 1
fi

# Count logs
TOTAL_LOGS=$(find "$LOG_DIR" -name "*.json" | wc -l | tr -d ' ')

if [ "$TOTAL_LOGS" -eq 0 ]; then
    echo "❌ No AI debug logs found."
    exit 1
fi

echo "📊 Found $TOTAL_LOGS AI interaction log(s)"
echo ""

# Show latest logs
echo "Latest AI interactions:"
echo "─────────────────────────────────────────────────────────────"

# List files by time (newest first)
find "$LOG_DIR" -name "*.json" -type f -print0 | 
    xargs -0 ls -t | 
    head -10 | 
    while read -r file; do
        filename=$(basename "$file")
        operation=$(echo "$filename" | sed 's/ai_\(.*\)_[0-9]*.json/\1/')
        timestamp=$(echo "$filename" | sed 's/ai_.*_\([0-9]*_[0-9]*_[0-9]*\).json/\1/')
        
        # Format timestamp
        date_part=${timestamp:0:8}
        time_part=${timestamp:9:6}
        
        formatted_date="${date_part:0:4}-${date_part:4:2}-${date_part:6:2}"
        formatted_time="${time_part:0:2}:${time_part:2:2}:${time_part:4:2}"
        
        echo "📝 $operation ($formatted_date $formatted_time)"
        echo "   File: $filename"
        echo ""
    done

echo "─────────────────────────────────────────────────────────────"
echo ""
echo "To view a specific log:"
echo "  cat logs/ai_debug/<filename>"
echo ""
echo "To view the latest log with pretty formatting:"
echo "  cat \$(ls -t logs/ai_debug/*.json | head -1) | python3 -m json.tool"
echo ""
echo "To view all query enhancements:"
echo "  find logs/ai_debug -name 'ai_query_enhancement_*.json' -exec cat {} \\;"
echo ""
echo "To view all result filtering:"
echo "  find logs/ai_debug -name 'ai_result_filtering_*.json' -exec cat {} \\;"
