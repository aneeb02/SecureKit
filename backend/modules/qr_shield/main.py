from fastapi import FastAPI, UploadFile, File
import joblib
import numpy as np

from qr_decoder import decode_qr_from_bytes
from feature_extractor import extract_url_features

app = FastAPI()

# Load model + feature order
model = joblib.load("model/qrshield_url_model.pkl")
feature_order = joblib.load("model/qrshield_feature_order.pkl")

@app.post("/analyze_qr")
async def analyze_qr(file: UploadFile = File(...)):

    file_bytes = await file.read()

    # Step 1: Decode QR
    url = decode_qr_from_bytes(file_bytes)
    if url is None:
        return {"success": False, "error": "No QR code detected"}

    # Step 2: Extract features
    features = extract_url_features(url)
    vector = np.array([features[f] for f in feature_order]).reshape(1, -1)

    # Step 3: ML prediction
    prediction = model.predict(vector)[0]
    prob = model.predict_proba(vector)[0][1]

    return {
        "success": True,
        "url": url,
        "prediction": "malicious" if prediction == 1 else "benign",
        "probability": float(prob)
    }
