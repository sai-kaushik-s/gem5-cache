import os

import m5.stats as stats

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.components.memory.simple import SingleChannelSimpleMemory
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from configParser import (
    parseArguments,
    setupConfig,
)


args = parseArguments()
coreConfig, cacheConfig, workloadConfig = setupConfig(args)


def roiStart():
    print("ROI started")
    for cpu in board.processor.get_cores():
        cpu.core.numROBEntries = coreConfig["robSize"]
        cpu.core.numIQEntries = coreConfig["iqSize"]
        cpu.core.fetchWidth = coreConfig["pipelineWidth"]
        cpu.core.decodeWidth = coreConfig["pipelineWidth"]
        cpu.core.renameWidth = coreConfig["pipelineWidth"]
        cpu.core.issueWidth = coreConfig["pipelineWidth"]
        cpu.core.wbWidth = coreConfig["pipelineWidth"]
        cpu.core.commitWidth = coreConfig["pipelineWidth"]
        if coreConfig["predictor"]:
            cpu.core.branchPred = coreConfig["predictor"]()

    if cacheConfig["l2ReplacementPolicy"]:
        board.cache_hierarchy.l2cache.replacement_policy = cacheConfig[
            "l2ReplacementPolicy"
        ]()
    if cacheConfig["l2Prefetcher"]:
        board.cache_hierarchy.l2cache.prefetcher = cacheConfig["l2Prefetcher"]()
    for l1d in board.cache_hierarchy.l1dcaches:
        if cacheConfig["l1ReplacementPolicy"]:
            l1d.replacement_policy = cacheConfig["l1ReplacementPolicy"]()
        if cacheConfig["l1Prefetcher"]:
            l1d.prefetcher = cacheConfig["l1Prefetcher"]()
    for l1i in board.cache_hierarchy.l1icaches:
        if cacheConfig["l1ReplacementPolicy"]:
            l1i.replacement_policy = cacheConfig["l1ReplacementPolicy"]()
        if cacheConfig["l1Prefetcher"]:
            l1i.prefetcher = cacheConfig["l1Prefetcher"]()
    stats.reset()
    yield False


def roiEnd():
    print("ROI ended")
    stats.dump()
    yield True


cacheHierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size=cacheConfig["l1Size"],
    l1i_size=cacheConfig["l1Size"],
    l2_size=cacheConfig["l2Size"],
    l1d_assoc=cacheConfig["l1Associativity"],
    l1i_assoc=cacheConfig["l1Associativity"],
    l2_assoc=cacheConfig["l2Associativity"],
)

memory = SingleChannelSimpleMemory(
    latency="40ns", latency_var="0ns", bandwidth="25.6GB/s", size="3GiB"
)

processor = SimpleProcessor(
    cpu_type=coreConfig["cpuType"],
    num_cores=coreConfig["nCores"],
    isa=coreConfig["isa"],
)

board = SimpleBoard(
    clk_freq=coreConfig["clkFreq"],
    processor=processor,
    memory=memory,
    cache_hierarchy=cacheHierarchy,
)

board.set_se_binary_workload(
    binary=BinaryResource(workloadConfig["binary"]),
    arguments=workloadConfig["binaryArgs"],
)

simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKBEGIN: roiStart(),
        ExitEvent.WORKEND: roiEnd(),
    },
)
simulator.run()
