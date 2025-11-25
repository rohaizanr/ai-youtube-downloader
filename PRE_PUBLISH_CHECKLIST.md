# Pre-Publication Checklist

Use this checklist before publishing to GitHub:

## ✅ Security Review

- [ ] Removed all API keys from `config/config.yaml`
- [ ] Created `.env` file with empty/placeholder values
- [ ] Verified `.gitignore` is properly configured
- [ ] Reviewed all code for hardcoded secrets
- [ ] Checked logs directory for sensitive information
- [ ] Ensured `downloads/` only contains example JSON, not videos

## ✅ Configuration Files

- [ ] `config/config.yaml` has no real API keys
- [ ] `config/config.yaml.example` created with safe defaults
- [ ] `.env.example` created with instructions
- [ ] `.env` file exists but is git-ignored

## ✅ Documentation

- [ ] README.md updated with security instructions
- [ ] SECURITY.md created with best practices
- [ ] AI_SETUP.md updated for secure setup
- [ ] All docs reference `.env` file, not direct config

## ✅ Dependencies

- [ ] `requirements.txt` updated to secure versions
- [ ] Ran `pip-audit` to check for vulnerabilities
- [ ] No known security issues in dependencies

## ✅ Git Hygiene

- [ ] Reviewed all staged files before commit
- [ ] No sensitive files in git history
- [ ] `.DS_Store` and system files excluded
- [ ] Virtual environment excluded

## ✅ Testing

- [ ] Tested with environment variables
- [ ] Verified API keys load from `.env`
- [ ] Confirmed application works without API keys (non-AI mode)
- [ ] Tested fresh clone in new directory

## 🚀 Ready to Publish

Once all items are checked:

```bash
# Review what will be committed
git status

# Review actual file contents
git diff

# Stage files
git add .

# Commit (review one more time!)
git commit -m "Initial public release"

# Push to GitHub
git push origin main
```

## ⚠️ Final Warning

Before pushing, double-check:
- No API keys in any file
- No personal information in logs
- No downloaded videos committed
- `.gitignore` is working correctly

Run this command to verify:
```bash
# Check for potential API keys
grep -r "AIza" . --exclude-dir=venv --exclude-dir=.git --exclude="*.md"
grep -r "sk-" . --exclude-dir=venv --exclude-dir=.git --exclude="*.md"
```

If these return ANY results in code/config files, **DO NOT PUSH!**
