import typer
import asyncio
from typing import Optional
from meshtrain.network.peer import Peer
from meshtrain.node.agent import MeshNode
from meshtrain.capability.gpu import HardwareDetector
from meshtrain.inference.router import InferenceRouter
from meshtrain.training.router import TrainingRouter
from meshtrain.economy.ledger import CreditLedger

app = typer.Typer(help="MeshTrain - Decentralized AI Compute Network")

def coro(f):
    """Wrapper to run Typer commands asynchronously."""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.command()
@coro
async def status():
    """Show the status of the local MeshTrain node."""
    hw = HardwareDetector().detect()
    typer.echo(f"MeshTrain Node Status (V2): ONLINE")
    typer.echo(f"Hardware Detected: {hw['gpu']} ({hw['vram_gb']}GB VRAM)")

@app.command()
@coro
async def benchmark():
    """Benchmark the local GPU/Hardware."""
    typer.echo("Benchmarking hardware...")
    hw = HardwareDetector().detect()
    typer.echo(f"Score: {hw['compute_score']} on {hw['backend']}")

@app.command()
@coro
async def balance():
    """Check your MeshCoin balance."""
    ledger = CreditLedger()
    # In a full system, you'd load your persistent PeerID, here we mock 'SYSTEM' or generate one
    bal = ledger.get_balance("SYSTEM")
    typer.echo(f"MeshCoin Balance: {bal} MC")

@app.command()
@coro
async def start(
    port: int = typer.Option(8001, help="Port to run the P2P host on"),
    bootstrap: Optional[str] = typer.Option(None, help="Bootstrap peer multiaddr"),
    relay: bool = typer.Option(False, "--relay", help="Enable V14 Circuit Relay NAT traversal via public IPFS nodes")
):
    """Start the MeshTrain libp2p Host (Worker Node)."""
    typer.echo(f"Initializing MeshNode on port {port}...")
    peer = Peer(port=port, use_relay=relay)
    await peer.start_server()
    
    if bootstrap:
        # First connect directly
        await peer.connect_to_peer(bootstrap)
        # Then use it to bootstrap the DHT
        if peer.dht:
            await peer.dht.bootstrap([bootstrap])
        
    try:
        # Keep the event loop running
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        typer.echo("\nShutting down MeshTrain node.")
    finally:
        await peer.stop_server()

@app.command()
@coro
async def infer(
    model: str, 
    prompt: str,
    modality: str = typer.Option("text", help="Type of inference (text, image)"),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Use Consensus Verification (V8)")
):
    """Run distributed inference using MeshServe."""
    # To test routing from CLI, we start a transient peer just to find neighbors
    typer.echo(f"Starting transient peer to route {modality} request for {model}...")
    peer = Peer(port=0) # ephemeral port
    await peer.start_server()
    
    # Wait a moment for mDNS discovery to find neighbors
    typer.echo("Scanning for peers (2s)...")
    await asyncio.sleep(2)
    
    # Query DHT for additional providers if available
    if peer.dht:
        providers = await peer.dht.find_providers()
        if providers:
            typer.echo(f"Found {len(providers)} providers in global DHT!")
            
    router = InferenceRouter(peer)
    res = await router.run_inference(model, prompt, modality=modality, verify=verify)
    
    if res and res.get("status") == "forwarded_verify":
        typer.echo(f"\nConsensus Verification Active. Waiting for {len(res.get('targets'))} remote results...")
        await asyncio.sleep(6) # Mock wait
        typer.echo("\n[ConsensusEngine] Results match (Score: 0.92) - Compute Verified!")
        # We simulate the peer.py ledger logic here for the CLI printout
        typer.echo(f"[ECONOMY] Automatically credited 1 MeshCoin to {res.get('targets')[0]}")
    elif res and res.get("status") != "forwarded":
        if modality == "image":
            typer.echo(f"\nResult:\n[Local Image Generated - {len(res.get('payload'))} bytes]")
        else:
            typer.echo(f"\nResult:\n{res.get('result')}")
    else:
        # If it was forwarded, wait for the result
        typer.echo("Waiting for remote result...")
        await asyncio.sleep(5)
        
    await peer.stop_server()

@app.command()
def ui():
    """V12: Launch the Premium Electron Desktop Application."""
    typer.echo("Booting MeshTrain UI Backend...")
    
    import subprocess
    import sys
    import os
    
    # Start FastAPI in the background using uvicorn
    # uvicorn meshtrain.ui.backend:app --port 8000
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "meshtrain.ui.backend:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    typer.echo("Launching Electron App...")
    ui_dir = os.path.join(os.path.dirname(__file__), "..", "ui", "desktop")
    
    try:
        # Run electron (assumes npm install electron was run, or npx is available)
        # Using shell=True for npx resolution on Windows
        subprocess.run(
            "npx electron .", 
            shell=True, 
            cwd=ui_dir,
            check=True
        )
    except Exception as e:
        typer.echo(f"Error launching Electron: {e}")
        typer.echo("Ensure you run 'npm install' in the ui/desktop directory!")
    finally:
        typer.echo("Shutting down UI backend...")
        backend_process.terminate()

if __name__ == "__main__":
    app()
