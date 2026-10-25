import {CPU, readHex} from '../shared/cpu.mjs';

export const KEY_CODES = Object.freeze(Object.fromEntries([
  ...Array.from({length: 8}, (_, i) => [String(i), 0xf0 + 2*i]),
  ['GO', 0xf1], ['AD', 0xf3], ['DA', 0xf5], ['+', 0xf7]
]));

// The CPU knows instruction semantics; this adapter supplies board connections.
class MidahsCPU extends CPU {
  constructor(image, board) {
    super(image);
    this.board = board;
  }

  readPort(port) { return this.board.readPort(port); }
  writePort(port, value) { this.board.writePort(port, value); }
  readMemory(space, address) { return this.board.readMemory(space, address); }
  writeMemory(space, address, value) { this.board.writeMemory(space, address, value); }

  control(value, wait) {
    if (wait) throw Error('SCW handshaking is outside this demo');
    if ((value & 0xc0) === 0x80) this.board.kex = Boolean(value & 1);
  }
}

export class Midahs {
  constructor(monitor, userImage) {
    this.program = new Uint8Array(1024);
    this.storage = new Uint8Array(1024);
    this.program.set(userImage.subarray(0, 768));
    this.program.set(monitor.subarray(768), 768);
    // Explicit demo power-on values for external latches and switches.
    this.ports = new Uint8Array(7);
    this.ports[5] = 255;
    this.key = null;
    this.kex = false;
    this.enterKex();
  }

  enterKex() {
    // Functional equivalent of RESET then injected F3,F3 (JMP3,363o).
    // Latches and RAM survive KEX; startup code initializes the monitor state.
    const old = this.cpu;
    this.cpu = new MidahsCPU(this.program, this);
    this.cpu.memory = this.program;
    if (old) {
      this.cpu.r.set(old.r);
      this.cpu.link = old.link;
      this.cpu.z = old.z;
      this.cpu.inte = old.inte;
    }
    this.cpu.n = 0;
    this.cpu.pg = 3;
    this.cpu.r[0] = 0o363;
    this.kex = false;
    this.release();
  }

  press(key) {
    if (!Object.hasOwn(KEY_CODES, key)) throw Error(`Unknown key ${key}`);
    if (this.key !== null) throw Error('Release the previous key first');
    this.key = key;
    this.ports[5] = KEY_CODES[key];
  }

  release() {
    this.key = null;
    this.ports[5] = 255;
  }

  readPort(port) {
    // Explicit demo open-bus value for unpopulated ports, not an electrical model.
    if (port < 0 || port > 6) return 255;
    return this.ports[port];
  }

  writePort(port, value) {
    if (![0, 1, 2, 4, 6].includes(port)) throw Error(`No writable Midahs port ED${port}`);
    this.ports[port] = value;
  }

  selectedSpace(space, address) {
    // Selected reconstruction: KEX remaps data accesses only. Opcode and
    // operand fetches remain physical PM, keeping page-3 monitor executable.
    if (this.kex) {
      const mode = this.ports[6] & 7;
      if (mode === 1) return ['devices', address];
      if (mode !== 2 && mode !== 4) throw Error('Invalid KEX memory selection');
      const shift = mode === 4 ? 0 : 3;
      const page = (this.ports[0] >>> shift) & 3;
      return [mode === 4 ? 'program' : 'storage', page*256 + address];
    }
    return [space, this.cpu.pg*256 + address];
  }

  readMemory(space, address) {
    const [selected, full] = this.selectedSpace(space, address);
    if (selected === 'devices') return this.readPort(full);
    return (selected === 'program' ? this.program : this.storage)[full];
  }

  writeMemory(space, address, value) {
    const [selected, full] = this.selectedSpace(space, address);
    if (selected === 'devices') return this.writePort(full, value);
    if (selected === 'program' && full >= 768) {
      throw Error('Page 3 is monitor ROM; press KEX to resume');
    }
    (selected === 'program' ? this.program : this.storage)[full] = value;
  }

  run(instructions = 1000) {
    for (let i = 0; i < instructions; i++) this.cpu.step();
  }

  // Scriptable equivalent of a human press/release, executing real CPU steps.
  tap(key) {
    this.press(key);
    this.run(100);
    this.release();
    this.run(200);
  }

  get mode() { return this.ports[6] & 7; }

  static fromHex(monitor, user) {
    return new Midahs(readHex(monitor, {requireReset: false}),
                      readHex(user, {addressLimit: 768}));
  }
}
