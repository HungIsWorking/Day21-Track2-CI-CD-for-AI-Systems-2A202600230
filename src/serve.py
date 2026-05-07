from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.storage.blob import BlobServiceClient
import joblib
import os

app = FastAPI()

# Doc ten container tu bien moi truong
CLOUD_BUCKET = os.environ.get("CLOUD_BUCKET", os.environ.get("GCS_BUCKET", ""))
MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")

def download_model():
    """Tai file model.pkl tu Azure Blob Storage ve may khi server khoi dong."""
    try:
        # Azure su dung AZURE_STORAGE_CONNECTION_STRING
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            print("Warning: AZURE_STORAGE_CONNECTION_STRING not set. Model download skipped.")
            return

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=CLOUD_BUCKET, blob=MODEL_KEY)

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        print("Model downloaded successfully from Azure Blob Storage.")
    except Exception as e:
        print(f"Failed to download model: {e}")

# Goi khi server khoi dong
download_model()
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """Endpoint kiem tra suc khoe server."""
    if model is None:
        return {"status": "error", "message": "Model not loaded"}
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luan.
    """
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    preds = model.predict([req.features])
    prediction = int(preds[0])
    
    labels = {0: "thấp", 1: "trung_bình", 2: "cao"}
    label = labels.get(prediction, "unknown")
    
    return {"prediction": prediction, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
