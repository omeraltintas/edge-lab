param(
    [string]$BaseUrl = "http://192.168.56.10:18080",
    [string]$Duration = "30s",
    [int[]]$Levels = @(5, 10, 20, 40, 80, 160),
    [string]$Prefix = ""
)

# Kapali cevrim sweep: her seviye ayri kosu, ayri JSON.
# Cikti: docs/results/<prefix>-sweep-vus-<n>.json
#
# Prefix onerilir: vermezsen dosyalar sabit isimle yazilir ve onceki fazin
# olcumlerinin uzerine gecer (Faz 1'de tam olarak bu oldu).

$repoRoot = Split-Path -Parent $PSScriptRoot
$resultDir = Join-Path $repoRoot "docs/results"
New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

$namePrefix = if ($Prefix) { "$Prefix-" } else { "" }

Push-Location $repoRoot
try {
    foreach ($vus in $Levels) {
        $out = "docs/results/${namePrefix}sweep-vus-$vus.json"
        Write-Host "=== VUS=$vus duration=$Duration -> $out ===" -ForegroundColor Cyan
        k6 run `
            -e BASE_URL=$BaseUrl `
            -e VUS=$vus `
            -e DURATION=$Duration `
            --summary-export $out `
            loadtest/sweep.js
    }
}
finally {
    Pop-Location
}
