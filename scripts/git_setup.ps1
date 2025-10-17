# Git Setup Script for Windows PowerShell
# Helps you push Solana Trading Bot to GitHub

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GIT SETUP WIZARD FOR WINDOWS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if already a git repo
if (Test-Path ".git") {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
} else {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
}

Write-Host ""

# Configure git (if not configured)
$gitName = git config user.name
if ([string]::IsNullOrEmpty($gitName)) {
    Write-Host "Git user not configured. Please enter your details:" -ForegroundColor Yellow
    $name = Read-Host "Your name"
    $email = Read-Host "Your email"
    git config user.name "$name"
    git config user.email "$email"
    Write-Host "✓ Git configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SECURITY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check .gitignore
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore"
    if ($gitignoreContent -match "^\.env$") {
        Write-Host "✓ .env is in .gitignore (safe)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env not explicitly in .gitignore" -ForegroundColor Yellow
        Write-Host "   (Should be okay, but double-check)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  No .gitignore found" -ForegroundColor Yellow
}

# Check if .env is staged
if (Test-Path ".env") {
    Write-Host "⚠️  WARNING: .env file exists" -ForegroundColor Yellow
    Write-Host "   Make sure it's in .gitignore!" -ForegroundColor Yellow
    Write-Host "   NEVER commit your .env file!" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GITHUB REPOSITORY SETUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: solana-trading-bot (or your choice)" -ForegroundColor White
Write-Host "3. Make it PRIVATE (recommended for trading bot)" -ForegroundColor White
Write-Host "4. DON'T initialize with README" -ForegroundColor White
Write-Host "5. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when repository is created"

Write-Host ""
$repoUrl = Read-Host "Enter repository URL (e.g., https://github.com/user/repo.git)"

if ([string]::IsNullOrEmpty($repoUrl)) {
    Write-Host "❌ No URL provided. Exiting." -ForegroundColor Red
    exit 1
}

# Add remote
try {
    $existingRemote = git remote
    if ($existingRemote -contains "origin") {
        Write-Host "Remote 'origin' already exists. Updating..." -ForegroundColor Yellow
        git remote set-url origin $repoUrl
    } else {
        git remote add origin $repoUrl
    }
    Write-Host "✓ Remote added: $repoUrl" -ForegroundColor Green
} catch {
    Write-Host "❌ Error adding remote: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Stage files
Write-Host "Staging files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
git status --short

Write-Host ""
$commitMsg = Read-Host "Commit message (or press Enter for default)"
if ([string]::IsNullOrEmpty($commitMsg)) {
    $commitMsg = "Initial commit: Revolutionary Solana Trading Bot v1.0"
}

# Commit
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "$commitMsg"

Write-Host ""
Write-Host "✓ Changes committed" -ForegroundColor Green
Write-Host ""

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main

try {
    git push -u origin main
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code is now on GitHub!" -ForegroundColor Green
    Write-Host "View it at: $($repoUrl -replace '\.git$','')" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next time, just use:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'Your changes'" -ForegroundColor White
    Write-Host "  git push" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "❌ Push failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Wrong repository URL" -ForegroundColor White
    Write-Host "2. Need to authenticate (use GitHub token or SSH)" -ForegroundColor White
    Write-Host "3. Repository doesn't exist yet" -ForegroundColor White
    Write-Host ""
    Write-Host "Try again with correct URL or use GitHub Desktop" -ForegroundColor Yellow
}

