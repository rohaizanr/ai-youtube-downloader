#!/bin/bash
# Quick security check before publishing to GitHub

echo "🔍 Running Security Pre-Publish Check..."
echo ""

# Check for API keys in config files
echo "1. Checking for exposed API keys..."
if grep -r "AIza" config/config.yaml src/ 2>/dev/null | grep -v "^#" | grep -v ".example"; then
    echo "   ❌ DANGER: API keys found in config files!"
    echo "   DO NOT PUBLISH until these are removed!"
    exit 1
else
    echo "   ✅ No API keys found in config files"
fi

# Check if .gitignore exists
echo ""
echo "2. Checking .gitignore..."
if [ -f .gitignore ]; then
    echo "   ✅ .gitignore exists"
else
    echo "   ❌ WARNING: .gitignore missing!"
    exit 1
fi

# Check if .env is in gitignore
echo ""
echo "3. Checking if .env is ignored..."
if grep -q "^\.env$" .gitignore; then
    echo "   ✅ .env is git-ignored"
else
    echo "   ❌ WARNING: .env not in .gitignore!"
    exit 1
fi

# Check if .env.example exists
echo ""
echo "4. Checking for .env.example..."
if [ -f .env.example ]; then
    echo "   ✅ .env.example exists"
else
    echo "   ⚠️  WARNING: .env.example missing (recommended)"
fi

# Check if SECURITY.md exists
echo ""
echo "5. Checking for SECURITY.md..."
if [ -f SECURITY.md ]; then
    echo "   ✅ SECURITY.md exists"
else
    echo "   ⚠️  WARNING: SECURITY.md missing (recommended)"
fi

# Check if config.yaml has empty API keys
echo ""
echo "6. Checking config.yaml API key fields..."
if grep -q 'gemini_api_key: ""' config/config.yaml; then
    echo "   ✅ config.yaml has safe (empty) API keys"
else
    echo "   ⚠️  WARNING: config.yaml may contain API keys"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SECURITY CHECK PASSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your project is ready for GitHub publication! 🚀"
echo ""
echo "Next steps:"
echo "  1. Review: git status"
echo "  2. Commit: git commit -m 'Initial public release'"
echo "  3. Push: git push origin main"
echo ""
echo "📚 See PUBLICATION_READY.md for complete guide"
