# Dockerfile for TempShell user pods
# Lightweight shell environment with essential tools

FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install essential tools in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    findutils \
    grep \
    sed \
    gawk \
    vim \
    nano \
    curl \
    wget \
    tree \
    file \
    less \
    git \
    python3 \
    python3-pip \
    tar \
    gzip \
    zip \
    unzip \
    jq \
    sudo \
    procps \
    net-tools \
    iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash tempuser && \
    echo "tempuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /home/tempuser
USER tempuser

ENV HOME=/home/tempuser \
    USER=tempuser \
    SHELL=/bin/bash \
    LANG=C.UTF-8

CMD ["sleep", "3600"]
