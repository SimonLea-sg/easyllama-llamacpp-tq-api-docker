# llama-control — TurboQuant-capable llama.cpp runtime with FastAPI control plane
# Builds llama-server from the TurboQuant fork, then packages qllama as the public service.
# Uses ubuntu24.04, 

FROM nvidia/cuda:12.8.1-devel-ubuntu24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    gcc-14 \
    g++-14 \
    cmake \
    build-essential \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    libssl-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV CC=gcc-14 CXX=g++-14 CUDAHOSTCXX=g++-14

WORKDIR /build

# CRITICAL: Must use --branch feature/turboquant-kv-cache
# Default 'master' does NOT have turbo2/turbo3/turbo4 cache types.
RUN git clone https://github.com/TheTom/llama-cpp-turboquant.git \
    --branch feature/turboquant-kv-cache \
    --depth=1

WORKDIR /build/llama-cpp-turboquant

# Fix: libcuda.so.1 is not available at build time (driver is injected at runtime only).
RUN ln -sf /usr/local/cuda/lib64/stubs/libcuda.so \
           /usr/local/cuda/lib64/stubs/libcuda.so.1 \
    && echo "/usr/local/cuda/lib64/stubs" > /etc/ld.so.conf.d/cuda-stubs.conf \
    && ldconfig

RUN cmake -B build \
    -DGGML_CUDA=ON \
    -DGGML_NATIVE=OFF \
    -DGGML_BACKEND_DL=ON \
    -DGGML_CPU_ALL_VARIANTS=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_EXE_LINKER_FLAGS=-Wl,--allow-shlib-undefined .&& \
    cmake --build build --config Release -j4 --target llama-server

FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY --from=builder /build/llama-cpp-turboquant/build/bin /opt/llama/bin
RUN ln -sf /opt/llama/bin/llama-server /usr/local/bin/llama-server \
    && echo "/opt/llama/bin" > /etc/ld.so.conf.d/llama-bin.conf \
    && ldconfig

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt /tmp/requirements.txt

RUN python3 -m venv .venv \
    && . .venv/bin/activate \
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r /tmp/requirements.txt
   
RUN rm /tmp/requirements.txt

COPY api/ /app/api/
COPY docker/.env /app/api/.env

RUN mkdir -p /models

COPY ./docker/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000 8080

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8000/health >/dev/null || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

