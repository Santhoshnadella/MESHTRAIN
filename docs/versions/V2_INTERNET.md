# VERSION 2 — REAL INTERNET MESH

Goal:

Make MeshTrain work across real consumer Internet conditions.

Implement:

    NAT detection
    hole punching
    relay fallback
    connection migration
    NAT timeout handling
    CGNAT compatibility where possible
    firewall-aware connection strategy
    peer reachability scoring
    latency measurement
    bandwidth measurement
    jitter measurement
    packet-loss measurement

Architecture:

    Peer A
      │
      ├── direct
      ├── hole punch
      └── relay fallback
                │
                ▼
              Peer B

Important:

Relay nodes MUST NOT become mandatory compute servers.

A relay only forwards traffic when direct connectivity fails.

Acceptance:

    Nodes behind ordinary home routers can participate.
