# VERSION 8 — ELASTIC DISTRIBUTED TRAINING

Goal:

Workers may join and leave during training.

Implement:

    elastic membership
    worker registration
    worker removal
    heartbeat
    failure detection
    task reassignment
    checkpoint recovery
    dynamic world size
    scheduler re-planning
    straggler detection
    worker replacement

Example:

    A B C D E

    C fails

    A B D E
      ↓
    scheduler
      ↓
    replace/rebalance
      ↓
    continue

Training must NOT restart from zero after a worker failure.
