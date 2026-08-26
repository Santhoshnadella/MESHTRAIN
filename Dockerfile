# V15 Containerization for MeshTrain Worker Nodes
# Standard NVIDIA CUDA base image for native GPU execution
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Install Python and basic build tools
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install (if they existed, or we just install pyproject via pip)
COPY . /app/
RUN pip3 install --no-cache-dir -e .

# Expose libp2p port and FastAPI port
EXPOSE 8001
EXPOSE 8000

# Start MeshTrain as a background worker node with NAT Relay enabled
CMD ["meshtrain", "start", "--port", "8001", "--relay"]
