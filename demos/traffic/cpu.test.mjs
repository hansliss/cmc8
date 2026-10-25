import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {CPU,readHex} from './cpu.mjs';
const text = readFileSync(new URL('traffic.hex',import.meta.url),'utf8');
const canonical = JSON.parse(readFileSync(new URL('../../specification/traffic-program.json',import.meta.url)));
const reference = JSON.parse(readFileSync(new URL('../../specification/traffic-validation.json',import.meta.url)));

test('bundled HEX preserves every independent book byte',()=>{
  const image=readHex(text);
  for(const cell of canonical.cells) assert.equal(image[parseInt(cell.address,8)],parseInt(cell.byte,8));
});
for(const sensor of [1,3]) test(`literal light sequence and exact intervals, T${sensor}`,()=>{
  const cpu=new CPU(readHex(text)); cpu.tests[sensor]=true;
  let instructions=0;
  while(cpu.writes.length<7 && ++instructions<1000000) cpu.step();
  assert.deepEqual(cpu.writes.map(w=>w.value),reference.port_writes.map(w=>w.value));
  assert.equal(cpu.writes[0].time,reference.port_writes[0].time_ns/1e9);
  for(let i=2;i<7;i++) {
    const actual=cpu.writes[i].time-cpu.writes[i-1].time;
    const expected=(reference.port_writes[i].time_ns-reference.port_writes[i-1].time_ns)/1e9;
    assert.ok(Math.abs(actual-expected)<1e-10,`interval ${i}: ${actual} != ${expected}`);
  }
});
test('no demand leaves main green; pulse initiates service',()=>{
  const cpu=new CPU(readHex(text));
  for(let i=0;i<200;i++) cpu.step();
  assert.equal(cpu.writes.length,1); assert.equal(cpu.lamps,0o44);
  cpu.tests[1]=true;
  for(let i=0;i<10 && cpu.writes.length<2;i++) cpu.step();
  cpu.tests[1]=false;
  assert.equal(cpu.lamps,0o46);
});
test('register-selected return preserves caller PC',()=>{
  const image=new Uint8Array(1024);image.set([0x0c,0x10]);image[0x10]=0x0f;
  const cpu=new CPU(image);cpu.step();
  assert.equal(cpu.n,1);assert.equal(cpu.r[0],2);assert.equal(cpu.r[1],16);
  cpu.step();assert.equal(cpu.n,0);assert.equal(cpu.r[0],2);assert.equal(cpu.cycles,6);
});
test('page-local operand wrapping and conditional page change',()=>{
  const image=new Uint8Array(1024);image[255]=0xe9;image[0]=42;
  const cpu=new CPU(image);cpu.r[0]=255;cpu.z=true;cpu.step();
  assert.equal(cpu.pg,1);assert.equal(cpu.r[0],42);
});
test('unsupported instructions and devices fail explicitly',()=>{
  const image=new Uint8Array(1024);image[0]=1;
  assert.throws(()=>new CPU(image).step(),/Unsupported/);
  image.set([0x18,5]);assert.throws(()=>new CPU(image).step(),/no output port/);
});
test('HEX rejects corrupt, absent, overlapping and out-of-range records',()=>{
  for(const source of ['',text.replace(':100000',':110000'),text+':00000001FF\n',
    ':0104000000FB\n:00000001FF',':00000001FF',text.replace(':00000001FF',text)]) {
    assert.throws(()=>readHex(source));
  }
});

test('persistent demand retriggers after 640 microseconds; no minimum main green',()=>{
  const cpu=new CPU(readHex(text)); cpu.tests[1]=true;
  let instructions=0;
  while(cpu.writes.length<8 && ++instructions<1000000) cpu.step();
  assert.equal(cpu.writes.length,8);
  assert.equal(cpu.writes[6].value,0o44);
  assert.equal(cpu.writes[7].value,0o46);
  assert.ok(Math.abs(cpu.writes[7].time-cpu.writes[6].time-0.000640)<1e-10);
  cpu.tests[1]=false;
  while(cpu.writes.length<13 && ++instructions<2000000) cpu.step();
  assert.equal(cpu.writes.length,13);
  assert.equal(cpu.lamps,0o44);
  for(let i=0;i<1000;i++) cpu.step();
  assert.equal(cpu.writes.length,13,'with demand removed, main green persists');
});
