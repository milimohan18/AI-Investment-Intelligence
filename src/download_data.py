import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def sanitize_symbol(symbol: str) -> str:
    """Convert symbol into filesystem-safe text used in artifact file names."""
    return "".join(ch if ch.isalnum() else "_" for ch in symbol)


def normalize_download_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Flatten yfinance output to single-level OHLCV columns when needed."""
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data


def download_stock_data(ticker: str = "AAPL", period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """Download historical stock data from Yahoo Finance."""
    print(f"Downloading {ticker} stock data ({period}, {interval})...")
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        raise ValueError(f"No data returned for ticker: {ticker}")
    return normalize_download_columns(data)


def save_raw_data(data: pd.DataFrame, ticker: str = "AAPL") -> Path:
    """Save downloaded stock data to data/<TICKER>_stock_data.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / f"{sanitize_symbol(ticker)}_stock_data.csv"
    data.to_csv(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download historical stock data")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol (default: AAPL)")
    parser.add_argument("--benchmark", default="^GSPC", help="Benchmark index symbol (default: ^GSPC)")
    parser.add_argument("--period", default="2y", help="History window (default: 2y)")
    parser.add_argument("--interval", default="1d", help="Data interval (default: 1d)")
    args = parser.parse_args()

    stock_data = download_stock_data(ticker=args.ticker, period=args.period, interval=args.interval)
    stock_path = save_raw_data(stock_data, ticker=args.ticker)
    print("Stock first 5 rows:")
    print(stock_data.head())
    print(f"Stock data saved to: {stock_path}")

    benchmark_data = download_stock_data(ticker=args.benchmark, period=args.period, interval=args.interval)
    benchmark_path = save_raw_data(benchmark_data, ticker=args.benchmark)
    print("Benchmark first 5 rows:")
    print(benchmark_data.head())
    print(f"Benchmark data saved to: {benchmark_path}")


if __name__ == "__main__":
    main()
