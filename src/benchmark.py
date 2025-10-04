import m5.stats as stats
from m5.objects import PowerModel, PowerModelState, MathExprPowerModel
from m5.proxy import Parent

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from configParser import (
    parseArguments,
    setupConfig,
)


class MemoryPowerOn(MathExprPowerModel):
    def __init__(self, mem_ctrl_path, **kwargs):
        super().__init__(**kwargs)
        self.dyn = f"(({mem_ctrl_path}.bytesRead::total + {mem_ctrl_path}.bytesWritten::total) / simSeconds * 0.00000007)"
        self.st = "temp * 0.8"


class MemoryPowerOff(MathExprPowerModel):
    dyn = "0"
    st = "0"


class MemoryPowerModel(PowerModel):
    def __init__(self, mem_ctrl_path, **kwargs):
        super().__init__(**kwargs)
        self.pm = [
            MemoryPowerOn(mem_ctrl_path),
            MemoryPowerOff(),
            MemoryPowerOff(),
            MemoryPowerOff(),
        ]


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

    if cacheConfig["l2rp"]:
        board.cache_hierarchy.l2cache.replacement_policy = cacheConfig["l2rp"]()
    if cacheConfig["l2p"]:
        board.cache_hierarchy.l2cache.prefetcher = cacheConfig["l2p"]()

    for l1d in board.cache_hierarchy.l1dcaches:
        if cacheConfig["l1rp"]:
            l1d.replacement_policy = cacheConfig["l1rp"]()
        if cacheConfig["l1p"]:
            l1d.prefetcher = cacheConfig["l1p"]()
    for l1i in board.cache_hierarchy.l1icaches:
        if cacheConfig["l1rp"]:
            l1i.replacement_policy = cacheConfig["l1rp"]()
        if cacheConfig["l1p"]:
            l1i.prefetcher = cacheConfig["l1p"]()
    mem_ctrl = board.get_memory().mem_ctrl[0]
    mem_ctrl.power_state.default_state = "ON"
    mem_ctrl.power_model = MemoryPowerModel(mem_ctrl.path())
    board.power_model = PowerModel(subsystem=Parent.itself)
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

memory = SingleChannelDDR3_1600(size="3GiB")

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
