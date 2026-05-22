param(
    [string]$DestDir = (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "backup")
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$ArchiveName = "backup_$Timestamp.zip"
$ArchivePath = Join-Path $DestDir $ArchiveName

# Ensure backup directory exists
if (-not (Test-Path -LiteralPath $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
}

# Files to backup (gitignored / untracked items)
$Items = @(
    (Join-Path $ProjectRoot ".env"),
    (Join-Path $ProjectRoot "expense_tracker.db"),
    (Join-Path $ProjectRoot "requirements.txt")
)

# Filter to only existing files
$ExistingItems = @()
foreach ($item in $Items) {
    if (Test-Path -LiteralPath $item) {
        $ExistingItems += $item
        Write-Host "  [OK]   $((Get-Item $item).Name)" -ForegroundColor Green
    } else {
        Write-Host "  [MISS] $((Split-Path $item -Leaf)) (skipping)" -ForegroundColor Yellow
    }
}

if ($ExistingItems.Count -eq 0) {
    Write-Host "`nNothing to back up." -ForegroundColor Red
    exit 1
}

# Create zip archive
$TempDir = Join-Path $env:TEMP "backup_temp_$PID"
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

try {
    foreach ($item in $ExistingItems) {
        Copy-Item -LiteralPath $item -Destination $TempDir
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($TempDir, $ArchivePath)

    $ZipInfo = Get-Item -LiteralPath $ArchivePath
    Write-Host "`nBackup saved: $ArchivePath" -ForegroundColor Cyan
    Write-Host "Size: $('{0:N1} KB' -f ($ZipInfo.Length / 1KB))" -ForegroundColor Cyan

    # Keep only last 10 backups
    $AllBackups = Get-ChildItem -LiteralPath $DestDir -Filter "backup_*.zip" | Sort-Object Name -Descending
    if ($AllBackups.Count -gt 10) {
        $ToRemove = $AllBackups | Select-Object -Skip 10
        foreach ($old in $ToRemove) {
            Remove-Item -LiteralPath $old.FullName -Force
            Write-Host "  Pruned old backup: $($old.Name)" -ForegroundColor DarkGray
        }
    }
} finally {
    Remove-Item -LiteralPath $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "`nDone." -ForegroundColor Green
