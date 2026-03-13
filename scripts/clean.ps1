$ErrorActionPreference = "Stop"

Write-Output "Cleaning Python cache and generated artifacts..."

Get-ChildItem -Path . -Recurse -Directory -Force -Filter __pycache__ |
    ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }

Get-ChildItem -Path . -Recurse -File -Force -Include *.pyc, *.pyo |
    ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }

$generated = @(
    ".\data\*_stock_data.csv",
    ".\data\*_cleaned.csv",
    ".\data\*_predictions.csv",
    ".\data\*_plot.png",
    ".\data\*_explanation_*.txt",
    ".\data\daily_run_log.txt",
    ".\daily_run_log.txt",
    ".\src\daily_run_log.txt"
)

foreach ($pattern in $generated) {
    Get-ChildItem -Path $pattern -Force -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
}

Write-Output "Cleanup complete."
