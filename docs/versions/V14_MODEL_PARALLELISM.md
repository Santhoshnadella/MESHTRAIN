# VERSION 14 — ADVANCED MODEL PARALLELISM

Experimental.

Only implement after V1-V13 are stable.

Investigate:

    tensor parallelism
    pipeline parallelism
    expert parallelism
    mixture-of-experts
    sharded inference
    distributed KV cache
    heterogeneous model partitioning

IMPORTANT:

Do not force these techniques onto high-latency Internet links.

The scheduler must determine whether topology supports them.
