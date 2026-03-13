import argparse
import datetime as dt
import os
from pathlib import Path

try:
    from .clean_features import engineer_features, load_raw_data, save_clean_data
    from .download_data import download_stock_data, save_raw_data
    from .ml_model import run_model_pipeline
except ImportError:
    from clean_features import engineer_features, load_raw_data, save_clean_data
    from download_data import download_stock_data, save_raw_data
    from ml_model import run_model_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
LOG_PATH = DATA_DIR / "daily_run_log.txt"


def append_run_log(message: str) -> None:
    """Append a timestamped line to the pipeline run log."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{dt.datetime.now().isoformat()} | {message}\n")


def generate_ai_explanation(table_text: str, model_name: str = "gpt-4o-mini") -> str | None:
    """Generate plain-language explanation using OpenAI if API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("AI explanation skipped: OPENAI_API_KEY is not set.")
        return None

    try:
        from openai import OpenAI
    except ImportError:
        print("AI explanation skipped: openai package is not installed.")
        return None

    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a friendly financial assistant. "
            "Explain this stock daily return prediction table in simple language for a beginner.\n"
            f"Table:\n{table_text}"
        )
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as exc:
        print(f"AI explanation skipped due to API error: {exc}")
        return None


def get_close_series(frame):
    """Get close-price series from stock frame with fallback matching."""
    if "Close" in frame.columns:
        return frame["Close"]
    close_candidates = [col for col in frame.columns if str(col).lower().startswith("close")]
    if close_candidates:
        return frame[close_candidates[0]]
    raise KeyError("Close column not found in downloaded data")


def print_latest_snapshot(stock_data, market_data, ticker: str, benchmark: str) -> None:
    """Print latest stock and benchmark close/return values for quick market context."""
    stock_close = get_close_series(stock_data)
    latest_stock_close = stock_close.dropna().iloc[-1]
    stock_return = stock_close.pct_change().iloc[-1]
    print(f"Latest {ticker} close: {float(latest_stock_close):.2f}")
    print(f"Latest {ticker} daily return: {float(stock_return):.5f}")

    market_close = get_close_series(market_data)
    latest_market_close = market_close.dropna().iloc[-1]
    market_return = market_close.pct_change().iloc[-1]
    print(f"Latest {benchmark} close: {float(latest_market_close):.2f}")
    print(f"Latest {benchmark} daily return: {float(market_return):.5f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run daily stock data + ML + optional AI explanation")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol (default: AAPL)")
    parser.add_argument("--benchmark", default="^GSPC", help="Benchmark index symbol (default: ^GSPC)")
    parser.add_argument("--period", default="2y", help="History window for download (default: 2y)")
    parser.add_argument("--interval", default="1d", help="Download interval (default: 1d)")
    parser.add_argument("--skip-ai", action="store_true", help="Skip AI explanation step")
    parser.add_argument("--ai-model", default="gpt-4o-mini", help="OpenAI model for explanation")
    parser.add_argument("--live-plot", action="store_true", help="Show animated live plot window")
    args = parser.parse_args()

    append_run_log(f"Pipeline started for {args.ticker}")
    print(f"Running pipeline for {args.ticker} with benchmark {args.benchmark}...")

    raw_data = download_stock_data(args.ticker, args.period, args.interval)
    raw_path = save_raw_data(raw_data, args.ticker)
    print(f"Raw data saved to: {raw_path}")

    market_raw_data = download_stock_data(args.benchmark, args.period, args.interval)
    market_raw_path = save_raw_data(market_raw_data, args.benchmark)
    print(f"Market data saved to: {market_raw_path}")

    cleaned_data = engineer_features(
        load_raw_data(args.ticker),
        market_data=load_raw_data(args.benchmark),
    )
    cleaned_path = save_clean_data(cleaned_data, args.ticker)
    print(f"Cleaned data saved to: {cleaned_path}")
    print_latest_snapshot(raw_data, market_raw_data, args.ticker, args.benchmark)

    comparison, mse, predictions_path, plot_path = run_model_pipeline(
        args.ticker,
        write_plot=True,
        show_live=args.live_plot,
    )
    print(f"Mean Squared Error: {mse}")
    print(f"Predictions saved to: {predictions_path}")
    if plot_path:
        print(f"Plot saved to: {plot_path}")

    if not args.skip_ai:
        explanation = generate_ai_explanation(comparison.tail(5).to_string(), model_name=args.ai_model)
        if explanation:
            explanation_path = DATA_DIR / f"{args.ticker}_explanation_{dt.date.today().isoformat()}.txt"
            explanation_path.write_text(explanation, encoding="utf-8")
            print("AI explanation generated:")
            print(explanation)
            print(f"Explanation saved to: {explanation_path}")

    append_run_log(f"Pipeline completed for {args.ticker}")


if __name__ == "__main__":
    main()
