import m5.stats as stats
from m5.objects import PowerModel, MathExprPowerModel, SubSystem

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from caches import CustomPrivateL1SharedL2CacheHierarchy
from configParser import (
    parseArguments,
    setupConfig,
)


args = parseArguments()
coreConfig, cacheConfig, workloadConfig = setupConfig(args)


def roiStart():
    print("ROI started")
    stats.reset()
    yield False


def roiEnd():
    print("ROI ended")
    stats.dump()
    yield True


cacheHierarchy = CustomPrivateL1SharedL2CacheHierarchy(
    l1_size=cacheConfig["l1Size"],
    l1_assoc=cacheConfig["l1Associativity"],
    l1_replacement_policy=cacheConfig["l1rp"],
    l1_prefetcher=cacheConfig["l1p"],
    l2_size=cacheConfig["l2Size"],
    l2_assoc=cacheConfig["l2Associativity"],
    l2_replacement_policy=cacheConfig["l2rp"],
    l2_prefetcher=cacheConfig["l2p"],
)

memory = SingleChannelDDR3_1600(size="4GiB")

processor = SimpleProcessor(
    cpu_type=coreConfig["cpuType"],
    num_cores=coreConfig["nCores"],
    isa=coreConfig["isa"],
)
for cpu in processor.get_cores():
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
