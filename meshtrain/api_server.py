import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from meshtrain.network.peer import Peer

app = FastAPI(title="MeshTrain OpenAI-Compatible API", version="1.0")
# Global peer instance for the API
mesh_node = None

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 100

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    if not mesh_node:
        raise HTTPException(status_code=500, detail="Mesh node not initialized")
        
    prompt = "\n".join([f"{m.role}: {m.content}" for m in req.messages])
    
    # We submit it to the local node's agent. If it needs to be offloaded to the mesh, 
    # the scheduler logic would go here. For MVP, we use the local isolated sandbox.
    print(f"[API] Received inference request for {req.model}")
    
    # Try to resolve via local AI node (which now uses isolated ProcessSandbox)
    result = mesh_node.ai_node.infer(req.model, prompt, max_length=req.max_tokens)
    
    return {
        "id": "chatcmpl-meshtrain",
        "object": "chat.completion",
        "created": 1677652288,
        "model": req.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": result.get("result", "Error")
            },
            "finish_reason": "stop"
        }]
    }

def start_api_server(port: int = 8080, peer_instance: Peer = None):
    global mesh_node
    mesh_node = peer_instance
    print(f"[API] Starting OpenAI-compatible server on http://localhost:{port}/v1")
    uvicorn.run(app, host="0.0.0.0", port=port)
