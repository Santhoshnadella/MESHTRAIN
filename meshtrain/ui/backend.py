from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
from meshtrain.network.peer import Peer
from meshtrain.inference.router import InferenceRouter
from meshtrain.economy.ledger import CreditLedger

app = FastAPI(title="MeshTrain API Bridge")

class MeshState:
    peer = None
    router = None
    ledger = None

state = MeshState()

@app.on_event("startup")
async def startup_event():
    state.peer = Peer(port=0) # Ephemeral port for UI bridge
    await state.peer.start_server()
    state.router = InferenceRouter(state.peer)
    state.ledger = CreditLedger()
    print("MeshTrain API Bridge started.")

@app.on_event("shutdown")
async def shutdown_event():
    if state.peer:
        await state.peer.stop_server()

@app.get("/api/status")
async def get_status():
    peers = len(state.peer.connected_peers) if state.peer else 0
    balance = state.ledger.get_balance("SYSTEM") if state.ledger else 0
    return {"connected_peers": peers, "balance": balance, "status": "online"}

class InferRequest(BaseModel):
    model: str
    prompt: str
    modality: str = "text"

@app.post("/api/infer")
async def run_infer(req: InferRequest):
    # In a real async app we'd stream the response, for MVP we await it
    res = await state.router.run_inference(req.model, req.prompt, modality=req.modality)
    # Give the mock consensus engine time to finish if it's forwarded
    if res and res.get("status") == "forwarded_verify":
        await asyncio.sleep(2)
        return {"status": "verified", "result": "Mock Verified Result from Network!"}
    
    if req.modality == "image":
        return {"status": "success", "result": "[Image Generated Locally]"}
    
    return {"status": "success", "result": res.get("result") if res else "Error"}
