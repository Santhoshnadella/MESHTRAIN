# VERSION 5 — DISTRIBUTED INFERENCE / MESHSERVE

Goal:

Turn the network into a distributed inference fabric.

Implement:

    model discovery
    model availability
    GPU capability matching
    VRAM matching
    latency-aware routing
    throughput-aware routing
    batching
    request routing
    model caching
    replica selection
    pipeline inference
    fault recovery

Routing:

    User
      ↓
    Local MeshTrain node
      ↓
    DHT
      ↓
    candidate peers
      ↓
    scheduler
      ↓
    selected GPU
      ↓
    inference
      ↓
    result

Support:

    local inference
    remote inference
    replicated inference
    pipeline inference
    regional inference

Provide:

    OpenAI-compatible API

but it must be optional.

Acceptance:

    A user can consume remote GPU inference without knowing
    where the GPU physically exists.
