/* Instruction-level demo core. Cycles are 64 microseconds at the Midahs clock.
 * Unsupported instructions fail explicitly; the research CPU remains authoritative.
 */
export function readHex(text) {
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
    if (type !== 0 || address + count > 1024) throw Error('Only absolute CMC8 data and EOF records are supported');
    for (let i = 0; i < count; ++i) {
      if (present.has(address+i)) throw Error('Overlapping HEX records');
      present.add(address+i); memory[address+i] = bytes[4+i];
    }
  }
  if (!ended) throw Error('Missing HEX EOF');
  if (!present.has(0)) throw Error('Program must include reset address zero');
  return memory;
}

export class CPU {
  constructor(image) {
    this.memory = image.slice();
    // Explicit demo startup state, not a claim that RESET clears every register.
    this.r = new Uint8Array(8); this.n = 0; this.pg = 0;
    this.z = false; this.tests = [false,false,false,false];
    this.cycles = 1; // Initial eight-slot RESET cycle, as in the board fixture.
    this.lamps = 0; this.writes = [];
  }
  fetch() {
    const value = this.memory[this.pg*256 + this.r[this.n]];
    this.r[this.n] = (this.r[this.n]+1) & 255;
    return value;
  }
  step() {
    const location = this.pg*256 + this.r[this.n], op = this.fetch(), reg = op & 7;
    let cycles;
    if (op === 0) cycles = 1;
    else if ((op & 0xf8) === 0x20) { this.r[reg] = this.fetch(); cycles = 2; }
    else if ((op & 0xf8) === 0x40) { const address = this.fetch(); this.r[reg] = this.memory[this.pg*256+address]; cycles = 3; }
    else if ((op & 0xf8) === 0x18) {
      const port = this.fetch();
      if (port !== 4) throw Error(`Demo has no output port ${port}`);
      this.lamps = this.r[reg];
      // WRITE falls at T5 of execute cycle: 21 subdivisions after instruction start.
      this.writes.push({time:(this.cycles*8+21)*8e-6,value:this.lamps}); cycles = 3;
    } else if ((op & 0xf8) === 0x80 || (op & 0xf8) === 0xa0) {
      this.r[reg] = (this.r[reg] + ((op & 0xf8) === 0x80 ? 1 : -1)) & 255;
      this.z = this.r[reg] === 0; cycles = 3;
    } else if (op === 0x0c) {
      const target = this.fetch(); this.n = (this.n+1)&7; this.r[this.n] = target; cycles = 3;
    } else if (op === 0x0f) { this.n = (this.n+7)&7; cycles = 2; }
    else if ((op & 0xfc) === 0xc0 || (op & 0xfc) === 0xc8) {
      const target = this.fetch();
      if (this.tests[op&3] === Boolean(op&8)) this.r[this.n] = target;
      cycles = 2;
    } else if ((op & 0xfc) === 0xf0 || (op & 0xfc) === 0xe0 || (op & 0xfc) === 0xe8) {
      const target = this.fetch();
      if ((op & 0xfc) === 0xf0 || this.z === Boolean(op&8)) { this.pg = op&3; this.r[this.n] = target; }
      cycles = 2;
    } else throw Error(`Unsupported demo opcode 0x${op.toString(16)} at 0x${location.toString(16)}`);
    this.cycles += cycles;
  }
  get time() { return this.cycles * 64e-6; }
}
