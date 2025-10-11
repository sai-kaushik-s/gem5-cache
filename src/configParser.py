import os
from argparse import ArgumentParser, REMAINDER
from constants import (
    BRANCH_PREDICTORS,
    CACHE_REPLACEMENT_POLICIES,
    CACHE_PREFETCHERS,
    CORE_ISA,
    NUM_CORES,
    CLK_FREQ,
    CPU_TYPE,
)


def setupConfig(args):
    branchPredictorKey = args.branch_pred.lower()
    if branchPredictorKey not in BRANCH_PREDICTORS:
        raise ValueError(f"Unknown branch predictor type: {branchPredictorKey}")

    coreConfig = {
        "predictor": BRANCH_PREDICTORS[branchPredictorKey],
        "robSize": args.rob_size,
        "iqSize": args.iq_size,
        "pipelineWidth": args.pipeline_width,
        "isa": CORE_ISA,
        "nCores": NUM_CORES,
        "clkFreq": CLK_FREQ,
        "cpuType": CPU_TYPE,
    }

    l1ReplacementPolicyKey = args.l1_replacement_policy
    if l1ReplacementPolicyKey not in CACHE_REPLACEMENT_POLICIES:
        raise ValueError(
            f"Unknown L1 replacement policy type: {l1ReplacementPolicyKey}"
        )

    l1PrefetcherKey = args.l1_prefetcher
    if l1PrefetcherKey not in CACHE_PREFETCHERS:
        raise ValueError(f"Unknown L1 prefetcher type: {l1PrefetcherKey}")

    l2ReplacementPolicyKey = args.l2_replacement_policy
    if l2ReplacementPolicyKey not in CACHE_REPLACEMENT_POLICIES:
        raise ValueError(
            f"Unknown L2 replacement policy type: {l2ReplacementPolicyKey}"
        )

    l2PrefetcherKey = args.l2_prefetcher
    if l2PrefetcherKey not in CACHE_PREFETCHERS:
        raise ValueError(f"Unknown L2 prefetcher type: {l2PrefetcherKey}")

    cacheConfig = {
        "l1Size": args.l1_size,
        "l1Associativity": args.l1_associativity,
        "l1ReplacementPolicy": CACHE_REPLACEMENT_POLICIES[l1ReplacementPolicyKey],
        "l1Prefetcher": CACHE_PREFETCHERS[l1PrefetcherKey],
        "l2Size": args.l2_size,
        "l2Associativity": args.l2_associativity,
        "l2ReplacementPolicy": CACHE_REPLACEMENT_POLICIES[l2ReplacementPolicyKey],
        "l2Prefetcher": CACHE_PREFETCHERS[l2PrefetcherKey],
    }

    binaryPath = args.binary
    if not os.path.isfile(binaryPath):
        raise FileNotFoundError(f"Binary not found at: {binaryPath}")

    workloadConfig = {
        "binary": binaryPath,
        "binaryArgs": args.binary_args[-1].split(" ") or [],
    }

    return coreConfig, cacheConfig, workloadConfig


def parseArguments():
    """Defines and parses command-line arguments for the gem5 simulation."""
    parser = ArgumentParser(
        description="A script to run benchmarks on a gem5 simulator for with different cache types."
    )

    parser.add_argument(
        "-pred",
        "--branch-pred",
        type=str,
        default="tournament",
        help="The branch predictor for the O3 CPU.",
        choices=list(BRANCH_PREDICTORS.keys()),
    )

    parser.add_argument(
        "-rob",
        "--rob-size",
        type=int,
        default=192,
        help="Size of the Re-Order Buffer for the O3 CPU.",
        choices=[64, 128, 192, 256],
    )

    parser.add_argument(
        "-iq",
        "--iq-size",
        type=int,
        default=64,
        help="Size of the Instruction Queue for the O3 CPU.",
        choices=[32, 64, 128],
    )

    parser.add_argument(
        "-pw",
        "--pipeline-width",
        type=int,
        default=4,
        help="Size of the Pipeline Width for the O3 CPU.",
        choices=[4, 8, 12],
    )

    parser.add_argument(
        "-l1s",
        "--l1-size",
        type=str,
        default="32KiB",
        help="Size of the L1 Cache for the O3 CPU.",
        choices=["16KiB", "32KiB", "64KiB"],
    )

    parser.add_argument(
        "-l1a",
        "--l1-associativity",
        type=int,
        default=4,
        help="Associativity of the L1 Cache for the O3 CPU.",
        choices=[2, 4, 8],
    )

    parser.add_argument(
        "-l1rp",
        "--l1-replacement-policy",
        type=str,
        default="plru",
        help="Replacement Policy for the L1 Cache for the O3 CPU.",
        choices=["plru", "lru", "random", "none"],
    )

    parser.add_argument(
        "-l1p",
        "--l1-prefetcher",
        type=str,
        default="none",
        help="Prefetcher for the L1 Cache for the O3 CPU.",
        choices=["stride", "tagged", "none"],
    )

    parser.add_argument(
        "-l2s",
        "--l2-size",
        type=str,
        default="256KiB",
        help="Size of the L2 Cache for the O3 CPU.",
        choices=["256KiB", "1MB", "4MB"],
    )

    parser.add_argument(
        "-l2a",
        "--l2-associativity",
        type=int,
        default=8,
        help="Associativity of the L2 Cache for the O3 CPU.",
        choices=[8, 16, 32],
    )

    parser.add_argument(
        "-l2rp",
        "--l2-replacement-policy",
        type=str,
        default="dueling",
        help="Replacement Policy of the L2 Cache for the O3 CPU.",
        choices=["dueling", "lru", "random", "none"],
    )

    parser.add_argument(
        "-l2p",
        "--l2-prefetcher",
        type=str,
        default="none",
        help="Prefetcher for the L2 Cache for the O3 CPU.",
        choices=["stride", "tagged", "ampm", "signature", "bop", "none"],
    )

    parser.add_argument(
        "-b",
        "--binary",
        type=str,
        required=True,
        help="Path to the binary file to be simulated",
    )

    parser.add_argument(
        "-ba",
        "--binary-args",
        nargs=REMAINDER,
        help="Any extra arguments to pass directly to the binary",
    )

    return parser.parse_args()
