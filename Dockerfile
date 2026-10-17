FROM ubuntu:24.04

LABEL maintainer="VeloC Language Team"
LABEL description="Official VeloC systems programming language environment"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install toolchain and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    lld \
    ninja-build \
    cmake \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up workdir
WORKDIR /workspace

# Copy VeloC repository
COPY . /opt/veloc
RUN ln -s /opt/veloc/veloc.py /usr/local/bin/veloc && chmod +x /opt/veloc/veloc.py

# Install Python support tools
RUN pip install --no-cache-dir --break-system-packages pytest numpy ipykernel

# Register Jupyter kernel
RUN python3 -c "import sys; sys.path.insert(0, '/opt/veloc'); from src.jupyter_kernel import install_kernel; install_kernel()"

WORKDIR /project
CMD ["veloc", "--version"]
