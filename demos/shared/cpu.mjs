/* Instruction-level demo core. Cycles are 64 microseconds at the Midahs clock.
 * Functional results follow v018. Interrupt entry and electrical handshakes
 * remain outside this core; boards provide memory, ports and control strobes.
 */
export function readHex(text, {requireReset = true, addressLimit = 1024} = {}) {
  const memory = new Uint8Array(1024), present = new Set();
  let ended = false;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    if (ended || !/^:(?:[0-9a-f]{2})+$/i.test(line)) throw Error('Invalid Intel HEX record');
    const bytes = line.slice(1).match(/../g).map(x => parseInt(x, 16));
    const [count, high, low, type] = bytes;
    if (bytes.length !== count + 5 || (bytes.reduce((a,b) => a+b,0) & 255)) throw Error('Invalid HEX length/checksum');
    const address = high * 256 + low;
    if (type === 1 && count === 0 && address === 0) { ended = true; continue; }
    if (type !== 0) throw Error('Only absolute CMC8 data and EOF records are supported');
    if (address + count > addressLimit) throw Error(`HEX data exceeds allowed program range 0–${addressLimit-1}`);
    for (let i = 0; i < count; ++i) {
      if (present.has(address+i)) throw Error('Overlapping HEX records');
      present.add(address+i); memory[address+i] = bytes[4+i];
    }
  }
  if (!ended) throw Error('Missing HEX EOF');
  if (requireReset && !present.has(0)) throw Error('Program must include reset address zero');
  return memory;
}

export class CPU {
  constructor(image) {
    this.memory = image.slice();
    // Explicit demo startup state, not a claim that RESET clears every register.
    this.r = new Uint8Array(8); this.n = 0; this.pg = 0;
    this.z = false; this.link = false; this.inte = false; this.tests = [false,false,false,false];
    this.cycles = 1; // Initial eight-slot RESET cycle, as in the board fixture.
    this.lamps = 0; this.writes = [];
  }
  fetch() {
    const value = this.memory[this.pg*256 + this.r[this.n]];
    this.r[this.n] = (this.r[this.n]+1) & 255;
    return value;
  }
  readMemory(space, address) {
    if (space !== 'program') throw Error(`No ${space} memory attached`);
    return this.memory[this.pg*256+address];
  }
  writeMemory(space, address, value) { throw Error(`No writable ${space} memory attached`); }
  readPort(port) { throw Error(`Demo has no input port ${port}`); }
  writePort(port, value) {
    if (port !== 4) throw Error(`Demo has no output port ${port}`);
    this.lamps = value;
    this.writes.push({time:(this.cycles*8+21)*8e-6,value});
  }
  control(value, wait) { throw Error(`Control ${wait ? 'SCW' : 'SCS'} is not attached`); }
  setResult(register, value) {
    this.r[register] = value & 255;
    this.z = this.r[register] === 0;
  }

  step() {
    const location = this.pg * 256 + this.r[this.n];
    const opcode = this.fetch();
    const register = opcode & 7;
    const family = opcode & 0xf8;
    let cycles;

    if (opcode === 0) {                         // NOP
      cycles = 1;
    } else if (opcode >= 2 && opcode <= 7) {     // DIN/EIN, REL/SEL, REZ/SEZ
      // Applied at the instruction boundary. In the signaling model these
      // take effect at the following fetch T2; no IRQ sampling occurs here.
      const flag = opcode < 4 ? 'inte' : opcode < 6 ? 'link' : 'z';
      this[flag] = Boolean(opcode & 1);
      cycles = 1;
    } else if (opcode === 8 || opcode === 9) {   // SCW / SCS
      this.control(this.fetch(), opcode === 8);
      cycles = 3;
    } else if (opcode === 0x0c) {                // JSR
      const target = this.fetch();
      this.n = (this.n + 1) & 7;
      this.r[this.n] = target;
      cycles = 3;
    } else if (opcode === 0x0f) {                // RSR
      this.n = (this.n + 7) & 7;
      cycles = 2;
    } else if (family === 0x10) {                // LRD
      this.r[register] = this.readPort(this.fetch());
      cycles = 3;
    } else if (family === 0x18) {                // SRD
      const port = this.fetch();
      this.writePort(port, this.r[register]);
      cycles = 3;
    } else if (family === 0x20) {                // LRI
      this.r[register] = this.fetch();
      cycles = 2;
    } else if (family === 0x28 || family === 0x30) { // XRI / ANI
      const operand = this.fetch();
      const value = family === 0x28
        ? this.r[register] ^ operand : this.r[register] & operand;
      this.setResult(register, value);
      cycles = 3;
    } else if (family === 0x38) {                // CPY
      this.r[7] = this.r[register];
      cycles = 2;
    } else if (family >= 0x40 && family <= 0x78) {
      // LRM/LRX/LRS/LSX and SRM/SRX/SRS/SSX share three encoding bits:
      // bit3 = indexed, bit4 = storage, bit5 = store.
      const address = opcode & 8 ? this.r[7] : this.fetch();
      const space = opcode & 0x10 ? 'storage' : 'program';
      if (opcode & 0x20) this.writeMemory(space, address, this.r[register]);
      else this.r[register] = this.readMemory(space, address);
      cycles = 3;
    } else if (family === 0x80 || family === 0xa0) { // INR / DCR
      this.setResult(register, this.r[register] + (family === 0x80 ? 1 : -1));
      cycles = 3;
    } else if ([0x88, 0x90, 0x98].includes(family)) { // ROR / SHR / RRL
      const value = this.r[register];
      const high = family === 0x88 ? value & 1
        : family === 0x98 ? Number(this.link) : 0;
      this.r[register] = (value >>> 1) | (high << 7);
      if (family === 0x98) this.link = Boolean(value & 1);
      cycles = 2;
    } else if (family === 0xa8 || family === 0xb0) { // XOR / AND
      const value = family === 0xa8
        ? this.r[register] ^ this.r[7] : this.r[register] & this.r[7];
      this.setResult(7, value);
      cycles = 3;
    } else if (family === 0xb8) {                // EXR
      const value = this.r[register];
      this.r[register] = this.r[7];
      this.r[7] = value;
      cycles = 3;
    } else if ((opcode & 0xfc) === 0xc0 || (opcode & 0xfc) === 0xc8) {
      const target = this.fetch();               // BT0 / BT1
      if (this.tests[opcode & 3] === Boolean(opcode & 8)) this.r[this.n] = target;
      cycles = 2;
    } else if (family === 0xd0 || family === 0xd8) { // BB0 / BB1
      const target = this.fetch();
      if (Boolean(this.r[register] & 1) === Boolean(opcode & 8)) this.r[this.n] = target;
      cycles = 3;
    } else if ([0xe0, 0xe4, 0xe8, 0xec, 0xf0].includes(opcode & 0xfc)) {
      const target = this.fetch();               // BZ / BL / JMP
      const condition = opcode & 4 ? this.link : this.z;
      if ((opcode & 0xfc) === 0xf0 || condition === Boolean(opcode & 8)) {
        this.pg = opcode & 3;
        this.r[this.n] = target;
      }
      cycles = 2;
    } else if (family === 0xf8) {                // JCR
      this.r[this.n] = this.r[register];
      cycles = 2;
    } else {
      throw Error(`Unsupported demo opcode 0x${opcode.toString(16)} at 0x${location.toString(16)}`);
    }
    this.cycles += cycles;
  }
  get time() { return this.cycles * 64e-6; }
}
