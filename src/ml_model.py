import argparse
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def sanitize_symbol(symbol: str) -> str:
    """Convert symbol into filesystem-safe text used in artifact file names."""
    return "".join(ch if ch.isalnum() else "_" for ch in symbol)


def load_clean_data(ticker: str = "AAPL") -> pd.DataFrame:
    """Load cleaned data from data/<TICKER>_cleaned.csv."""
    csv_path = DATA_DIR / f"{sanitize_symbol(ticker)}_cleaned.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned data file not found: {csv_path}")

    data = pd.read_csv(csv_path, index_col=0)
    data.index = pd.to_datetime(data.index, errors="coerce")
    data = data[~data.index.isna()]
    numeric_cols = ["Close", "MA_5", "Volume", "Daily_Return", "Market_Close", "Market_Return"]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data.dropna()


def train_model(data: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    """Train linear regression and return comparison table + mse."""
    feature_cols = ["Close", "MA_5", "Volume"]
    if "Market_Return" in data.columns:
        feature_cols.append("Market_Return")
    X = data[feature_cols]
    y = data["Daily_Return"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    comparison = pd.DataFrame({"Actual": y_test, "Predicted": y_pred}).sort_index()
    mse = mean_squared_error(y_test, y_pred)
    return comparison, mse


def save_plot(comparison: pd.DataFrame, ticker: str = "AAPL") -> Path:
    """Save prediction-vs-actual plot to data/<TICKER>_plot.png."""
    y_pred_smooth = comparison["Predicted"].rolling(window=3).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(comparison.index, comparison["Actual"], label="Actual", color="blue", linewidth=2)
    plt.plot(
        comparison.index,
        y_pred_smooth,
        label="Predicted (Smoothed)",
        color="orange",
        linestyle="--",
        linewidth=2,
    )
    plt.title(f"{ticker} Daily Returns: Actual vs Predicted")
    plt.xlabel("Date")
    plt.ylabel("Daily Return")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path = DATA_DIR / f"{ticker}_plot.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


def show_live_plot(comparison: pd.DataFrame, ticker: str = "AAPL") -> None:
    """Show an animated live plot window for actual vs predicted values."""
    y_pred_smooth = comparison["Predicted"].rolling(window=3).mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f"{ticker} Daily Returns: Live Actual vs Predicted")
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Return")
    ax.grid(True)

    x_dt = pd.to_datetime(comparison.index, errors="coerce")
    valid_mask = ~x_dt.isna()
    x_dt = x_dt[valid_mask]
    y_actual_series = comparison.loc[valid_mask, "Actual"]
    y_pred_series = y_pred_smooth.loc[valid_mask]

    x_vals = mdates.date2num(x_dt.to_pydatetime())
    y_actual = y_actual_series.to_list()
    y_pred = y_pred_series.bfill().to_list()

    actual_line, = ax.plot([], [], label="Actual", color="blue", linewidth=2)
    pred_line, = ax.plot([], [], label="Predicted (Smoothed)", color="orange", linestyle="--", linewidth=2)
    actual_dot, = ax.plot([], [], "o", color="blue", markersize=5)
    pred_dot, = ax.plot([], [], "o", color="orange", markersize=5)
    value_text = ax.text(0.01, 0.98, "", transform=ax.transAxes, va="top")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    ax.legend()

    def init():
        actual_line.set_data([], [])
        pred_line.set_data([], [])
        actual_dot.set_data([], [])
        pred_dot.set_data([], [])
        value_text.set_text("")
        ax.relim()
        ax.autoscale_view()
        return actual_line, pred_line, actual_dot, pred_dot, value_text

    def update(frame_idx: int):
        actual_line.set_data(x_vals[:frame_idx], y_actual[:frame_idx])
        pred_line.set_data(x_vals[:frame_idx], y_pred[:frame_idx])
        if frame_idx > 0:
            actual_dot.set_data([x_vals[frame_idx - 1]], [y_actual[frame_idx - 1]])
            pred_dot.set_data([x_vals[frame_idx - 1]], [y_pred[frame_idx - 1]])
            value_text.set_text(
                f"Date: {x_dt.iloc[frame_idx - 1].date()}\n"
                f"Actual: {y_actual[frame_idx - 1]:.5f}\n"
                f"Predicted: {y_pred[frame_idx - 1]:.5f}"
            )
        ax.relim()
        ax.autoscale_view()
        return actual_line, pred_line, actual_dot, pred_dot, value_text

    anim = FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=len(x_vals) + 1,
        interval=40,
        blit=False,
        repeat=False,
    )
    fig._anim_ref = anim
    plt.tight_layout()
    plt.show()


def run_model_pipeline(
    ticker: str = "AAPL",
    write_plot: bool = True,
    show_live: bool = False,
) -> Tuple[pd.DataFrame, float, Path, Path | None]:
    """Run model pipeline and save key outputs."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = load_clean_data(ticker)
    comparison, mse = train_model(data)

    predictions_path = DATA_DIR / f"{sanitize_symbol(ticker)}_predictions.csv"
    comparison.to_csv(predictions_path)

    plot_path = save_plot(comparison, ticker=ticker) if write_plot else None
    if show_live:
        show_live_plot(comparison, ticker=ticker)
    return comparison, mse, predictions_path, plot_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Train stock prediction model")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol (default: AAPL)")
    parser.add_argument("--no-plot", action="store_true", help="Skip generating plot image")
    parser.add_argument("--live-plot", action="store_true", help="Show animated live plot window")
    args = parser.parse_args()

    comparison, mse, predictions_path, plot_path = run_model_pipeline(
        ticker=args.ticker,
        write_plot=not args.no_plot,
        show_live=args.live_plot,
    )

    print("First 5 predictions:")
    print(comparison.head())
    print(f"Mean Squared Error: {mse}")
    print(f"Predictions saved to: {predictions_path}")
    if plot_path:
        print(f"Plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
