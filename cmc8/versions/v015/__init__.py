"""Complete v015 instruction repertoire, including SCS/SCW and explicit SCWR waits."""
from .model import MODEL_VERSION, ModelError, Simulator, State, evaluate
from .mops import MOPS, UNRESOLVED

__all__ = ["MODEL_VERSION", "ModelError", "Simulator", "State", "evaluate", "MOPS", "UNRESOLVED"]

from .instructions import (ControlPort, ControlStrobe, InstructionLimit,
                           InstructionSimulator, Memory, MemoryWrite, SlotTrace)

__all__ += ["InstructionSimulator", "Memory", "MemoryWrite", "SlotTrace"]
__all__ += ["ControlPort", "ControlStrobe", "InstructionLimit"]

from .sequences import FLAG_INSTRUCTIONS, FlagInstruction

__all__ += ["FLAG_INSTRUCTIONS", "FlagInstruction"]
