#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np

def safe_div(a, b):
    return np.where((b==0) | (pd.isna(b)), np.nan, a / b)

def amat_per_level(hit_time_cycles, hits, accesses, miss_ticks_total, misses, clk):
    hit_rate = safe_div(hits, accesses)
    miss_rate = 1.0 - hit_rate
    avg_miss_ticks = safe_div(miss_ticks_total, misses)
    if clk and clk > 0:
        miss_penalty_cycles = safe_div(avg_miss_ticks, clk)
    else:
        miss_penalty_cycles = np.nan
    amat = hit_time_cycles + miss_rate * miss_penalty_cycles
    amat = np.where(pd.isna(amat), hit_time_cycles, amat)
    return amat

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='metrics_raw.xlsx')
    ap.add_argument('--output', default='metrics_final.xlsx')
    ap.add_argument('--clock', type=float, default=0.0)
    ap.add_argument('--hit-l1', type=float, default=1.0)
    ap.add_argument('--hit-l2', type=float, default=10.0)
    args = ap.parse_args()

    clk = args.clock if args.clock and args.clock > 0 else None

    df = pd.read_excel(args.input, sheet_name='raw_metrics')

    run = df['run']
    ipc = df['board.processor.cores.core.ipc']
    simInsts = df['simInsts']

    l1d_hits = df['board.cache_hierarchy.l1dcaches.overallHits::total']
    l1d_accs = df['board.cache_hierarchy.l1dcaches.overallAccesses::total']
    l1d_miss = df['board.cache_hierarchy.l1dcaches.overallMisses::total']

    l1i_hits = df['board.cache_hierarchy.l1icaches.overallHits::total']
    l1i_accs = df['board.cache_hierarchy.l1icaches.overallAccesses::total']
    l1i_miss = df['board.cache_hierarchy.l1icaches.overallMisses::total']

    l2_hits = df['board.cache_hierarchy.l2caches.overallHits::total']
    l2_accs = df['board.cache_hierarchy.l2caches.overallAccesses::total']
    l2_miss = df['board.cache_hierarchy.l2caches.overallMisses::total']

    l1d_ticks = df['l1d.overallMissLatency::total']
    l1i_ticks = df['l1i.overallMissLatency::total']
    l2_ticks  = df['l2.overallMissLatency::total']

    br_com = df['branchPred.committed_0::total']
    br_mis = df['branchPred.mispredicted_0::total']
    squashed = df['commit.commitSquashedInsts']

    kinsts = safe_div(simInsts, 1000.0)

    L1D_HitRate = safe_div(l1d_hits, l1d_accs)
    L1I_HitRate = safe_div(l1i_hits, l1i_accs)
    L2_HitRate  = safe_div(l2_hits,  l2_accs)

    L1D_MPKI = safe_div(l1d_miss, kinsts)
    L1I_MPKI = safe_div(l1i_miss, kinsts)
    L2_MPKI  = safe_div(l2_miss,  kinsts)

    Br_MispredRate = safe_div(br_mis, br_com)

    L1D_AMAT = amat_per_level(args.hit_l1, l1d_hits, l1d_accs, l1d_ticks, l1d_miss, clk)
    L1I_AMAT = amat_per_level(args.hit_l1, l1i_hits, l1i_accs, l1i_ticks, l1i_miss, clk)
    L2_AMAT  = amat_per_level(args.hit_l2, l2_hits,  l2_accs,  l2_ticks,  l2_miss, clk)

    out = pd.DataFrame({
        'Run': run,
        'IPC': ipc,
        'L1D_HitRate': L1D_HitRate, 'L1I_HitRate': L1I_HitRate, 'L2_HitRate': L2_HitRate,
        'L1D_MPKI': L1D_MPKI, 'L1I_MPKI': L1I_MPKI, 'L2_MPKI': L2_MPKI,
        'L1D_AMAT': L1D_AMAT, 'L1I_AMAT': L1I_AMAT, 'L2_AMAT': L2_AMAT,
        'Br_MispredRate': Br_MispredRate,
        'Squashed': squashed,
    })

    with pd.ExcelWriter(args.output, engine='xlsxwriter') as writer:
        out.to_excel(writer, index=False, sheet_name='final_metrics')

    print(f"Wrote {len(out)} rows to {args.output}")

if __name__ == '__main__':
    main()
