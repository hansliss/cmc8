"""Complete v016 instruction repertoire with opt-in interrupt integration."""
from .model import MODEL_VERSION, ModelError, Simulator, State, evaluate, pending_interrupt
from .mops import MOPS, UNRESOLVED

__all__ = ["MODEL_VERSION", "ModelError", "Simulator", "State", "evaluate", "MOPS", "UNRESOLVED"]

from .instructions import (ControlPort, ControlStrobe, InstructionLimit,
                           InstructionSimulator, InterruptInput, Memory, MemoryWrite, SlotTrace)

__all__ += ["InstructionSimulator", "Memory", "MemoryWrite", "SlotTrace"]
__all__ += ["ControlPort", "ControlStrobe", "InstructionLimit"]
__all__ += ["InterruptInput", "pending_interrupt"]

from .sequences import FLAG_INSTRUCTIONS, FlagInstruction

__all__ += ["FLAG_INSTRUCTIONS", "FlagInstruction"]
