# AI Investment Intelligence

AI Investment Intelligence is a clean, reproducible stock-analysis pipeline designed as a portfolio-ready machine learning project.

It performs:
1. Market data download from Yahoo Finance.
2. Data cleaning and feature engineering.
3. Baseline regression modeling and evaluation.
4. Optional AI-generated plain-language explanation of recent predictions.

## Why this project is portfolio-ready

1. Modular code with single-responsibility scripts.
2. Environment-based secret handling, no hardcoded keys.
3. Automated tests and GitHub Actions CI.
4. Reproducible outputs and run logging.
5. Clear setup and execution documentation.

## Repository structure

- src/download_data.py: Downloads historical stock data.
- src/clean_features.py: Cleans data and creates modeling features.
- src/ml_model.py: Trains baseline model, writes predictions, saves plot.
- src/daily_update.py: Orchestrates the full end-to-end pipeline.
- tests/: Unit tests for feature engineering, model pipeline, and AI fallback behavior.
- .github/workflows/ci.yml: CI pipeline for automated testing.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Optional, for AI explanation: create a .env file or set environment variable.

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run

Run full pipeline:

```powershell
python src/daily_update.py
```

Run without AI step (recommended for deterministic local runs):

```powershell
python src/daily_update.py --skip-ai
```

Run modules independently:

```powershell
python src/download_data.py --ticker AAPL --period 2y --interval 1d
python src/clean_features.py --ticker AAPL
python src/ml_model.py --ticker AAPL
```

## Test

```powershell
pytest
```

## Cleanup generated artifacts

```powershell
powershell -ExecutionPolicy Bypass -File scripts/clean.ps1
```

## CI

GitHub Actions runs tests on every push and pull request via:
- .github/workflows/ci.yml

## Outputs

Generated files under data/:
- <TICKER>_stock_data.csv
- <TICKER>_cleaned.csv
- <TICKER>_predictions.csv
- <TICKER>_plot.png
- <TICKER>_explanation_<DATE>.txt (if AI enabled)
- daily_run_log.txt

## Limitations and future work

1. Current model is a baseline linear regression.
2. Single-ticker execution per run.
3. No hyperparameter search or cross-validation yet.

Suggested upgrades:
1. Add multiple models and compare metrics.
2. Add richer feature set (technical indicators, lag features).
3. Add backtesting and model monitoring.

## Disclaimer

This repository is for educational purposes only and is not financial advice.
