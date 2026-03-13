import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def sanitize_symbol(symbol: str) -> str:
    """Convert symbol into filesystem-safe text used in artifact file names."""
    return "".join(ch if ch.isalnum() else "_" for ch in symbol)


def load_raw_data(ticker: str = "AAPL") -> pd.DataFrame:
    """Load raw stock data from data/<TICKER>_stock_data.csv."""
    raw_csv_path = DATA_DIR / f"{sanitize_symbol(ticker)}_stock_data.csv"
    if not raw_csv_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {raw_csv_path}")
    return pd.read_csv(raw_csv_path)


def engineer_features(data: pd.DataFrame, market_data: pd.DataFrame | None = None) -> pd.DataFrame:
    """Clean source data and build features used by the model."""
    data = data.drop(columns=["Dividends", "Stock Splits"], errors="ignore")

    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data = data.dropna(subset=["Date"])
        data.set_index("Date", inplace=True)

    data["Daily_Return"] = data["Close"].pct_change()
    data["MA_5"] = data["Close"].rolling(window=5).mean()

    if market_data is not None and not market_data.empty:
        market_data = market_data.drop(columns=["Dividends", "Stock Splits"], errors="ignore")
        if "Date" in market_data.columns:
            market_data["Date"] = pd.to_datetime(market_data["Date"], errors="coerce")
            market_data = market_data.dropna(subset=["Date"])
            market_data.set_index("Date", inplace=True)
        if "Close" in market_data.columns:
            market_data["Market_Close"] = pd.to_numeric(market_data["Close"], errors="coerce")
            market_data["Market_Return"] = market_data["Market_Close"].pct_change()
            data = data.join(market_data[["Market_Close", "Market_Return"]], how="inner")

    return data.dropna()


def save_clean_data(data: pd.DataFrame, ticker: str = "AAPL") -> Path:
    """Save cleaned data to data/<TICKER>_cleaned.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    clean_csv_path = DATA_DIR / f"{sanitize_symbol(ticker)}_cleaned.csv"
    data.to_csv(clean_csv_path)
    return clean_csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean stock data and create ML features")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol (default: AAPL)")
    parser.add_argument("--benchmark", default="^GSPC", help="Benchmark index symbol (default: ^GSPC)")
    args = parser.parse_args()

    raw_data = load_raw_data(args.ticker)
    market_data = None
    try:
        market_data = load_raw_data(args.benchmark)
    except FileNotFoundError:
        market_data = None

    cleaned_data = engineer_features(raw_data, market_data=market_data)
    output_path = save_clean_data(cleaned_data, args.ticker)

    print("Original row count:", len(raw_data))
    print("Cleaned row count:", len(cleaned_data))
    print(f"Cleaned data saved to: {output_path}")
    print("First 5 rows of cleaned data:")
    print(cleaned_data.head())


if __name__ == "__main__":
    main()