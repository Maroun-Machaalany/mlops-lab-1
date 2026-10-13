
import io
import os

import mlflow
import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from torchvision import transforms

app = FastAPI(title="Food-11 Classification API")

MODEL_URI = os.getenv("MODEL_URI", "models:/food11@champion")

CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

model = None


@app.on_event("startup")
def load_model():
    global model
    mlflow.set_tracking_uri(
        os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    )
    model = mlflow.pytorch.load_model(MODEL_URI, map_location="cpu")
    model.eval()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, dim=1)

        index = predicted.item()
        return {
            "class_id": index,
            "class_name": CLASS_NAMES[index],
            "confidence": round(confidence.item(), 4),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
