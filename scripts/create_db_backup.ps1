# Database backup script for Windows
# Creates timestamped PostgreSQL backup

$BackupDir = "backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir/trading_bot_backup_$Timestamp.sql"

# Create backups directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "✅ Created backups directory" -ForegroundColor Green
}

Write-Host "📦 Creating database backup..." -ForegroundColor Cyan
Write-Host "   File: $BackupFile"

try {
    # Create backup
    docker exec trading-bot-db pg_dump -U trader trading_bot > $BackupFile
    
    $FileSize = (Get-Item $BackupFile).Length / 1MB
    Write-Host "✅ Backup created successfully: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Green
    
    # Clean up old backups (keep last 7 days)
    Write-Host ""
    Write-Host "🧹 Cleaning old backups (keeping last 7 days)..."
    $CutoffDate = (Get-Date).AddDays(-7)
    Get-ChildItem $BackupDir -Filter "trading_bot_backup_*.sql" | 
        Where-Object { $_.LastWriteTime -lt $CutoffDate } | 
        ForEach-Object {
            Remove-Item $_.FullName
            Write-Host "   Deleted: $($_.Name)" -ForegroundColor Yellow
        }
    
    # List current backups
    Write-Host ""
    Write-Host "📁 Current backups:"
    Get-ChildItem $BackupDir -Filter "trading_bot_backup_*.sql" | 
        Sort-Object LastWriteTime -Descending | 
        ForEach-Object {
            $size = [math]::Round($_.Length / 1MB, 2)
            Write-Host "   $($_.Name): ${size} MB ($(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm'))"
        }
    
    Write-Host ""
    Write-Host "✅ Backup routine complete!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Backup failed: $_" -ForegroundColor Red
    exit 1
}

