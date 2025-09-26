FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    scons \
    python3 \
    python3-dev \
    python3-pip \
    libprotobuf-dev \
    protobuf-compiler \
    libgoogle-perftools-dev \
    libpng-dev \
    libz-dev \
    libboost-all-dev \
    graphviz \
    m4 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pydot

WORKDIR /

RUN git clone https://gem5.googlesource.com/public/gem5

WORKDIR /gem5

RUN scons build/X86/gem5.opt -j $(nproc)

RUN scons -C util/m5 build/x86/out/m5

WORKDIR /data

CMD ["bash"]