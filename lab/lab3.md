# Lab 3 - Model Serving with FastAPI and Docker

## Objective

The objective of this lab is to deploy the trained Food-11 image classification model as a REST API using FastAPI and package the application in a Docker container.

The model was trained using PyTorch and tracked using MLflow in Lab 2.

---

## Model Selection

The selected model is a pretrained ResNet18 fine-tuned for 11 food categories.

Best training run: `bustling-deer-164`

- Learning rate: `0.0001`
- Batch size: `32`
- Epochs: `5`
- Final validation accuracy: `0.7080`
- Test accuracy: `0.7600`

The model was registered in MLflow as `food11`, version 1, with the alias `champion`.

## FastAPI Implementation

The API was implemented in `src/food11/serve.py`.

Two endpoints were created:

### GET /health

This endpoint checks whether the application is running and whether the model has been loaded.

Successful response:

```json
{"status": "ok", "model_loaded": true}
```

### POST /predict

This endpoint accepts an uploaded food image and returns:

- Predicted class ID
- Predicted class name
- Prediction confidence

The uploaded image is converted to RGB, resized, normalized, and passed through the trained ResNet18 model.

The prediction is calculated using PyTorch and the softmax function.

## Docker Implementation

A multi-stage Dockerfile was created using Python 3.13.

The first stage installs the Python dependencies using `uv`.

The second stage copies the environment, application code, and trained model artifacts into the runtime image.

The model artifacts are stored locally in `docker-model/` and copied into the container during the build.

The Docker image was built using:

```powershell
docker build -t food11-api:latest .
```

The container was started using:

```powershell
docker run --rm --name food11-container -p 8000:8000 food11-api:latest
```

## API Testing

### Health Check

Command:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Result:

```json
{"status": "ok", "model_loaded": true}
```

The health check confirmed that the API was running and the trained model was loaded.

### Prediction Test

The prediction endpoint was tested using FastAPI Swagger UI:

`http://127.0.0.1:8000/docs`

The API successfully accepted an uploaded image and returned HTTP status `200`.

Observed prediction:

```json
{
  "class_id": 3,
  "class_name": "Egg",
  "confidence": 0.3795
}
```

This confirmed that the inference endpoint worked inside the Docker container. The predicted category is not necessarily the correct category for the uploaded image.

## Version Control

The following files were prepared for Git:

- `Dockerfile`
- `.dockerignore`
- `src/food11/serve.py`
- `pyproject.toml`
- `uv.lock`
- `lab/lab3.md`
- `.gitignore`

The `docker-model/` directory was excluded from Git because it contains generated model artifacts.

To reproduce the Docker image on another machine, the model artifacts must first be obtained from the corresponding MLflow model and placed in `docker-model/`.

## Conclusion

In this lab, the Food-11 classification model was successfully deployed using FastAPI and Docker.

Both the `/health` and `/predict` endpoints were tested successfully.

The Docker container loaded the trained model and performed image inference, demonstrating a working model-serving workflow.