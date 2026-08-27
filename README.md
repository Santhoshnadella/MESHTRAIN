![MeshTrain Architecture Banner](banner.jpg)

# MeshTrain: The Decentralized AI Compute Mesh

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/Status-Beta-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()


Welcome to **MeshTrain**, a production-grade, zero-trust, peer-to-peer network designed to democratize AI compute. MeshTrain allows anyone to run or train massive AI models (like LLMs or Stable Diffusion) by dynamically borrowing GPU power from a global network of peers, creating a giant decentralized supercomputer.

## 📖 The "Real World" Analogy
Think of MeshTrain as **Airbnb for GPUs combined with BitTorrent**. 
If you have an old laptop and you want to generate a heavy Stable Diffusion image, you don't have the hardware for it. Meanwhile, someone in Tokyo is asleep with a massive RTX 4090 sitting idle. 
MeshTrain connects you directly to that idle GPU over an encrypted peer-to-peer network. Your prompt is sent to Tokyo, the image is generated, and streamed back to you. In return, the node in Tokyo automatically earns a "MeshCoin" on their local ledger. 

No central servers. No AWS bills. No corporate gatekeepers.

---

## 🌟 Core Capabilities

### 1. Decentralized Inference (Running Models)
- **Text Generation:** You can send a prompt to the network, and a remote GPU will load a HuggingFace LLM (like Llama-3 or GPT-2) and stream the text back to you.
- **Image Generation (Multi-Modal):** We added support for binary payloads, meaning you can send a prompt to the network and a remote GPU will run `diffusers` (Stable Diffusion) and return a raw PNG image.

### 2. Distributed Fine-Tuning (Training)
You can provide a custom `.jsonl` dataset and a target model. MeshTrain will send it to a remote GPU with enough VRAM, train a LoRA adapter on their hardware, and send the completed `.bin` adapter file back to you.

### 3. True Federated Learning (Swarm Training)
If your dataset is huge, you can specify `--peers 5`. MeshTrain will chop your dataset into 5 pieces, send them to 5 different GPUs around the world simultaneously, wait for all of them to finish training, and then mathematically average their weights together using the `FederatedAverager`.

### 4. Decentralized Dataset Hosting (MeshDrive)
Before a node can train, it needs the data. You built the `ContentStore` which acts like BitTorrent. You can upload gigabytes of training data to the network, and peers can request chunks of it securely without overwhelming a single server.

### 5. Monetizing Idle Hardware (GPU Renting)
Anyone with a gaming PC can just run `meshtrain start` and walk away. Their PC will passively accept safe, sandboxed jobs from the internet and automatically accumulate MeshCoins into their local SQLite ledger while they sleep.

*You didn't just build a tool to run AI; you built an entire decentralized cloud provider!*

---

## 🛠️ The Tech Stack
Built for speed, security, and scalability.
- **Core App**: Python 3.10+
- **P2P Networking**: `py-libp2p` (Kademlia DHT, SECIO encryption, multiplexing)
- **AI Execution**: `transformers`, `peft` (LoRA), `diffusers` (Stable Diffusion)
- **Data Serialization**: `protobuf` (Protocol Buffers)
- **Economy**: Local `sqlite3` ledger
- **Desktop UI**: `Electron`, `FastAPI`, Vanilla HTML/CSS/JS (Glassmorphism design)

---

## 🧠 Data & Logic Flow: How it Works

When you run a command like `meshtrain infer gpt2 "The future is..."`, here is the exact lifecycle of what happens under the hood:

### 1. Peer Discovery (Kademlia DHT)
Your node starts up and reaches out to the **Global DHT (Distributed Hash Table)**. It asks the network: *"Who is currently online and providing MeshTrain compute services?"* The DHT responds with a list of encrypted PeerIDs and their IP addresses.

### 2. Hardware Capability Routing
Not all nodes are created equal. Your `JobPlanner` evaluates the remote nodes based on their advertised hardware capabilities. If you are generating text, it looks for nodes with at least 2GB of VRAM. If you are generating a heavy image, it filters for nodes with 8GB+ VRAM.

### 3. MeshDrive: P2P Data Distribution
If you are running a heavy LoRA fine-tuning job (MeshTune), you need to send a large `.jsonl` dataset to the worker node. Instead of uploading a huge file, MeshTrain uses **MeshDrive**. It breaks your dataset into tiny 5MB chunks, generates a cryptographic manifest, and pins those chunks to random peers on the network. The worker node dynamically downloads the chunks from the swarm, just like BitTorrent.

### 4. MeshProtect: The Security Sandbox
When the remote node receives your request, it doesn't just blindly run code. The Execution Engine is wrapped in **MeshProtect**—a strict Python `SecurityContext` that disables `trust_remote_code` and locks down the environment. This ensures malicious users cannot trick the network into running harmful scripts.

### 5. Proof of Compute & Consensus Verification
How do you know the remote node didn't just return garbage text to steal your MeshCoins? 
MeshTrain routes your prompt to **multiple peers simultaneously**. The local `ConsensusEngine` mathematically calculates the `SHA-256` hash of their responses. Only if there is a strict cryptographic majority matching hash is the compute verified!

### 6. Economy & MeshCoin (Cryptographic Ledger)
Once the compute is verified, the transaction is cryptographically signed using `ed25519`. The `SignedTransactionLedger` verifies the signature and writes it to the distributed log, crediting the remote worker with MeshCoins automatically priced by the `DynamicPricer` based on model size and token length.

---

## 🛡️ Security Architecture (Technical Deep Dive)

MeshTrain operates on a **Zero-Trust** philosophy. Because you are executing AI models from anonymous nodes across the internet, security is paramount:

1. **Encrypted Transport**: All peer-to-peer traffic is multiplexed and encrypted using `libp2p`'s native SECIO / TLS-like handshakes. Eavesdropping on dataset transmission is mathematically impossible.
2. **MeshProtect (Process Sandbox)**: Loading a model in Python is notoriously dangerous. When a worker node receives a request, the `MeshNode` execution engine spawns a fully isolated native OS process via `multiprocessing`. If the model crashes, OOMs, or is malicious, the child process is killed without affecting the main node.
3. **Model Provenance (Signature Verification)**: Before loading any weights, the `ModelVerifier` ensures the `SHA-256` hash of the model precisely matches the `ed25519` cryptographic signature of its trusted author.
4. **Cryptographic Hash Consensus (Proof of Compute)**: To prevent a malicious worker node from returning random garbage text to farm MeshCoins, the `InferenceRouter` utilizes a multi-routing protocol. The local `ConsensusEngine` checks for a strict `SHA-256` hash majority among the peers. If they don't match, the results are rejected, the nodes' reputations are penalized, and no MeshCoins are minted.

---

## 🤝 Contributing Guide

We welcome contributions from the community! To get started:

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/Santhoshnadella/MESHTRAIN.git
   cd MESHTRAIN
   ```
2. **Set up a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```
3. **Make your Changes**: Create a new branch (`git checkout -b feature/amazing-idea`).
4. **Commit your Code**:
   - Write clear, descriptive commit messages.
   - Example: `git commit -m "feat(security): enhance consensus algorithm threshold"`
5. **Push and Open a PR**:
   ```bash
   git push origin feature/amazing-idea
   ```
   Head to GitHub and open a Pull Request. We review all PRs within 48 hours!

---

## 📂 Developer Folder Structure

If you want to contribute, here is how the codebase is organized:
```text
meshtrain/
├── meshtrain/
│   ├── cli/            # CLI commands (start, infer, tune, balance, ui)
│   ├── network/        # libp2p Host, Kademlia DHT, and Protocol Handlers
│   ├── inference/      # InferenceRouter & ConsensusEngine
│   ├── finetuning/     # LoRATuner for parameter-efficient distributed training
│   ├── storage/        # ContentStore (MeshDrive) for chunking datasets
│   ├── security/       # MeshProtect SecurityContext Sandbox
│   ├── economy/        # SQLite CreditLedger for MeshCoin tracking
│   ├── node/           # MeshNode local AI runtime (Transformers/Diffusers)
│   └── ui/             # FastAPI backend & Premium Electron Desktop App
├── protocols/          # .proto schema definitions (Node, Inference, Training, Storage)
└── pyproject.toml      # Dependency management
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js (for the Electron UI)
- `pip install -r requirements.txt` (or install via poetry/pipenv)

### Launching the Premium Desktop App
MeshTrain comes with a stunning, native desktop interface powered by Electron and a FastAPI Python backend.

```bash
# From the root directory:
meshtrain ui
```
This will automatically boot the local P2P network bridge on port 8000 and open the native window. You can check your MeshCoin balance, see connected peers, and run Text/Image generations right from the GUI!

### Using the CLI
If you prefer the terminal, MeshTrain provides a powerful command-line interface:

**Start a passive worker node (Earn MeshCoins):**
```bash
meshtrain start --port 8001
```

**Check your earned balance:**
```bash
meshtrain balance
```

**Run Decentralized Inference (Consensus Verified):**
```bash
meshtrain infer gpt2 "Decentralized AI is" 
```

**Run Multi-Modal Image Generation:**
```bash
meshtrain infer stable-diffusion-v1-5 "A cyberpunk city at night" --modality image
```

**Run Decentralized LoRA Fine-Tuning:**
```bash
meshtrain tune gpt2 my_dataset.jsonl
```

---

## 📊 Project Status & Progress

MeshTrain is being built in structured phases. Here is the current progress:

### ✅ Ready to Use (Completed)
- **V0-V5 (Foundations & Networking)**: Kademlia DHT, `libp2p` secure encrypted streams, auto-reconnects, and hardware benchmarking.
- **V6 (MeshTune)**: Distributed LoRA fine-tuning utilizing HuggingFace `peft`. Remote nodes train adapters and stream the binary weights back over the network.
- **V7 (MeshDrive)**: Content-addressed storage for chunking and replicating datasets across the P2P swarm.
- **V8 (Proof of Compute)**: `ConsensusEngine` utilizing `SHA-256` cryptographic hash majority voting.
- **V9 (Tokenomics)**: `SignedTransactionLedger` with `ed25519` cryptographic signatures replacing the old SQLite mock.
- **V10 (Multi-Modal)**: Binary payload streaming to support `diffusers` image generation alongside text.
- **V11 (MeshProtect Sandbox)**: True OS-level process isolation using `multiprocessing` to run AI models safely.
- **V12 (Model Provenance)**: Verifying model integrity via cryptographic signatures before loading.
- **V13 (Federated Learning)**: Robust Dataset-Weighted `FederatedAverager` for merging multi-node LoRA weights, with distributed checkpointing.
- **V14 (API & DX)**: Full OpenAI-compatible FastAPI server (`api_server.py`) and gorgeous `rich` CLI progress reporting.
- **V15 (Inference Hardening)**: Automatic `bitsandbytes` 8-bit quantization for VRAM efficiency, plus dynamic caching.
- **V16 (Production Packaging)**: Optional dependency groups (`pyproject.toml`), `Dockerfile` support, and GitHub Actions CI pipelines.

### ⏳ Still Pending (Future Roadmap)
- **Solana Devnet Deployment**: The Python codebase and Rust smart contracts are complete. The final step is to build, deploy, and link the Solana smart contract (see `the_big_picture.md` for exact steps).
- **Mainnet Migration**: Migrating from Devnet to Mainnet-Beta to give MeshCoins real financial value.
- **DAO Integration**: Handing treasury control to a smart contract DAO.
- **zk-SNARKs**: Upgrading verification to zero-knowledge proofs.
- **Arbitrary Docker Workloads**: Expanding beyond AI to general global compute.
