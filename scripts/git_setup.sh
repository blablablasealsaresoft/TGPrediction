#!/bin/bash
# Git setup and push script for Solana Trading Bot

echo "============================================================"
echo "GIT SETUP WIZARD"
echo "============================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "Download from: https://git-scm.com/download/win"
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Check if already a git repo
if [ -d ".git" ]; then
    echo "✓ Git repository already initialized"
else
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
fi

echo ""

# Configure git (if not configured)
if [ -z "$(git config user.name)" ]; then
    echo "Git user not configured. Please enter your details:"
    read -p "Your name: " git_name
    read -p "Your email: " git_email
    git config user.name "$git_name"
    git config user.email "$git_email"
    echo "✓ Git configured"
fi

echo ""
echo "============================================================"
echo "SECURITY CHECK"
echo "============================================================"

# Check if .env is in gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "✓ .env is in .gitignore (safe)"
else
    echo "⚠️  Adding .env to .gitignore for safety"
    echo ".env" >> .gitignore
fi

# Warn if .env exists and is tracked
if [ -f ".env" ] && git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ WARNING: .env file is tracked by git!"
    echo "Removing from git (keeping local copy)..."
    git rm --cached .env
fi

echo ""
echo "============================================================"
echo "GITHUB REPOSITORY"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "2. Choose a name (e.g., 'solana-trading-bot')"
echo "3. Make it PRIVATE (recommended for trading bot)"
echo "4. DON'T initialize with README"
echo ""
read -p "Press Enter when repository is created..."
echo ""
read -p "Enter repository URL (e.g., https://github.com/user/repo.git): " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ No URL provided. Exiting."
    exit 1
fi

# Add remote
if git remote | grep -q "^origin$"; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin "$repo_url"
else
    git remote add origin "$repo_url"
fi

echo "✓ Remote added: $repo_url"
echo ""

# Stage all files
echo "Staging files..."
git add .

echo ""
echo "Files to be committed:"
git status --short
echo ""

read -p "Commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Initial commit: Revolutionary Solana Trading Bot v1.0"
fi

# Commit
git commit -m "$commit_msg"

echo ""
echo "✓ Changes committed"
echo ""

# Push
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "============================================================"
echo "✅ SUCCESS!"
echo "============================================================"
echo ""
echo "Your code is now on GitHub!"
echo "View it at: ${repo_url%.git}"
echo ""
echo "Next time, just use:"
echo "  git add ."
echo "  git commit -m 'Your changes'"
echo "  git push"
echo ""

