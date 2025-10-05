# Performance Impact of OoO Execution and Speculation in gem5

**Author:** Sai Kaushik S (2025CSZ8470) and Yosep Ro (2025ANZ8223)

**Course:** Architecture of High Performance System

**Instructor:** Dr. Kolin Paul

## Overview

This project explores the interaction between out-of-order (OoO) execution, branch and memory speculation, and a two-level cache hierarchy using the gem5 simulator. The primary objective is to quantify the effect of these microarchitectural features on key performance metrics such as Instructions Per Cycle (IPC), Average Memory Access Time (AMAT), cache behavior, and effective stall cycles. All simulations are conducted in gem5's Syscall Emulation (SE) mode to ensure a controlled environment free from OS interference.

## Simulated Microarchitecture

The gem5 configuration is built around the following core components:

- **CPU Model:** The DerivO3CPU model is used to simulate a complex out-of-order processor.
- **Cache Hierarchy:** A two-level cache system is implemented, featuring:
  - Private L1 Instruction and Data caches.
  - A shared L2 cache.
- **Speculation:** A configurable branch predictor to manage control flow speculation.
- **Replacement Policies:** A configurable replacement policies for both levels of caches
- **Prefetchers:** A configurable prefetecher for both levels of caches

## Microbenchmarks

To stress different aspects of the microarchitecture, three categories of C/C++ microbenchmarks are used:

- **Compute-bound Kernel:** Features ALU-intensive loops designed to test the limits of OoO execution.
- **Pointer-chasing Kernel:** Involves linked-list traversal to evaluate the effectiveness of memory dependence speculation.
- **Streaming Kernel:** Utilizes sequential array accesses to analyze cache prefetching and L1/L2 cache behavior.

## Experimental Design

For each microbenchmark, a design space exploration is performed by sweeping the following parameters:

- **OoO CPU Parameters:** Reorder Buffer (ROB) size, and issue/commit width.
- **L1/L2 Cache Parameters:** Cache size, associativity, and replacement policy, prefetchers
- **Branch Speculation:** Toggling between enabled/disabled and testing different predictor types.

## Getting Started

### Prerequisites

Before running this project, make sure you have **Docker** installed on your system.  
You can download and install Docker from the official website: [https://www.docker.com/get-started](https://www.docker.com/get-started)

### Build the Docker Image

To build a Docker container with the latest gem5 repository, run the following command:

```sh
docker build -t gem5-cache .
```

This command creates a Docker image named `gem5-cache` using the Dockerfile in the current directory.

### Run the Docker Container

To run the Docker container interactively and mount the current directory into the container at `/data`, use:

```sh
docker run -it -v .:/data gem5-cache
```

This lets you work inside the container with access to your current host directory at `/data`.

### Compiling custom binaries

To cross-compile the C/C++ microbenchmarks for the ISA supported by your gem5 build.

```sh
./scripts/build_binaries.sh <path-to-the-cpp-file>
```

The compiled binary will be present in the `bin` directory.

### Running the benchmark

Execute the script to run the benchmarks on different inputs.

```bash
./scripts/run_benchmark.sh
```

## Results

Raw simulation results, including detailed statistics, are stored in the `stats.txt` file for each run inside the `output/` directory.

A summary of the most important metrics from all runs can be aggregated by the `analysis/main.ipynb` for plotting and analysis.

The main metrics will be generated on execution at `analysis/simResults.csv` and `analysis/simResults.json`. The different plots can be found within `analysis/figs`.
