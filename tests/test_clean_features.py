import pandas as pd

from clean_features import engineer_features


def test_engineer_features_creates_expected_columns() -> None:
    raw = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=8, freq="D").astype(str),
            "Open": [100, 101, 102, 103, 104, 105, 106, 107],
            "High": [101, 102, 103, 104, 105, 106, 107, 108],
            "Low": [99, 100, 101, 102, 103, 104, 105, 106],
            "Close": [100, 102, 101, 103, 104, 106, 105, 107],
            "Volume": [1000, 1100, 1050, 1150, 1200, 1300, 1250, 1350],
            "Dividends": [0] * 8,
            "Stock Splits": [0] * 8,
        }
    )

    cleaned = engineer_features(raw)

    assert "Daily_Return" in cleaned.columns
    assert "MA_5" in cleaned.columns
    assert "Dividends" not in cleaned.columns
    assert "Stock Splits" not in cleaned.columns
    assert len(cleaned) > 0
    assert cleaned.index.name == "Date"
