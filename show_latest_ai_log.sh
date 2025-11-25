#!/bin/bash

# Quick helper script to show the latest AI interaction with full details

LATEST_LOG=$(ls -t logs/ai_debug/*.json 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ No AI debug logs found."
    echo ""
    echo "Run a search with AI enabled to generate logs:"
    echo "  ./run_downloader.sh -q 'your search query' -n 5"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "🔍 LATEST AI INTERACTION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Parse and display the log
python3 << 'EOF'
import json
import sys
from datetime import datetime

try:
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Parse timestamp
    ts = datetime.fromisoformat(data['timestamp'])
    
    print(f"⏰ Time: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Operation: {data['operation'].replace('_', ' ').title()}")
    print(f"🤖 Provider: {data['provider'].upper()}")
    print("")
    
    if data['error']:
        print(f"❌ ERROR: {data['error']}")
    else:
        print("✅ Status: Success")
    
    print("")
    print("─" * 63)
    print("📝 PROMPT SENT TO AI:")
    print("─" * 63)
    print(data['prompt'])
    print("")
    print("─" * 63)
    print("💬 AI RESPONSE:")
    print("─" * 63)
    
    response = data['response']
    if response:
        # Try to pretty print if it's JSON
        try:
            response_json = json.loads(response)
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response)
    else:
        print("(no response)")
    
    print("")
    print("═" * 63)
    
except Exception as e:
    print(f"Error reading log: {e}")
    sys.exit(1)

EOF

python3 -c "
import json
import sys
from datetime import datetime

log_file = '$LATEST_LOG'

try:
    with open(log_file, 'r') as f:
        data = json.load(f)
    
    # Parse timestamp
    ts = datetime.fromisoformat(data['timestamp'])
    
    print(f\"⏰ Time: {ts.strftime('%Y-%m-%d %H:%M:%S')}\")
    print(f\"🔧 Operation: {data['operation'].replace('_', ' ').title()}\")
    print(f\"🤖 Provider: {data['provider'].upper()}\")
    print(\"\")
    
    if data['error']:
        print(f\"❌ ERROR: {data['error']}\")
    else:
        print(\"✅ Status: Success\")
    
    print(\"\")
    print(\"─\" * 63)
    print(\"📝 PROMPT SENT TO AI:\")
    print(\"─\" * 63)
    print(data['prompt'])
    print(\"\")
    print(\"─\" * 63)
    print(\"💬 AI RESPONSE:\")
    print(\"─\" * 63)
    
    response = data['response']
    if response:
        # Try to pretty print if it's JSON
        try:
            response_json = json.loads(response)
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response)
    else:
        print(\"(no response)\")
    
    print(\"\")
    print(\"═\" * 63)
    
except Exception as e:
    print(f\"Error reading log: {e}\")
    sys.exit(1)
"

echo ""
echo "📁 Log file: $LATEST_LOG"
echo ""
echo "To view all logs: ./view_ai_logs.sh"
