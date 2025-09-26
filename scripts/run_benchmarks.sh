#!/bin/bash
set -e

GEM5_PATH="/gem5/build/X86/gem5.opt"
SCRIPT_PATH="./src/benchmark.py"
BASE_OUTPUT_DIR="./output"
BINARIES=("./bin/test")
BINARY_ARGS=("10")
PREDICTORS=("bimodal" "local" "tage" "perceptron" "none")
ROB_SIZES=("64" "128" "256")
PIPELINE_WIDTHS=("2" "8")
L1_SIZES=("16KiB" "64KiB")
L1_PREFETCHERS=("stride" "tagged")
L2_SIZES=("1MB" "4MB")
L2_PREFETCHERS=("stride" "tagged" "ampm" "signature")


for i in "${!BINARIES[@]}"; do
    bin_path="${BINARIES[i]}"
    bin_name=$(basename "$bin_path")
    binary_args="${BINARY_ARGS[i]}"
    echo "--- Starting simulations for binary: $bin_name ---"

    echo "Running Baseline..."
    out_dir="$BASE_OUTPUT_DIR/$bin_name/baseline"
    mkdir -p "$out_dir"
    $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --binary="$bin_path" --binary-args="$binary_args"

    for pred in "${PREDICTORS[@]}"; do
        echo "Sweeping Branch Predictor: $pred"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/pred_$pred"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --branch-pred="$pred" --binary="$bin_path" --binary-args="$binary_args"
    done

    for rob in "${ROB_SIZES[@]}"; do
        echo "Sweeping ROB Size: $rob"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/rob_$rob"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --rob-size="$rob" --binary="$bin_path" --binary-args="$binary_args"
    done

    for pw in "${PIPELINE_WIDTHS[@]}"; do
        echo "Sweeping Pipeline Width: $pw"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/pw_$pw"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --pipeline-width="$pw" --binary="$bin_path" --binary-args="$binary_args"
    done

    for l1s in "${L1_SIZES[@]}"; do
        echo "Sweeping L1 Size: $l1s"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l1s_$l1s"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l1-size="$l1s" --binary="$bin_path" --binary-args="$binary_args"
    done

    for l1p in "${L1_PREFETCHERS[@]}"; do
        echo "Sweeping L1 Prefetcher: $l1p"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l1p_$l1p"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l1-prefetcher="$l1p" --binary="$bin_path" --binary-args="$binary_args"
    done

    for l2s in "${L2_SIZES[@]}"; do
        echo "Sweeping L2 Size: $l2s"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l2s_$l2s"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l2-size="$l2s" --binary="$bin_path" --binary-args="$binary_args"
    done
    
    for l2p in "${L2_PREFETCHERS[@]}"; do
        echo "Sweeping L2 Prefetcher: $l2p"
        out_dir="$BASE_OUTPUT_DIR/$bin_name/l2p_$l2p"
        mkdir -p "$out_dir"
        $GEM5_PATH --outdir="$out_dir" "$SCRIPT_PATH" --l2-prefetcher="$l2p" --binary="$bin_path" --binary-args="$binary_args"
    done

    echo "--- Finished simulations for binary: $bin_name ---"
done

echo "All experiments complete!"