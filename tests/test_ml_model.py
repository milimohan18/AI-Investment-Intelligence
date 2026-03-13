from pathlib import Path

import pandas as pd

import ml_model


def test_run_model_pipeline_writes_predictions(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ml_model, "DATA_DIR", tmp_path)

    df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=40, freq="D"),
            "Close": [100 + i for i in range(40)],
            "MA_5": [100 + i for i in range(40)],
            "Volume": [1000 + (i * 10) for i in range(40)],
            "Daily_Return": [0.001 + (i * 0.0001) for i in range(40)],
        }
    ).set_index("Date")

    (tmp_path / "TEST_cleaned.csv").write_text(df.to_csv(), encoding="utf-8")

    comparison, mse, predictions_path, plot_path = ml_model.run_model_pipeline(
        ticker="TEST",
        write_plot=False,
    )

    assert not comparison.empty
    assert mse >= 0
    assert predictions_path.exists()
    assert plot_path is None
