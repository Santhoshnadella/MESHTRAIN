# VERSION 1 — TWO-NODE P2P MESH

Goal:

Two machines can discover and communicate directly.

Implement:

    peer identity
    cryptographic identity
    peer discovery
    handshake
    encrypted transport
    QUIC
    DHT
    peer capability advertisement
    heartbeat
    peer health
    direct task execution
    result verification

Architecture:

    Node A
       ↕
    P2P
       ↕
    Node B

Required:

    DHT
    peer IDs
    signed capability advertisements
    protocol versioning
    connection lifecycle
    retries
    timeout
    backpressure

Acceptance:

    Two computers on different networks can discover/connect
    without a central compute server.
