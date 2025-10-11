from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes
from m5.objects import (
    # Branch Predictors
    BiModeBP,
    LocalBP,
    TournamentBP,
    TAGE,
    MultiperspectivePerceptron64KB,
    # Cache Replacement Policies
    LRURP,
    RandomRP,
    DuelingRP,
    TreePLRURP,
    # Cache Prefetchers
    StridePrefetcher,
    TaggedPrefetcher,
    AMPMPrefetcher,
    SignaturePathPrefetcher,
    BOPPrefetcher,
)


CORE_ISA = ISA.X86
NUM_CORES = 1
CLK_FREQ = "3.2GHz"
CPU_TYPE = CPUTypes.O3

BRANCH_PREDICTORS = {
    "bimodal": BiModeBP,
    "local": LocalBP,
    "tournament": TournamentBP,
    "tage": TAGE,
    "perceptron": MultiperspectivePerceptron64KB,
    "none": None,
}

CACHE_REPLACEMENT_POLICIES = {
    "lru": LRURP,
    "random": RandomRP,
    "dueling": DuelingRP,
    "plru": TreePLRURP,
    "none": None,
}

CACHE_PREFETCHERS = {
    "stride": StridePrefetcher,
    "tagged": TaggedPrefetcher,
    "ampm": AMPMPrefetcher,
    "signature": SignaturePathPrefetcher,
    "bop": BOPPrefetcher,
    "none": None,
}
