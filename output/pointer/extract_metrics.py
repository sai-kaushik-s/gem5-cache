#!/usr/bin/env python3
# (body trimmed in message above for brevity; full code included here)
import argparse, os, re
import pandas as pd

NUM_RE = re.compile(r'^-?\d+(\.\d+)?(e[+-]?\d+)?$', re.IGNORECASE)

def parse_stats(path):
    d = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            key = parts[0]
            val = parts[1].strip('=,:')
            if not NUM_RE.match(val):
                if len(parts) >= 3 and NUM_RE.match(parts[2]):
                    val = parts[2]
                else:
                    continue
            try:
                d[key] = float(val)
            except:
                continue
    return d

def first_key(d, keys):
    for k in keys:
        if k in d:
            return d[k]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.', help='Root directory to scan')
    ap.add_argument('--output', default='metrics_raw.xlsx', help='Output Excel filename')
    args = ap.parse_args()

    rows = []

    L2_HITS_KEYS = [
        'board.cache_hierarchy.l2caches.overallHits::total',
        'board.cache_hierarchy.l2cache.overallHits::total',
    ]
    L2_ACCS_KEYS = [
        'board.cache_hierarchy.l2caches.overallAccesses::total',
        'board.cache_hierarchy.l2caches.overallAccess::total',
        'board.cache_hierarchy.l2cache.overallAccesses::total',
        'board.cache_hierarchy.l2cache.overallAccess::total',
    ]
    L2_MISS_KEYS = [
        'board.cache_hierarchy.l2caches.overallMisses::total',
        'board.cache_hierarchy.l2cache.overallMisses::total',
    ]

    L1D_MLAT_KEYS = [
        'board.cache_hierarchy.l1dcaches.overallMissLatency::total',
        'board.cache_hierarchy.l1dcaches.overallAvgMissLatency::total',
    ]
    L1I_MLAT_KEYS = [
        'board.cache_hierarchy.l1icaches.overallMissLatency::total',
        'board.cache_hierarchy.l1icaches.overallAvgMissLatency::total',
    ]
    L2_MLAT_KEYS = [
        'board.cache_hierarchy.l2caches.overallMissLatency::total',
        'board.cache_hierarchy.l2caches.overallAvgMissLatency::total',
        'board.cache_hierarchy.l2cache.overallMissLatency::total',
        'board.cache_hierarchy.l2cache.overallAvgMissLatency::total',
    ]

    stats_files = []
    for dp, dn, fn in os.walk(args.root):
        if 'stats.txt' in fn:
            stats_files.append(os.path.join(dp, 'stats.txt'))

    for spath in sorted(stats_files):
        stats = parse_stats(spath)
        run = os.path.basename(os.path.dirname(spath))

        row = {
            'run': run,
            'stats_path': spath,
            'board.processor.cores.core.ipc': stats.get('board.processor.cores.core.ipc'),
            'board.cache_hierarchy.l1dcaches.overallHits::total':  stats.get('board.cache_hierarchy.l1dcaches.overallHits::total'),
            'board.cache_hierarchy.l1dcaches.overallAccesses::total': stats.get('board.cache_hierarchy.l1dcaches.overallAccesses::total'),
            'board.cache_hierarchy.l1dcaches.overallMisses::total': stats.get('board.cache_hierarchy.l1dcaches.overallMisses::total'),
            'board.cache_hierarchy.l1icaches.overallHits::total':  stats.get('board.cache_hierarchy.l1icaches.overallHits::total'),
            'board.cache_hierarchy.l1icaches.overallAccesses::total': stats.get('board.cache_hierarchy.l1icaches.overallAccesses::total'),
            'board.cache_hierarchy.l1icaches.overallMisses::total': stats.get('board.cache_hierarchy.l1icaches.overallMisses::total'),
            'board.cache_hierarchy.l2caches.overallHits::total':     first_key(stats, L2_HITS_KEYS),
            'board.cache_hierarchy.l2caches.overallAccesses::total': first_key(stats, L2_ACCS_KEYS),
            'board.cache_hierarchy.l2caches.overallMisses::total':   first_key(stats, L2_MISS_KEYS),
            'simInsts': stats.get('simInsts', stats.get('sim_insts')),
            'branchPred.committed_0::total':    stats.get('board.processor.cores.core.branchPred.committed_0::total'),
            'branchPred.mispredicted_0::total': stats.get('board.processor.cores.core.branchPred.mispredicted_0::total'),
            'insertedLoads':                    stats.get('board.processor.cores.core.MemDepUnit__0.insertedLoads'),
            'insertedStores':                   stats.get('board.processor.cores.core.MemDepUnit__0.insertedStores'),
            'conflictingLoads':                 stats.get('board.processor.cores.core.MemDepUnit__0.conflictingLoads'),
            'conflictingStores':                stats.get('board.processor.cores.core.MemDepUnit__0.conflictingStores'),
            'commit.branchMispredicts':         stats.get('board.processor.cores.core.commit.branchMispredicts'),
            'commit.commitSquashedInsts':       stats.get('board.processor.cores.core.commit.commitSquashedInsts'),
            'l1d.overallMissLatency::total': first_key(stats, L1D_MLAT_KEYS),
            'l1i.overallMissLatency::total': first_key(stats, L1I_MLAT_KEYS),
            'l2.overallMissLatency::total':  first_key(stats, L2_MLAT_KEYS),
            'L1D_overallAccesses': stats.get('board.cache_hierarchy.l1dcaches.overallAccesses::total'),
            'L1I_overallAccesses': stats.get('board.cache_hierarchy.l1icaches.overallAccesses::total'),
            'L2_overallAccesses':  first_key(stats, L2_ACCS_KEYS),
            'memory.module.numReads::total': stats.get('board.memory.module.numReads::total'),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    cols = [
        'run','stats_path',
        'board.processor.cores.core.ipc',
        'board.cache_hierarchy.l1dcaches.overallHits::total',
        'board.cache_hierarchy.l1dcaches.overallAccesses::total',
        'board.cache_hierarchy.l1dcaches.overallMisses::total',
        'board.cache_hierarchy.l1icaches.overallHits::total',
        'board.cache_hierarchy.l1icaches.overallAccesses::total',
        'board.cache_hierarchy.l1icaches.overallMisses::total',
        'board.cache_hierarchy.l2caches.overallHits::total',
        'board.cache_hierarchy.l2caches.overallAccesses::total',
        'board.cache_hierarchy.l2caches.overallMisses::total',
        'simInsts',
        'branchPred.committed_0::total',
        'branchPred.mispredicted_0::total',
        'insertedLoads','insertedStores','conflictingLoads','conflictingStores',
        'commit.branchMispredicts','commit.commitSquashedInsts',
        'l1d.overallMissLatency::total','l1i.overallMissLatency::total','l2.overallMissLatency::total',
        'L1D_overallAccesses','L1I_overallAccesses','L2_overallAccesses','memory.module.numReads::total',
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols]
    out = args.output
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='raw_metrics')
    print(f"Wrote {len(df)} rows to {out}")

if __name__ == "__main__":
    main()
