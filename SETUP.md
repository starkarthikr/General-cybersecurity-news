# Setup Guide - General Cybersecurity News Monitor

## Quick Start

This guide will help you set up the cybersecurity news monitor with proper secret management for GitHub Actions.

## Prerequisites

- Python 3.8 or higher
- GitHub account
- OpenRouter API account (free tier available)

## Step 1: Get Your OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up or log in
3. Click "Create Key"
4. Copy your API key (starts with `sk-or-v1-`)
5. **Save it securely** - you won't be able to see it again!

## Step 2: Configure GitHub Secrets

### For GitHub Actions (Automated Runs)

1. Go to your repository: `https://github.com/starkarthikr/General-cybersecurity-news`
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add the following secret:
   - **Name:** `OPENROUTER_API_KEY`
   - **Value:** Your OpenRouter API key (paste the key you copied)
6. Click **Add secret**

### Optional: GitHub Token for Issue Creation

If you want automated issue creation:

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Give it a name: "Cybersecurity News Monitor"
4. Select scopes:
   - ✓ `repo` (Full control of private repositories)
   - ✓ `workflow` (Update GitHub Action workflows)
5. Click **Generate token**
6. Copy the token
7. Add it as a repository secret:
   - **Name:** `GH_TOKEN`
   - **Value:** Your GitHub personal access token

## Step 3: Local Development Setup

### Clone the Repository

```bash
git clone https://github.com/starkarthikr/General-cybersecurity-news.git
cd General-cybersecurity-news
```

### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

**Edit `.env` and add your API key:**

```bash
# REQUIRED: Add your OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE

# Optional: GitHub token for issue creation
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_REPO=starkarthikr/General-cybersecurity-news
```

**⚠️ IMPORTANT:** Never commit the `.env` file! It's already in `.gitignore`.

## Step 4: Test Locally

```bash
# Run the monitor
python main.py

# You should see:
# ============================================================
#    🔒 CYBERSECURITY NEWS MONITOR - AI-POWERED ANALYSIS 🔒
# ============================================================
```

If you see "❌ ERROR: OPENROUTER_API_KEY environment variable is not set!", check your `.env` file.

## Step 5: Verify GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You should see your workflows listed
4. Click on any workflow to see its configuration
5. Manually trigger a test run:
   - Click on a workflow
   - Click **Run workflow** button
   - Select **main** branch
   - Click **Run workflow**

### If Workflows Are Disabled

GitHub may disable Actions for newly public repositories:

1. Go to **Settings** → **Actions** → **General**
2. Under "Actions permissions", select:
   - ✓ **Allow all actions and reusable workflows**
3. Under "Workflow permissions", select:
   - ✓ **Read and write permissions**
4. Click **Save**

## Step 6: Set Spending Limit (Required)

**Even though your repos are now public with unlimited Actions, you need to set a spending limit > $0 to enable workflows:**

1. Go to [GitHub Billing Settings](https://github.com/settings/billing/summary)
2. Click **Spending limit** under GitHub Actions
3. Change from **$0** to **$1** (or higher)
4. Add/verify payment method if prompted
5. Click **Save**

**Note:** Public repositories get unlimited free minutes, so you won't actually be charged.

## Security Checklist

- ✅ API key stored in GitHub Secrets (not in code)
- ✅ `.env` file added to `.gitignore`
- ✅ `.env.example` provided for reference
- ✅ Main code uses environment variables only
- ✅ No hardcoded credentials in any file
- ✅ `.gitignore` protects sensitive files

## Workflow Schedule

By default, workflows run:

- **Security Monitor:** Every 6 hours
- **CyberSec Monitor:** Every 8 hours  
- **Dark Reading Monitor:** Daily at 9 AM IST

To change schedules, edit the `.github/workflows/*.yml` files:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

## Troubleshooting

### "API key not set" error

```bash
# Check if environment variable is set
echo $OPENROUTER_API_KEY

# If empty, reload your environment
source .env  # Linux/Mac
# or
set -a; source .env; set +a  # Linux/Mac alternative
```

### Workflows not running

1. Check Actions are enabled: **Settings** → **Actions** → **General**
2. Check spending limit is > $0: [Billing Settings](https://github.com/settings/billing)
3. Check workflow files exist in `.github/workflows/`
4. Check secrets are configured: **Settings** → **Secrets and variables** → **Actions**

### "Rate limited" errors

OpenRouter free tier has rate limits. The code automatically:
- Retries with fallback models
- Waits between requests
- Uses multiple free models

If you consistently hit limits, consider:
- Reducing workflow frequency
- Using fewer concurrent workflows
- Upgrading to OpenRouter paid tier

### API key exposed in git history

If you accidentally committed an API key:

1. **Immediately revoke** the key at [OpenRouter](https://openrouter.ai/keys)
2. Generate a new key
3. Remove from git history:

```bash
# Install BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# Remove the exposed key
bfg --replace-text <(echo 'YOUR_EXPOSED_KEY==>***REMOVED***')

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: Rewrites history)
git push --force
```

4. Add the new key to GitHub Secrets

## Advanced Configuration

### Custom Analysis Prompts

Set via environment variable or GitHub Secret:

```bash
CUSTOM_PROMPT="Analyze the latest ransomware attacks targeting healthcare"
```

### Different AI Models

Available free models:
- `meta-llama/llama-3.2-3b-instruct:free`
- `google/gemma-2-9b-it:free`
- `mistralai/mistral-7b-instruct:free`
- `qwen/qwen-2.5-7b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

```bash
CUSTOM_MODEL="google/gemma-2-9b-it:free"
```

## Support

For issues or questions:

1. Check [SECURITY.md](SECURITY.md) for security-related issues
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
3. Open an issue on GitHub

## Security Best Practices

1. **Never commit secrets** - Use environment variables or GitHub Secrets
2. **Rotate API keys** every 30-90 days
3. **Use least privilege** - Give tokens only necessary permissions
4. **Monitor usage** - Check OpenRouter and GitHub Actions usage regularly
5. **Enable secret scanning** - GitHub's built-in secret detection
6. **Review commits** - Check diffs before pushing

---

**Ready to monitor cybersecurity news securely!** 🔒🚀
