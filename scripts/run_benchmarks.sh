#!/bin/bash
set -e

GEM5_PATH="/gem5/build/X86/gem5.opt"
SCRIPT_PATH="./src/benchmark.py"
BASE_OUTPUT_DIR="./output"
BINARIES=("./bin/compute" "./bin/pointer" "./bin/stream")
BINARY_ARGS=("1048576" "65536 4" "1048576 1")
PREDICTORS=("bimodal" "local" "tage" "perceptron" "none")
ROB_SIZES=("64" "128" "256")
PIPELINE_WIDTHS=("8" "12")
L1_SIZES=("16KiB" "64KiB")
L1_ASSOCIATIVITY=("2" "8")
L1_PREFETCHERS=("stride" "tagged")
L1_REPLACEMENT_POLICIES=("plru" "lru" "random")
L2_SIZES=("1MB" "4MB")
L2_ASSOCIATIVITY=("16" "32")
L2_PREFETCHERS=("stride" "tagged" "ampm" "signature")
L2_REPLACEMENT_POLICIES=("dueling" "lru" "random")


for i in "${!BINARIES[@]}"; do
    bin_path="${BINARIES[i]}"
    bin_name=$(basename "$bin_path")
    binary_args="${BINARY_ARGS[i]}"
    echo "--- Starting simulations for binary: $bin_name ---"

    echo "Running Baseline..."
    out_dir="$BASE_OUTPUT_DIR/$bin_name/baseline"
    mkdir -p "$out_dir"
    $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"

    for pred in "${PREDICTORS[@]}"; do
        echo "Sweeping Branch Predictor: $pred"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/pred_$pred"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --branch-pred="$pred" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for rob in "${ROB_SIZES[@]}"; do
        echo "Sweeping ROB Size: $rob"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/rob_$rob"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --rob-size="$rob" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for pw in "${PIPELINE_WIDTHS[@]}"; do
        echo "Sweeping Pipeline Width: $pw"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/pw_$pw"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --pipeline-width="$pw" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l1s in "${L1_SIZES[@]}"; do
        echo "Sweeping L1 Size: $l1s"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l1s_$l1s"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l1-size="$l1s" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l1a in "${L1_ASSOCIATIVITY[@]}"; do
        echo "Sweeping L1 Associativity: $l1a"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l1a_$l1a"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l1-associativity="$l1a" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l1rp in "${L1_REPLACEMENT_POLICIES[@]}"; do
        echo "Sweeping L1 Replacement Policy: $l1rp"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l1rp_$l1rp"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l1-replacement-policy="$l1rp" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l1p in "${L1_PREFETCHERS[@]}"; do
        echo "Sweeping L1 Prefetcher: $l1p"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l1p_$l1p"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l1-prefetcher="$l1p" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l2s in "${L2_SIZES[@]}"; do
        echo "Sweeping L2 Size: $l2s"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l2s_$l2s"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l2-size="$l2s" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l2a in "${L2_ASSOCIATIVITY[@]}"; do
        echo "Sweeping L2 Associativity: $l2a"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l2a_$l2a"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l2-associativity="$l2a" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    for l2rp in "${L2_REPLACEMENT_POLICIES[@]}"; do
        echo "Sweeping L2 Replacement Policy: $l2rp"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l2rp_$l2rp"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l2-replacement-policy="$l2rp" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done
    
    for l2p in "${L2_PREFETCHERS[@]}"; do
        echo "Sweeping L2 Prefetcher: $l2p"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l2p_$l2p"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l2-prefetcher="$l2p" --binary="$bin_path" --binary-args="$binary_args" > "$out_dir/sim.out" 2> "$out_dir/sim.err"
    done

    echo "--- Finished simulations for binary: $bin_name ---"
done

echo "All experiments complete!"