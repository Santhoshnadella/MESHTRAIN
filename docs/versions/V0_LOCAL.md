# VERSION 0 — LOCAL NODE / SINGLE GPU

Goal:

Make MeshTrain useful even when only ONE machine exists.

Implement:

    meshtrain node start
    meshtrain status
    meshtrain benchmark
    meshtrain model
    meshtrain infer
    meshtrain train
    meshtrain tune

Capabilities:

    GPU detection
    CPU/RAM detection
    CUDA detection
    PyTorch runtime
    model loading
    local inference
    local fine-tuning
    LoRA
    QLoRA
    checkpointing
    local content-addressed storage
    metrics
    CLI
    localhost API

Architecture:

    CLI
      ↓
    Local API
      ↓
    MeshTrain Node
      ↓
    Runtime
      ↓
    GPU

No network required.

Acceptance:

    A user can install MeshTrain and run useful AI workloads
    completely offline.
