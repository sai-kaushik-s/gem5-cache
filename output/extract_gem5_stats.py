#!/usr/bin/env python3
"""
extract_gem5_stats.py

Scan subdirectories for gem5 stats.txt files, extract key metrics, compute derived values,
and write a single CSV summary.

Usage:
  python3 extract_gem5_stats.py --root . --output gem5_metrics.csv --weights 1 4 40

- --root:   base directory to scan (default: .)
- --output: output CSV filename (default: gem5_metrics.csv)
- --weights: energy proxy weights (wL1 wL2 wDRAM), default: 1 4 40
"""

import argparse
import os
import re
import csv
from collections import defaultdict

NUM_RE = re.compile(r'^-?\d+(\.\d+)?(e[+-]?\d+)?$', re.IGNORECASE)

def parse_stats_file(path):
    """
    Parse gem5 stats.txt into a dict: key -> float value
    Accepts lines like: 'system.cpu.numCycles  12345   # comment'
    Keeps original keys (verbatim), but also stores simplified variants
    (stripped of whitespace) for fuzzy matching fallback.
    """
    stats = {}
    if not os.path.isfile(path):
        return stats

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Typical format: <key> <value> [# ...]
            # Keys may contain dots, underscores, colons, etc.
            parts = line.split()
            if len(parts) < 2:
                continue
            key = parts[0]
            # Value may sometimes be in the second token; ignore trailing tokens/comments.
            val_token = parts[1]
            # Some lines have '=' or ':' or commas; try to sanitize minimally.
            val_token = val_token.strip().strip('=,:')
            if not NUM_RE.match(val_token):
                # Try the next token if it exists and is numeric
                if len(parts) >= 3 and NUM_RE.match(parts[2]):
                    val_token = parts[2]
                else:
                    continue
            try:
                val = float(val_token)
            except Exception:
                continue

            stats[key] = val
            # Also store "normalized" key for fuzzy lookups: remove punctuation (except alnum)
            norm_key = normalize_key(key)
            stats[norm_key] = val
    return stats

def normalize_key(k: str) -> str:
    # Lowercase, remove non-alphanumeric characters for broad fuzzy matching
    # but keep alnum only.
    return re.sub(r'[^a-z0-9]', '', k.lower())

def find_first(stats, key_patterns, default=None, prefer_total=True):
    """
    Search for a value in stats by trying multiple candidate patterns.
    - key_patterns: list of exact keys (first), then list of substring patterns (fuzzy).
    We attempt exact keys first (original), then normalized exact, then fuzzy contains.
    If prefer_total is True, we prefer keys that include '::total' if many candidates exist.
    """
    # 1) Try exact (verbatim) matches
    for k in key_patterns:
        if isinstance(k, str) and k in stats:
            return stats[k]

    # 2) Try exact normalized matches
    norm_map = {normalize_key(k): k for k in stats.keys() if ' ' not in k}
    for k in key_patterns:
        if not isinstance(k, str):
            continue
        nk = normalize_key(k)
        if nk in norm_map:
            return stats[norm_map[nk]]

    # 3) Fuzzy contains in original keys: all substrings must appear
    #    key_patterns here can be tuples/lists meaning "all tokens must be present"
    candidates = []
    for k in stats.keys():
        k_low = k.lower()
        for pat in key_patterns:
            if isinstance(pat, (list, tuple)):
                if all(p.lower() in k_low for p in pat):
                    candidates.append(k)
            else:
                if pat.lower() in k_low:
                    candidates.append(k)

    # Prefer ::total variants if requested
    if prefer_total:
        total_candidates = [c for c in candidates if '::total' in c]
        if total_candidates:
            # If multiple, pick the "longest" (most specific)
            best = sorted(total_candidates, key=len)[-1]
            return stats[best]

    if candidates:
        best = sorted(candidates, key=len)[-1]
        return stats[best]

    return default

def sum_all(stats, include_patterns):
    """
    Sum all values whose keys match ALL substrings in include_patterns (fuzzy AND).
    """
    s = 0.0
    for k, v in stats.items():
        if ' ' in k:
            continue
        k_low = k.lower()
        if all(p.lower() in k_low for p in include_patterns):
            s += v
    return s

def compute_ipc(stats):
    # 1) direct IPC
    direct = find_first(stats, [
        'board.processor.cores0.core.ipc',
        'board.processor.cores.core.ipc',
        'system.cpu.ipc',
    ])
    if direct is not None:
        return direct

    # 2) committedInsts / numCycles
    committed = find_first(stats, [
        'board.processor.cores0.core.committedInsts',
        'board.processor.cores.core.committedInsts',
        'system.cpu.commit.committedInsts',
        'system.cpu.committedInsts',
    ])

    num_cycles = find_first(stats, [
        'board.processor.cores0.core.numCycles',
        'board.processor.cores.core.numCycles',
        'system.cpu.numCycles',
    ])

    if committed is not None and num_cycles is not None and num_cycles > 0:
        return committed / num_cycles

    # 3) sim_insts / sim_ticks/clock
    sim_insts = find_first(stats, ['sim_insts', 'simInsts'])
    sim_ticks = find_first(stats, ['sim_ticks', 'simTicks'])
    clock = find_first(stats, [
        'board.clk_domain.clock',
        'system.clk_domain.clock',
        'system.cpu_clk_domain.clock',
    ])
    if sim_insts is not None and sim_ticks and clock and clock > 0:
        cycles = sim_ticks / clock
        if cycles > 0:
            return sim_insts / cycles

    return None

def get_cycles(stats):
    # Prefer explicit numCycles
    num_cycles = find_first(stats, [
        'board.processor.cores0.core.numCycles',
        'board.processor.cores.core.numCycles',
        'system.cpu.numCycles',
    ])
    if num_cycles is not None:
        return num_cycles

    sim_ticks = find_first(stats, ['sim_ticks', 'simTicks'])
    clock = find_first(stats, [
        'board.clk_domain.clock',
        'system.clk_domain.clock',
        'system.cpu_clk_domain.clock',
    ])
    if sim_ticks and clock and clock > 0:
        return sim_ticks / clock
    return None

def get_sim_insts(stats):
    s = find_first(stats, ['sim_insts', 'simInsts'])
    if s is not None:
        return s
    # fallback to committedInsts
    s = find_first(stats, [
        'board.processor.cores0.core.committedInsts',
        'board.processor.cores.core.committedInsts',
        'system.cpu.commit.committedInsts',
        'system.cpu.committedInsts',
    ])
    return s

def cache_block(stats, level_tag):
    """
    Extract cache accesses/hits/misses and avg miss latency for given level.
    level_tag examples:
      ('l1dcaches', 'L1D')
      ('l1icaches', 'L1I')
      ('l2cache',   'L2')
    Returns dict with keys:
      accesses, hits, misses, hit_rate, mpki (mpki needs sim_insts passed separately),
      miss_latency_ticks
    """
    tag, label = level_tag
    acc = find_first(stats, [[tag, 'overallaccesses']])
    hits = find_first(stats, [[tag, 'overallhits']])
    misses = find_first(stats, [[tag, 'overallmisses']])
    miss_lat = find_first(stats, [[tag, 'overallavgmisslatency']])
    # Some builds use camel-case or underscores; fuzzy search should catch.

    # If only hits or accesses present, derive misses if possible
    if misses is None and acc is not None and hits is not None:
        misses = max(0.0, acc - hits)

    hit_rate = None
    if acc and hits is not None and acc > 0:
        hit_rate = hits / acc

    return {
        'label': label,
        'accesses': acc,
        'hits': hits,
        'misses': misses,
        'hit_rate': hit_rate,
        'miss_latency_ticks': miss_lat,
    }

def branch_mispred(stats):
    # Try common variants
    mis = find_first(stats, [
        'system.cpu.branchPred.mispredicted_0::total',
        'branchPred.mispredicted_0::total',
        ['branchpred', 'mispredicted'],
    ])
    com = find_first(stats, [
        'system.cpu.branchPred.committed_0::total',
        'branchPred.committed_0::total',
        ['branchpred', 'committed'],
    ])
    rate = None
    if mis is not None and com and com > 0:
        rate = mis / com
    return mis, com, rate

def memdep_conflicts(stats):
    # Sum across any MemDepUnit instances/threads
    loads_inserted = sum_all(stats, ['memdepunit', 'insertedloads'])
    loads_conf = sum_all(stats, ['memdepunit', 'conflictingloads'])
    stores_inserted = sum_all(stats, ['memdepunit', 'insertedstores'])
    stores_conf = sum_all(stats, ['memdepunit', 'conflictingstores'])

    load_rate = (loads_conf / loads_inserted) if loads_inserted > 0 else None
    store_rate = (stores_conf / stores_inserted) if stores_inserted > 0 else None
    return loads_inserted, loads_conf, load_rate, stores_inserted, stores_conf, store_rate

def pipeline_flush(stats):
    bm = find_first(stats, [
        'system.cpu.commit.branchMispredicts',
        'commit.branchMispredicts',
        ['commit', 'branchmispredicts'],
    ])
    squashed = find_first(stats, [
        'system.cpu.commit.commitSquashedInsts',
        'commit.commitSquashedInsts',
        ['commit', 'squashedinsts'],
    ])
    return bm, squashed

def dram_stats(stats):
    rd = find_first(stats, [['memory', 'module', 'numreads']])
    wr = find_first(stats, [['memory', 'module', 'numwrites']])
    rdb = find_first(stats, [['memory', 'module', 'bytesread']])
    wrb = find_first(stats, [['memory', 'module', 'byteswritten']])
    return rd or 0.0, wr or 0.0, rdb or 0.0, wrb or 0.0

def clock_ticks_per_cycle(stats):
    clk = find_first(stats, [
        'board.clk_domain.clock',
        'system.clk_domain.clock',
        'system.cpu_clk_domain.clock',
    ])
    return clk

def amat(hit_rate, miss_penalty_cycles, hit_time_cycles=1.0):
    if hit_rate is None or miss_penalty_cycles is None:
        return None
    miss_rate = 1.0 - hit_rate
    return hit_time_cycles + miss_rate * miss_penalty_cycles

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.', help='Root directory to scan recursively for stats.txt')
    ap.add_argument('--output', default='gem5_metrics.csv', help='Output CSV filename')
    ap.add_argument('--weights', nargs=3, type=float, default=[1.0, 4.0, 40.0],
                    help='Energy proxy weights: wL1 wL2 wDRAM')
    args = ap.parse_args()

    records = []

    # Walk the root and find all stats.txt files
    stats_files = []
    for dirpath, dirnames, filenames in os.walk(args.root):
        if 'stats.txt' in filenames:
            stats_files.append(os.path.join(dirpath, 'stats.txt'))

    if not stats_files:
        print("No stats.txt found under:", args.root)
        return

    for spath in sorted(stats_files):
        stats = parse_stats_file(spath)
        run_name = os.path.basename(os.path.dirname(spath))

        ipc = compute_ipc(stats)
        cycles = get_cycles(stats)
        sim_insts = get_sim_insts(stats)
        clk = clock_ticks_per_cycle(stats)

        # Caches
        l1d = cache_block(stats, ('l1dcaches', 'L1D'))
        l1i = cache_block(stats, ('l1icaches', 'L1I'))
        l2  = cache_block(stats, ('l2cache',   'L2'))

        # MPKI
        def mpki(misses, sim_insts):
            if misses is None or sim_insts in (None, 0):
                return None
            return misses / (sim_insts / 1000.0)

        l1d_mpki = mpki(l1d['misses'], sim_insts)
        l1i_mpki = mpki(l1i['misses'], sim_insts)
        l2_mpki  = mpki(l2['misses'],  sim_insts)

        # Miss penalties (cycles) from ticks
        def miss_penalty_cycles(entry):
            if entry['miss_latency_ticks'] is None or not clk or clk <= 0:
                return None
            return entry['miss_latency_ticks'] / clk

        l1d_mpen = miss_penalty_cycles(l1d)
        l1i_mpen = miss_penalty_cycles(l1i)
        l2_mpen  = miss_penalty_cycles(l2)

        # AMAT (cycles). If hit-time unknown, use 1 cycle default (documented assumption).
        l1d_amat = amat(l1d['hit_rate'], l1d_mpen, hit_time_cycles=1.0)
        l1i_amat = amat(l1i['hit_rate'], l1i_mpen, hit_time_cycles=1.0)
        # For L2, AMAT is usually used as miss penalty for L1; still we compute local AMAT under same assumption
        l2_amat  = amat(l2['hit_rate'],  l2_mpen,  hit_time_cycles=10.0)  # use 10-cycle hit as conservative placeholder if needed

        # Branch prediction
        br_mis, br_com, br_rate = branch_mispred(stats)

        # Mem dep conflicts
        ld_ins, ld_conf, ld_rate, st_ins, st_conf, st_rate = memdep_conflicts(stats)

        # Pipeline flushes
        flush_events, squashed_insts = pipeline_flush(stats)

        # Effective stall cycles upper bound: sum of overallMissLatency ticks / clk
        stall_ticks = 0.0
        for tag in [('l1dcaches',), ('l1icaches',), ('l2cache',)]:
            ticks = find_first(stats, [list(tag) + ['overallmisslatency']])
            if ticks:
                stall_ticks += ticks
        eff_stall_cycles_upper = (stall_ticks / clk) if clk and clk > 0 else None

        # Energy proxies
        # L1 accesses
        l1_accesses = 0.0
        for tag in [('l1dcaches',), ('l1icaches',)]:
            acc = find_first(stats, [list(tag) + ['overallaccesses']])
            if acc:
                l1_accesses += acc
        l2_accesses = l2['accesses'] or 0.0
        dram_r, dram_w, dram_rb, dram_wb = dram_stats(stats)

        wL1, wL2, wDRAM = args.weights
        energy_proxy = None
        try:
            energy_proxy = wL1 * l1_accesses + wL2 * l2_accesses + wDRAM * (dram_r + dram_w)
        except Exception:
            energy_proxy = None

        rec = {
            'run': run_name,
            'ipc': ipc,
            'cycles': cycles,
            'sim_insts': sim_insts,

            'l1d_accesses': l1d['accesses'],
            'l1d_hits': l1d['hits'],
            'l1d_misses': l1d['misses'],
            'l1d_hit_rate': l1d['hit_rate'],
            'l1d_mpki': l1d_mpki,
            'l1d_miss_penalty_cycles': l1d_mpen,
            'l1d_amat_cycles': l1d_amat,

            'l1i_accesses': l1i['accesses'],
            'l1i_hits': l1i['hits'],
            'l1i_misses': l1i['misses'],
            'l1i_hit_rate': l1i['hit_rate'],
            'l1i_mpki': l1i_mpki,
            'l1i_miss_penalty_cycles': l1i_mpen,
            'l1i_amat_cycles': l1i_amat,

            'l2_accesses': l2['accesses'],
            'l2_hits': l2['hits'],
            'l2_misses': l2['misses'],
            'l2_hit_rate': l2['hit_rate'],
            'l2_mpki': l2_mpki,
            'l2_miss_penalty_cycles': l2_mpen,
            'l2_amat_cycles': l2_amat,

            'branch_mispreds': br_mis,
            'branch_committed': br_com,
            'branch_mispred_rate': br_rate,

            'memdep_loads_inserted': ld_ins,
            'memdep_loads_conflicting': ld_conf,
            'memdep_load_conflict_rate': ld_rate,
            'memdep_stores_inserted': st_ins,
            'memdep_stores_conflicting': st_conf,
            'memdep_store_conflict_rate': st_rate,

            'flush_events': flush_events,
            'squashed_insts': squashed_insts,

            'eff_stall_cycles_upper': eff_stall_cycles_upper,

            'l1_accesses_total': l1_accesses,
            'l2_accesses_total': l2_accesses,
            'dram_reads': dram_r,
            'dram_writes': dram_w,
            'dram_bytes_read': dram_rb,
            'dram_bytes_written': dram_wb,
            'energy_proxy': energy_proxy,
            'weights_wL1_wL2_wDRAM': f'{wL1},{wL2},{wDRAM}',
            'stats_path': spath,
        }
        records.append(rec)

    # Write CSV
    out_path = args.output
    # Ensure deterministic column order
    fieldnames = [
        'run','stats_path',
        'ipc','cycles','sim_insts',
        'l1d_accesses','l1d_hits','l1d_misses','l1d_hit_rate','l1d_mpki','l1d_miss_penalty_cycles','l1d_amat_cycles',
        'l1i_accesses','l1i_hits','l1i_misses','l1i_hit_rate','l1i_mpki','l1i_miss_penalty_cycles','l1i_amat_cycles',
        'l2_accesses','l2_hits','l2_misses','l2_hit_rate','l2_mpki','l2_miss_penalty_cycles','l2_amat_cycles',
        'branch_mispreds','branch_committed','branch_mispred_rate',
        'memdep_loads_inserted','memdep_loads_conflicting','memdep_load_conflict_rate',
        'memdep_stores_inserted','memdep_stores_conflicting','memdep_store_conflict_rate',
        'flush_events','squashed_insts',
        'eff_stall_cycles_upper',
        'l1_accesses_total','l2_accesses_total','dram_reads','dram_writes','dram_bytes_read','dram_bytes_written',
        'energy_proxy','weights_wL1_wL2_wDRAM',
    ]
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"Wrote {len(records)} rows to {out_path}")
    print("Tip: open in pandas for quick sorting/plotting.")
    print("Weights used (wL1, wL2, wDRAM):", args.weights)

if __name__ == '__main__':
    main()
