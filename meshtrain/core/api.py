from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MeshTrain Local API", version="0.1.0")

class InferenceRequest(BaseModel):
    model: str
    prompt: str

@app.get("/v1/node")
def get_node_status():
    return {"status": "online", "version": "0.1.0"}

@app.get("/v1/benchmark")
def get_benchmark():
    return {"compute_score": 100, "vram": "16GB"}

@app.post("/v1/inference")
def run_inference(req: InferenceRequest):
    return {"result": f"Simulated inference for {req.model} with prompt: {req.prompt}"}
