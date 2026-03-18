from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI(title="AI Investment Intelligence UI")

# Mount the static directory for the frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount it explicitly as the root / static path
app.mount("/static", StaticFiles(directory=static_dir), name="static")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

@app.get("/api/tickers")
def get_tickers():
    """Returns a list of available tickers by inspecting the data directory."""
    if not os.path.exists(DATA_DIR):
        return {"tickers": []}
    
    tickers = set()
    for file in os.listdir(DATA_DIR):
        if file.endswith("_predictions.csv"):
            tickers.add(file.replace("_predictions.csv", ""))
    return {"tickers": sorted(list(tickers))}

@app.get("/api/data/{ticker}")
def get_data(ticker: str):
    """Returns historical and latest predicted data for a given ticker."""
    pred_path = os.path.join(DATA_DIR, f"{ticker}_predictions.csv")
    hist_path = os.path.join(DATA_DIR, f"{ticker}_cleaned.csv")

    if not os.path.exists(pred_path):
        raise HTTPException(status_code=404, detail=f"Prediction data not found for {ticker}")
    
    # Read predictions
    df_pred = pd.read_csv(pred_path)
    
    # Check for historical actuals to include some history context
    history = []
    if os.path.exists(hist_path):
        df_hist = pd.read_csv(hist_path)
        # We only want the last 30 days of actual historical data to plot the preceding trend
        df_hist = df_hist.tail(30)
        for _, row in df_hist.iterrows():
            history.append({
                "Date": row.get("Date"),
                "Close": row.get("Close"),
                "Type": "Actual"
            })
    
    # Extract prediction data
    predictions = []
    for _, row in df_pred.iterrows():
        predictions.append({
            "Date": row.get("Date"),
            "Actual": row.get("Actual", None),
            "Predicted": row.get("Predicted", None)
        })

    return {
        "ticker": ticker,
        "history": history,
        "predictions": predictions
    }

@app.get("/")
def serve_index():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
