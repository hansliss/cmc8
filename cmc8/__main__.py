"""Readable versioned demonstrations: python3 -m cmc8 --model v018."""
import argparse
import json


def baseline_demo():
    from .versions.v001 import Simulator, State

    state = State(n=0)
    state.registers[0] = 0x29
    simulator = Simulator(state)
    # An illustrative experiment, not a transcribed instruction.
    simulator.capture([18, 21, 7, 10, 12], label="Increment R(N) through ALU into BR")
    simulator.capture([4, 18, 22], label="Write BR through DI back to R(N)")
    return simulator.trace


def instruction_demo():
    from .versions.v002 import InstructionSimulator, Memory, State

    state = State(n=0, pg=0)
    state.registers[0] = 0x20
    memory = Memory(
        program={0x20: 0x53, 0x21: 0x80, 0x22: 0x73, 0x23: 0x81},
        storage={0x80: 0xA6},
    )
    simulator = InstructionSimulator(state, memory)
    simulator.run_instruction()  # LRS R3, [0x80]
    simulator.run_instruction()  # SRS R3, [0x81]
    return simulator


def paged_instruction_demo():
    from .versions.v003 import InstructionSimulator, Memory, State

    state = State(n=0, pg=2)
    state.registers[0] = 0x20
    memory = Memory(
        program={
            0x220: 0x43, 0x221: 0x80,  # LRM R3,[280]
            0x222: 0x63, 0x223: 0x81,  # SRM R3,[281]
            0x224: 0x73, 0x225: 0x82,  # SRS R3,[282]
            0x226: 0x54, 0x227: 0x82,  # LRS R4,[282]
            0x280: 0xA6,
        },
        storage={0x082: 0x11},  # Different page: must remain untouched.
    )
    simulator = InstructionSimulator(state, memory)
    for _ in range(4):
        simulator.run_instruction()
    return simulator


def device_instruction_demo():
    from .versions.v004 import InstructionSimulator, Memory, State

    state = State(n=0, pg=3)
    state.registers[0] = 0x20
    memory = Memory(
        program={
            0x320: 0x13, 0x321: 0x05,  # LRD R3,[05]
            0x322: 0x1B, 0x323: 0x04,  # SRD R3,[04]
            0x324: 0x14, 0x325: 0x04,  # LRD R4,[04]
        },
        storage={0x304: 0x11},
        devices={0x05: 0xA6, 0x04: 0},
    )
    simulator = InstructionSimulator(state, memory)
    for _ in range(3):
        simulator.run_instruction()
    return simulator


def nop_demo():
    from .versions.v005 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1)
    state.registers[0] = 0xFF
    state.registers[3] = 0xA6
    simulator = InstructionSimulator(state, Memory(program={0x1FF: 0x00}))
    simulator.run_instruction()
    return simulator


def flag_demo():
    from .versions.v006 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0] = 0x20
    # The final NOP provides the fetch in which REZ takes effect.
    program = dict(enumerate([3, 2, 5, 4, 7, 6, 0], start=0x120))
    simulator = InstructionSimulator(state, Memory(program=program))
    for _ in range(7):
        simulator.run_instruction()
    return simulator


def show_flags(simulator):
    print("v006: EIN; DIN; SEL; REL; SEZ; REZ; NOP. All six flag implementations remain provisional.")
    print("Flag effects occur at the next fetch's T2; EIN has documented timing and higher confidence.")
    print("Slot  IR PC | INTE L Z | flag MOP and originating opcode")
    for row in simulator.trace:
        state = row.end.after
        effect = row.flag_effect
        description = "-"
        if effect is not None:
            description = (f"MOP{effect.mop}: {effect.flag}={effect.value} from "
                           f"{effect.name} ({byte(row.control_ir)}), confidence={effect.confidence}")
        print(f"F{row.phase}T{row.timing}  {byte(state.ir)} {byte(state.registers[state.n])} | "
              f"{state.inte}    {state.link} {state.z} | {description}")
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(simulator.state.registers[0])}, "
          f"INTE={simulator.state.inte}, L={simulator.state.link}, Z={simulator.state.z}")


def indexed_demo():
    from .versions.v007 import InstructionSimulator, Memory, State

    state = State(n=0, pg=2)
    state.registers[0], state.registers[7] = 0x20, 0x80
    memory = Memory(program={
        0x220: 0x4B,  # LRX R3
        0x221: 0x6B,  # SRX R3
        0x222: 0x7B,  # SSX R3
        0x223: 0x5C,  # LSX R4
        0x280: 0xA6,
    })
    simulator = InstructionSimulator(state, memory)
    for _ in range(4):
        simulator.run_instruction()
    return simulator


def control_flow_demo():
    from .versions.v008 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0], state.registers[3] = 0x20, 0x90
    memory = Memory(program={
        0x120: 0xF2, 0x121: 0x40,  # JMP to page 2, address 40
        0x240: 0x0C, 0x241: 0x80,  # JSR to address 80 on current page
        0x280: 0xFB,                # JCR R3 -> address 90
        0x290: 0x0F,                # RSR -> caller address 42
        0x242: 0x00,                # NOP after the call
    })
    simulator = InstructionSimulator(state, memory)
    for _ in range(5):
        simulator.run_instruction()
    return simulator


def show_control_flow(simulator):
    print("v008: JMP page 2; JSR; JCR R3; RSR; NOP. JCR's detailed schedule remains likely.")
    print("Slot  Instruction N PG PC AB BR | MOPs")
    for row in simulator.trace:
        state = row.end.after
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} {state.n} "
              f"{byte(state.pg)} {byte(state.registers[state.n])} {byte(state.ab)} {byte(state.br)} | "
              + ','.join(map(str,row.mops)))
    print(f"Result: {len(simulator.trace)} subdivisions, N={simulator.state.n}, "
          f"PG={byte(simulator.state.pg)}, PC={byte(simulator.state.registers[simulator.state.n])}")


def branch_demo():
    from .versions.v009 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0], state.registers[3] = 0x20, 0xA6
    memory = Memory(program={
        0x120: 0x05,                # SEL: takes effect during BL1 fetch.
        0x121: 0xEE, 0x122: 0x40,  # BL1 page 2 -> taken, address 40.
        0x240: 0x07,                # SEZ: takes effect during BZ0 fetch.
        0x241: 0xE3, 0x242: 0x70,  # BZ0 page 3 -> untaken, stays on page 2.
        0x243: 0xD3, 0x244: 0x60,  # BB0 R3 -> taken (A6 has bit 0 clear).
        0x260: 0xCA, 0x261: 0x80,  # BT1 T2 -> taken, retains page 2.
        0x280: 0x00,                # NOP.
    })
    simulator = InstructionSimulator(state, memory, test_inputs=(0, 0, 1, 0))
    for _ in range(7):
        simulator.run_instruction()
    return simulator


def show_branches(simulator):
    print("v009: SEL; BL1; SEZ; BZ0; BB0 R3; BT1 T2; NOP.")
    print("H is physical Q; H=0 enables the conditional write. Two-cycle schedules remain likely.")
    print("Slot  Instruction PG PC BR | L Z H T | branch write / flag effect")
    for row in simulator.trace:
        state = row.end.after
        effect = ""
        if row.flag_effect is not None:
            effect = f"{row.flag_effect.name}: {row.flag_effect.flag}={row.flag_effect.value}"
        if row.branch_taken is not None:
            effect = "taken" if row.branch_taken else "untaken"
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} {byte(state.pg)} "
              f"{byte(state.registers[state.n])} {byte(state.br)} | "
              f"{state.link} {state.z} {state.h} {state.t} | {effect}")
    print(f"Result: {len(simulator.trace)} subdivisions, N={simulator.state.n}, "
          f"PG={byte(simulator.state.pg)}, PC={byte(simulator.state.registers[simulator.state.n])}")


def byte(value):
    return "??" if value is None else f"{value:02X}"


def immediate_copy_demo():
    from .versions.v010 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 0x23, 0x121: 0x80,  # LRI R3, #80.
        0x122: 0x3B,                # CPY R3 -> X=80.
        0x123: 0x5C,                # LSX R4 reads storage[180].
        0x124: 0x25, 0x125: 0xA6,  # LRI R5, #A6.
        0x126: 0x7D,                # SSX R5 writes storage[180].
        0x127: 0x00,                # NOP.
    }, storage={0x180: 0x69})
    simulator = InstructionSimulator(state, memory)
    for _ in range(6):
        simulator.run_instruction()
    return simulator


def show_immediate_copy(simulator):
    print("v010: LRI R3,#80; CPY R3; LSX R4; LRI R5,#A6; SSX R5; NOP.")
    print("LRI/CPY detailed schedules are likely consistency-supported extrapolations.")
    print("Slot  Instruction PC R3 R4 R5 X  BR | MOPs")
    for row in simulator.trace:
        state = row.end.after
        registers = state.registers
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} "
              f"{byte(registers[state.n])} {byte(registers[3])} {byte(registers[4])} "
              f"{byte(registers[5])} {byte(registers[7])} {byte(state.br)} | "
              + ','.join(map(str, row.mops)))
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(state.registers[state.n])}, "
          f"R4={byte(state.registers[4])}, X={byte(state.registers[7])}, "
          f"storage[180]={byte(simulator.memory.storage[0x180])}")


def arithmetic_demo():
    from .versions.v011 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 0x23, 0x121: 0xF0,  # LRI R3,#F0.
        0x122: 0x27, 0x123: 0x0F,  # LRI X,#0F.
        0x124: 0xB3,                # AND R3 -> X=00, Z=1.
        0x125: 0xE9, 0x126: 0x40,  # BZ1 page 1 -> taken.
        0x140: 0x24, 0x141: 0xFF,  # LRI R4,#FF.
        0x142: 0x84,                # INR R4 -> 00, Z=1.
        0x143: 0xA4,                # DCR R4 -> FF, Z=0.
        0x144: 0xE1, 0x145: 0x60,  # BZ0 page 1 -> taken.
        0x160: 0x00,                # NOP.
    })
    simulator = InstructionSimulator(state, memory)
    for _ in range(9):
        simulator.run_instruction()
    return simulator


def show_arithmetic(simulator):
    if simulator.trace[0].version == "v012":
        print("v012: LRI R3,#FF; XRI R3,#FF; BZ1; LRI R4,#F7; ANI R4,#08; LRI X,#AA; LRI R5,#AA; XOR R5; NOP.")
        print("Logical operations use the ALU zero detector; their detailed schedules remain inferred.")
    else:
        print("v011: LRI R3,#F0; LRI X,#0F; AND R3; BZ1; LRI R4,#FF; INR R4; DCR R4; BZ0; NOP.")
        print("DCR's DI zero test at T6 represents omitted circuitry and remains provisional.")
    print("Slot  Instruction PC R3 R4 X  BR Z | flag sample / branch")
    for row in simulator.trace:
        state = row.end.after
        signals = row.start.signals
        effect = ""
        if signals.zero_source is not None:
            effect = f"Z from {signals.zero_source}={byte(signals.zero_value)}"
        if row.branch_taken is not None:
            effect = "taken" if row.branch_taken else "untaken"
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} "
              f"{byte(state.registers[state.n])} {byte(state.registers[3])} "
              f"{byte(state.registers[4])} {byte(state.registers[7])} "
              f"{byte(state.br)} {state.z} | {effect}")
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(state.registers[state.n])}, "
          f"X={byte(state.registers[7])}, R4={byte(state.registers[4])}, Z={state.z}")


def logical_demo():
    from .versions.v012 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 0x23, 0x121: 0xFF,  # LRI R3,#FF.
        0x122: 0x2B, 0x123: 0xFF,  # XRI R3,#FF -> 0, Z=1.
        0x124: 0xE9, 0x125: 0x40,  # BZ1 page1 -> taken.
        0x140: 0x24, 0x141: 0xF7,  # LRI R4,#F7.
        0x142: 0x34, 0x143: 8,     # ANI R4,#08 -> 0, Z=1.
        0x144: 0x27, 0x145: 0xAA,  # LRI X,#AA.
        0x146: 0x25, 0x147: 0xAA,  # LRI R5,#AA.
        0x148: 0xAD,                # XOR R5 -> X=0, Z=1.
        0x149: 0,
    })
    simulator = InstructionSimulator(state, memory)
    for _ in range(9):
        simulator.run_instruction()
    return simulator


def shift_demo():
    from .versions.v013 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, inte=0, link=0, z=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 0x23, 0x121: 0x81,  # LRI R3,#81.
        0x122: 0x8B,                # ROR R3 -> C0, Link unchanged.
        0x123: 0x93,                # SHR R3 -> 60, Link unchanged.
        0x124: 5,                   # SEL; takes effect in next fetch.
        0x125: 0x9B,                # RRL R3 -> B0, Link=0.
        0x126: 0x24, 0x127: 1,     # LRI R4,#01.
        0x128: 0x9C,                # RRL R4 -> 00, Link=1, Z unchanged.
        0x129: 0xED, 0x12A: 0x40,  # BL1 page1 -> taken.
        0x140: 0,
    })
    simulator = InstructionSimulator(state, memory)
    for _ in range(9):
        simulator.run_instruction()
    return simulator


def show_shifts(simulator):
    print("v013: LRI R3,#81; ROR R3; SHR R3; SEL; RRL R3; LRI R4,#01; RRL R4; BL1; NOP.")
    print("RRL samples old Link and ALU bit0 together at F2T2; ROR/SHR timing is inferred.")
    print("Slot  Instruction PC R3 R4 BR L Z | shift / Link / branch")
    for row in simulator.trace:
        state = row.end.after
        signals = row.start.signals
        effect = ""
        if 11 in row.mops:
            effect = f"bit7={signals.shift_in}, shifted-out={signals.alu & 1}"
            if 33 in row.mops:
                effect += f", new L={signals.link_input}"
        if row.flag_effect is not None:
            effect = f"{row.flag_effect.name}: L={state.link}"
        if row.branch_taken is not None:
            effect = "taken" if row.branch_taken else "untaken"
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} "
              f"{byte(state.registers[state.n])} {byte(state.registers[3])} "
              f"{byte(state.registers[4])} {byte(state.br)} {state.link} {state.z} | {effect}")
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(state.registers[state.n])}, "
          f"R3={byte(state.registers[3])}, R4={byte(state.registers[4])}, L={state.link}, Z={state.z}")


def exchange_demo():
    from .versions.v014 import InstructionSimulator, Memory, State

    state = State(n=0, pg=1, link=0, z=0, inte=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 0x23, 0x121: 0x80,  # LRI R3,#80.
        0x122: 0x27, 0x123: 0xA6,  # LRI X,#A6.
        0x124: 0xBB,                # EXR R3 -> X=80, R3=A6.
        0x125: 0x5C,                # LSX R4 -> storage[180].
        0x126: 0xBB,                # EXR R3 -> restore X=A6, R3=80.
        0x127: 0,
    }, storage={0x180: 0x69})
    simulator = InstructionSimulator(state, memory)
    for _ in range(6):
        simulator.run_instruction()
    return simulator


def show_exchange(simulator):
    print("v014: LRI R3,#80; LRI X,#A6; EXR R3; LSX R4; EXR R3; NOP.")
    print("H019 is provisional: EXR requires an undocumented ALU input holding latch in this model.")
    print("Slot  Instruction PC R3 R4 X  BR held-A | research control")
    for row in simulator.trace:
        state = row.end.after
        mode = row.start.signals.alu_a_mode
        note = '' if mode == 'di' else f'alu_a_mode={mode}'
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} "
              f"{byte(state.registers[state.n])} {byte(state.registers[3])} "
              f"{byte(state.registers[4])} {byte(state.registers[7])} "
              f"{byte(state.br)} {byte(state.alu_a)} | {note}")
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(state.registers[state.n])}, "
          f"R3={byte(state.registers[3])}, R4={byte(state.registers[4])}, X={byte(state.registers[7])}")


def control_signal_demo():
    from .versions.v015 import ControlPort, InstructionSimulator, Memory, State

    state = State(n=0, pg=1, link=0, z=0, inte=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 9, 0x121: 4,     # SCS #04: latch, continue without sampling SCWR.
        0x122: 8, 0x123: 0xA6,  # SCW #A6: two full wait cycles.
        0x124: 0,
    })
    control = ControlPort(ack_after=20)  # External test peripheral response.
    simulator = InstructionSimulator(state, memory, control=control)
    for _ in range(3):
        simulator.run_instruction()
    return simulator


def show_control_signals(simulator):
    print("v015: SCS #04; SCW #A6 with two acknowledgement waits; NOP.")
    print("Program memory supplies DB; the example peripheral latches it under STRCS. SCWR is active low.")
    print("Slot  Instruction PC AB DB STRCS SCWR waiting | external capture")
    for row in simulator.trace:
        state = row.end.after
        event = row.control_strobe
        effect = '' if event is None else f'control={byte(event.value)}'
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} "
              f"{byte(state.registers[state.n])} {byte(state.ab)} "
              f"{byte(row.start.signals.db)} {int(row.strcs):>3} {str(row.scwr):>5} "
              f"{str(row.waiting):>7} | {effect}")
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(simulator.state.registers[0])}, "
          f"control={byte(simulator.control.value)}, strobes={len(simulator.control.strobes)}")


def interrupt_demo():
    from .versions.v016 import InstructionSimulator, InterruptInput, Memory, State

    state = State(n=0, pg=1, link=0, z=0, inte=0, intr=0, inta=0)
    state.registers[0] = 0x20
    memory = Memory(program={
        0x120: 3,                   # Main EIN; still disabled at its completion.
        0x121: 0,                   # NOP completes before held INT is accepted.
        0x122: 0x23, 0x123: 0xA6,  # Main LRI R3,#A6, after handler return.
        0x102: 0x24, 0x103: 0x69,  # Handler vector: LRI R4,#69.
        0x104: 3,                   # Handler EIN.
        0x105: 0x0F,                # RSR finishes before a reenabled request could enter.
    })
    simulator = InstructionSimulator(state, memory, interrupts=InterruptInput(0))
    for _ in range(7):  # Six opcodes plus one interrupt-entry event.
        event = simulator.run_instruction()
        if event[0].interrupt_accepted:
            # Example source releases INT in response to acknowledgement.
            simulator.set_interrupt(1)
    return simulator


def show_interrupts(simulator):
    print("v016: EIN; NOP; interrupt entry; handler LRI/EIN/RSR; main LRI.")
    print("INT is a raw active-low input; INTA below is the logical acknowledge state.")
    print("Slot  Event       N PC | INT INTE INTR INTA | event / deferred effect")
    for row in simulator.trace:
        state = row.end.after
        effect = ''
        if row.interrupt_accepted:
            effect = 'accept request; disable and clear'
        elif row.flag_effect is not None:
            effect = f'{row.flag_effect.name}: {row.flag_effect.flag}={row.flag_effect.value}'
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} {state.n} "
              f"{byte(state.registers[state.n])} | {row.int_level}   {state.inte}    "
              f"{state.intr}    {state.inta} | {effect}")
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, N={state.n}, "
          f"PG={byte(state.pg)}, PC={byte(state.registers[state.n])}, "
          f"R3={byte(state.registers[3])}, R4={byte(state.registers[4])}, INTE={state.inte}")


def reset_demo():
    from .versions.v017 import InstructionSimulator, Memory, ResetInput, State

    state = State(n=3, pg=2, ir=0, inta=1, inte=0, intr=0, link=1, z=1)
    state.registers = [0x90, 0x91, 0x92, 0x20, 0x94, 0x95, 0x96, 0x97]
    simulator = InstructionSimulator(
        state, Memory(program={0x220: 0, 0: 0x23, 1: 0xA6}), reset=ResetInput(0))
    simulator.run_instruction()  # NOP; active RESET sampled at T7.
    simulator.set_reset(1)        # Selected reset cycle survives pin release.
    simulator.run_instruction()  # Reset: PG=0, N=0, R0=0, INTA=0.
    simulator.run_instruction()  # Startup code at 000: LRI R3,#A6.
    return simulator


def show_reset(simulator):
    print("v017: NOP; RESET sampled at T7; reset cycle; LRI R3,#A6 at 000.")
    print("Slot  Event       RESET N PG PC INTA | controls / reset sample")
    for row in simulator.trace:
        state = row.end.after
        effect = 'select next reset cycle' if row.reset_sampled else ''
        controls = ','.join(map(str, row.mops)) or '-'
        if row.start.signals.clear_inta:
            controls += '; clear INTA'
        print(f"F{row.phase}T{row.timing}  {row.instruction:<11} {row.reset_level}     "
              f"{state.n} {byte(state.pg)} {byte(state.registers[state.n])} "
              f"{state.inta} | {controls} {effect}")
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, N={state.n}, PG={byte(state.pg)}, "
          f"PC={byte(state.registers[state.n])}, R3={byte(state.registers[3])}, INTA={state.inta}")


def execution_demo():
    from .versions.v018 import InstructionSimulator, Memory, RunInputs, State

    state = State(n=0, pg=1, ir=0, sse=1, inte=0, intr=0, inta=0)
    state.registers[0] = 0x20
    simulator = InstructionSimulator(
        state, Memory(program={0x120: 0x53, 0x121: 0x80}, storage={0x180: 0x69}),
        run_inputs=RunInputs(memr=1, halt=1, ss=1))
    for _ in range(10):
        simulator.step()  # First fetch waits for memory at T4.
    simulator.set_run_inputs(memr=0, halt=0)
    for _ in range(8):
        simulator.step()  # HALT keeps it waiting after memory is ready.
    simulator.set_run_inputs(ss=0)
    simulator.resume_instruction()  # One SS grant completes LRS with HALT low.
    return simulator


def show_execution(simulator):
    print("v018: memory wait; HALT retains the pause; SS grants one LRS instruction.")
    print("Raw MEMR: high=busy. HALT/SS/WAIT are active low; WAIT is high during T4.")
    print("Slot  Event    MEMR HALT SS WAIT | PC BR SSE | controls / wait reason")
    for row in simulator.trace:
        state = row.end.after
        controls = ','.join(map(str, row.mops)) or '-'
        print(f"F{row.phase}T{row.timing}  {row.instruction:<8} "
              f"{row.memr}    {row.halt_level}    {row.ss_level}   "
              f"{row.end.signals.wait_pin} | {byte(state.registers[state.n])} "
              f"{byte(state.br)} {state.sse} | {controls} {row.wait_reason or ''}")
    state = simulator.state
    print(f"Result: {len(simulator.trace)} subdivisions, PC={byte(state.registers[0])}, "
          f"R3={byte(state.registers[3])}, SSE={state.sse}; HALT remains low.")


def show_instructions(simulator):
    version = simulator.trace[0].version
    print(f"{version}, text interpretation, always-ready memory")
    if version == "v007":
        print("Page 2, X=80: LRX R3; SRX R3; SSX R3; LSX R4. No operand bytes.")
    elif version == "v005":
        print("NOP at program address 1FF: eight subdivisions; PC wraps to 00 on page 1.")
    elif version == "v004":
        print("Program page 3: LRD R3,[05]; SRD R3,[04]; LRD R4,[04]. Ports use AB only.")
    elif version == "v003":
        print("Page 2: LRM R3,[280]; SRM R3,[281]; SRS R3,[282]; LRS R4,[282].")
    else:
        print("LRS R3,[80] followed by SRS R3,[81].")
    print("Values are hexadecimal; v003 onward: memory addresses include the page; I/O uses AB only.")
    print("Slot  PG AB PC BR IR | DI DB at start | asserted controls | capture / memory write")
    for row in simulator.trace:
        state = row.end.after
        signals = row.start.signals
        effects = []
        if 1 in row.mops:
            effects.append(f"IR={byte(state.ir)} (end)")
        if 2 in row.mops:
            effects.append(f"BR={byte(state.br)} (start)")
        if row.memory_write is not None:
            if version in {"v003", "v004", "v005", "v007"}:
                write = row.memory_write
                effects.append(f"{write.space}[{write.address:03X}]={write.value:02X}")
            else:
                address, value = row.memory_write
                effects.append(f"storage[{address:02X}]={value:02X}")
        controls = ",".join(signals.outputs) or "-"
        print(f"F{row.phase}T{row.timing}  {byte(state.pg)} {byte(state.ab)} {byte(state.registers[state.n])} "
              f"{byte(state.br)} {byte(state.ir)} | {byte(signals.di)} {byte(signals.db)}"
              f"            | {controls:<18} | {'; '.join(effects)}")
    if version == "v007":
        print(f"Result: R3={byte(simulator.state.registers[3])}, "
              f"R4={byte(simulator.state.registers[4])}, "
              f"program[280]={byte(simulator.memory.program.get(0x280))}, "
              f"storage[280]={byte(simulator.memory.storage.get(0x280))}, "
              f"PC={byte(simulator.state.registers[0])}; 96 subdivisions")
        return
    if version == "v005":
        print(f"Result: {len(simulator.trace)} subdivisions, "
              f"PC={byte(simulator.state.registers[0])}, PG={byte(simulator.state.pg)}, "
              f"R3={byte(simulator.state.registers[3])} (unchanged)")
        return
    if version == "v004":
        print(f"Result: R3={byte(simulator.state.registers[3])}, "
              f"R4={byte(simulator.state.registers[4])}, "
              f"devices[04]={byte(simulator.memory.devices.get(0x04))}, "
              f"storage[304]={byte(simulator.memory.storage.get(0x304))} (unchanged)")
        return
    if version == "v003":
        print(f"Result: R3={byte(simulator.state.registers[3])}, "
              f"R4={byte(simulator.state.registers[4])}, "
              f"program[281]={byte(simulator.memory.program.get(0x281))}, "
              f"storage[282]={byte(simulator.memory.storage.get(0x282))}, "
              f"storage[082]={byte(simulator.memory.storage.get(0x082))} (unchanged)")
        return
    print(f"Result: R3={byte(simulator.state.registers[3])}, "
          f"storage[81]={byte(simulator.memory.storage.get(0x81))}, "
          f"PC={byte(simulator.state.registers[0])}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("v001", "v002", "v003", "v004", "v005",
                                          "v006", "v007", "v008", "v009", "v010", "v011",
                                          "v012", "v013", "v014", "v015", "v016", "v017", "v018"),
                        default="v001")
    parser.add_argument("--json", action="store_true", help="print complete trace records")
    args = parser.parse_args()
    if args.model == "v001":
        print(json.dumps([record.to_dict() for record in baseline_demo()], indent=2))
        return
    demos = {"v002": instruction_demo, "v003": paged_instruction_demo,
             "v004": device_instruction_demo, "v005": nop_demo, "v006": flag_demo,
             "v007": indexed_demo, "v008": control_flow_demo, "v009": branch_demo,
             "v010": immediate_copy_demo, "v011": arithmetic_demo, "v012": logical_demo,
             "v013": shift_demo, "v014": exchange_demo, "v015": control_signal_demo,
             "v016": interrupt_demo, "v017": reset_demo, "v018": execution_demo}
    simulator = demos[args.model]()
    if args.json:
        print(json.dumps([record.to_dict() for record in simulator.trace], indent=2))
    elif args.model == "v018":
        show_execution(simulator)
    elif args.model == "v017":
        show_reset(simulator)
    elif args.model == "v016":
        show_interrupts(simulator)
    elif args.model == "v015":
        show_control_signals(simulator)
    elif args.model == "v014":
        show_exchange(simulator)
    elif args.model == "v013":
        show_shifts(simulator)
    elif args.model in {"v011", "v012"}:
        show_arithmetic(simulator)
    elif args.model == "v010":
        show_immediate_copy(simulator)
    elif args.model == "v009":
        show_branches(simulator)
    elif args.model == "v008":
        show_control_flow(simulator)
    elif args.model == "v006":
        show_flags(simulator)
    else:
        show_instructions(simulator)


if __name__ == "__main__":
    main()
