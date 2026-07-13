from fastapi import FastAPI, Request, HTTPException
import joblib
import pandas as pd
import os
import uvicorn

# Initialize the FastAPI Microservice
app = FastAPI(title="Python AI Engine - Trade Routing API", version="1.0")

# Load the trained XGBoost model into the server's memory
MODEL_PATH = os.path.join("data", "xgboost_baseline.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"[+] Successfully loaded AI model from {MODEL_PATH}")
except Exception as e:
    print(f"[!] ERROR: Could not load model. Ensure Task 2.3 was completed. Details: {e}")
    model = None

@app.get("/")
def health_check():
    """
    Basic endpoint to verify the microservice is online.
    """
    return {
        "status": "Online", 
        "microservice": "Python AI Engine",
        "model_loaded": model is not None
    }

@app.post("/predict")
async def predict_market_trend(request: Request):
    """
    Endpoint where the C# Meta-Controller sends live technical indicators.
    The AI evaluates the data and returns a 1 (Buy) or 0 (Sell/Hold).
    """
    if model is None:
        raise HTTPException(status_code=500, detail="AI Model is not loaded.")

    try:
        # Parse the JSON payload sent from the C# frontend
        incoming_data = await request.json()
        
        # Convert JSON into a Pandas DataFrame for the XGBoost model
        df_features = pd.DataFrame([incoming_data])
        
        # Ask the AI for a prediction
        prediction = model.predict(df_features)
        predicted_class = int(prediction[0])
        
        return {
            "status": "success",
            "prediction_code": predicted_class,
            "signal": "BUY (UPWARD TREND)" if predicted_class == 1 else "HOLD/SELL (DOWNWARD TREND)"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

# ==========================================
# Execution Block
# ==========================================
if __name__ == "__main__":
    print("[*] Booting up the Python AI Engine Microservice on Port 8000...")
    # uvicorn runs the FastAPI app on a local web server
    uvicorn.run("api_gateway:app", host="127.0.0.1", port=8000, reload=True)