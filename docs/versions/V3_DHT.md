# VERSION 3 — DECENTRALIZED PEER DISCOVERY

Goal:

Remove dependence on a centralized peer registry.

Implement:

    DHT
    peer announcements
    capability records
    model provider records
    job advertisements
    TTL
    record expiration
    signed records
    peer reputation metadata
    stale-peer cleanup

Example:

    DHT
     │
     ├── GPU providers
     ├── model providers
     ├── relay providers
     ├── compute peers
     └── storage peers

Acceptance:

    A new node can join the network using only bootstrap information
    and subsequently discover peers through the distributed network.
