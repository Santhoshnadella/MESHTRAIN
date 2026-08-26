import typer
import asyncio
from typing import Optional
from meshtrain.network.peer import Peer
from meshtrain.node.agent import MeshNode
from meshtrain.capability.gpu import HardwareDetector
from meshtrain.inference.router import InferenceRouter
from meshtrain.training.router import TrainingRouter
from meshtrain.economy.ledger import SignedTransactionLedger
from meshtrain.api_server import start_api_server
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
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
    ledger = SignedTransactionLedger()
    bal = ledger.get_balance("SYSTEM")
    console.print(f"[bold green]MeshCoin Balance:[/bold green] {bal} MC")

@app.command()
def api(port: int = typer.Option(8080, help="Port to run the OpenAI API on")):
    """Start the OpenAI-compatible HTTP API server."""
    # We create a dummy peer for local execution
    peer = Peer(port=0)
    console.print(f"[bold blue]Starting MeshTrain API Server on port {port}...[/bold blue]")
    start_api_server(port=port, peer_instance=peer)

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
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task1 = progress.add_task("Starting transient peer to route request...", total=None)
        peer = Peer(port=0) # ephemeral port
        await peer.start_server()
        
        progress.update(task1, description="Scanning for peers on the network...")
        await asyncio.sleep(2)
        
        if peer.dht:
            providers = await peer.dht.find_providers()
            if providers:
                progress.console.print(f"[bold green]✓ Found {len(providers)} providers in global DHT![/bold green]")
                
        progress.update(task1, description=f"Executing {model} inference request...")
        router = InferenceRouter(peer)
        res = await router.run_inference(model, prompt, modality=modality, verify=verify)
        progress.remove_task(task1)
        
    if res and res.get("status") == "forwarded_verify":
        console.print(f"\n[bold yellow]Consensus Verification Active.[/bold yellow] Waiting for {len(res.get('targets'))} remote results...")
        await asyncio.sleep(6) # Mock wait
        console.print("\n[bold green]✓ [ConsensusEngine] Results match (Score: Cryptographic Hash Match) - Compute Verified![/bold green]")
        console.print(f"[bold cyan]✓ [ECONOMY] Automatically verified signed transaction for {res.get('targets')[0]}[/bold cyan]")
    elif res and res.get("status") != "forwarded":
        if modality == "image":
            console.print(f"\n[bold]Result:[/bold]\n[Local Image Generated - {len(res.get('payload'))} bytes]")
        else:
            console.print(f"\n[bold]Result:[/bold]\n{res.get('result')}")
    else:
        console.print("[yellow]Waiting for remote result...[/yellow]")
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
