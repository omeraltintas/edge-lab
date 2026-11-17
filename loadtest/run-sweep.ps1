param(
    [string]$BaseUrl = "http://192.168.56.10:18000",
    [string]$Duration = "30s",
    [int[]]$Levels = @(5, 10, 20, 40, 80, 160)
)

# Kapali cevrim sweep: her seviye ayri kosu, ayri JSON.
# Cikti: docs/results/sweep-vus-<n>.json

$repoRoot = Split-Path -Parent $PSScriptRoot
$resultDir = Join-Path $repoRoot "docs/results"
New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

Push-Location $repoRoot
try {
    foreach ($vus in $Levels) {
        Write-Host "=== VUS=$vus duration=$Duration ===" -ForegroundColor Cyan
        k6 run `
            -e BASE_URL=$BaseUrl `
            -e VUS=$vus `
            -e DURATION=$Duration `
            --summary-export "docs/results/sweep-vus-$vus.json" `
            loadtest/sweep.js
    }
}
finally {
    Pop-Location
}
