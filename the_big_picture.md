# The Big Picture: MeshTrain & The Blockchain

MeshTrain has evolved from a simple Python networking script into a true **Layer-2 Decentralized AI State Channel**. 
This document outlines the final steps for pushing our economy onto the public blockchain, and paints the vision for what the future of MeshTrain holds.

---

## 1. The Final Step: Solana Devnet Deployment

Right now, the Python codebase is completely primed and ready to communicate with the Solana blockchain via the `solana` and `solders` SDKs. We have bypassed local ledger files in favor of building real cryptographic `VersionedTransactions`.

Once you have your local environment (Rust & Solana CLI) set up, here is the exact 4-step deployment process to push MeshTrain live:

### Step 1: Build the Smart Contract
Navigate to the `contracts/` directory and run:
```bash
anchor build
```
*This compiles the `lib.rs` Rust code into a deployable eBPF binary program.*

### Step 2: Link the Program ID
When the build finishes, Anchor generates a unique "Program ID" (the permanent public address of your smart contract). 
You must run `anchor keys list`, copy that ID, and paste it into two places:
1. `contracts/Anchor.toml`
2. `meshtrain/economy/solana_config.py` (The `MESHCOIN_PROGRAM_ID` variable)

### Step 3: Deploy to the Public Blockchain
With the ID linked, run:
```bash
anchor deploy
```
*This permanently publishes your custom MeshCoin smart contract to the global Solana Devnet. The contract is now a public entity that anyone can interact with.*

### Step 4: Run MeshTrain!
Start up your MeshTrain node (`meshtrain start`). 
Whenever your node completes a mathematically verified AI job (Proof-of-Compute), it will no longer save a local JSON receipt. Instead, it will automatically build a real blockchain transaction, sign it with its `ed25519` identity, and broadcast it to the Solana network. The Solana validators will execute your smart contract, verify the signature, and officially reward the worker with MeshCoins on the public ledger.

---

## 2. The Future: Where MeshTrain goes from here

Once the Devnet integration is proven, MeshTrain is ready to scale into a global, production-ready ecosystem. Here is the future roadmap:

### Mainnet Migration (Real Money)
The Devnet uses fake SOL for testing. The immediate next step is changing one string in `solana_config.py` from `devnet` to `mainnet-beta`. 
Once deployed to Mainnet, **MeshCoins become a real cryptocurrency** that can be traded on decentralized exchanges (DEXs) like Raydium or Orca. Users renting out their idle GPUs will literally be earning real financial value while they sleep.

### Decentralized Autonomous Organization (DAO)
Instead of a single "System Treasury" that controls the total supply of MeshCoins, the treasury will be handed over to a Smart Contract DAO. The community can vote on parameter changes—such as increasing the reward for fine-tuning jobs vs inference jobs—by staking their MeshCoins.

### Zero-Knowledge Proofs (zk-SNARKs)
Currently, our "Proof-of-Compute" relies on multi-routing (sending the same prompt to two peers and hashing their outputs to ensure consensus). While secure, this means we waste 50% of the network's compute power on verification. 
In the future, nodes will generate a **zk-SNARK** (a cryptographic proof) alongside their inference output. The smart contract will verify this math instantly, proving that the remote GPU actually ran the neural network correctly, without needing a second node to duplicate the work.

### Global Compute Fabric
Right now, you can request an LLM generation or a Stable Diffusion image. In the future, MeshTrain will support arbitrary Docker containers. You could submit a massive protein-folding simulation or a 3D rendering job, and the network will dynamically shard the workload across 10,000 idle gaming PCs around the world, paying them micro-transactions per second of compute via Solana. 

**MeshTrain isn't just an AI app anymore—it is the foundation for a decentralized AWS.**
