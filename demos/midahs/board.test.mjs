import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Midahs} from './board.mjs';
import {readHex,CPU} from '../shared/cpu.mjs';
const file=name=>readFileSync(new URL(name,import.meta.url),'utf8');
const make=()=>{const board=Midahs.fromHex(file('monitor.hex'),file('switches.hex'));board.run();return board;};
const keys=(board,names)=>{for(const key of names)board.tap(key);};

test('monitor starts in PM address mode and displays real program bytes',()=>{
  const b=make();assert.equal(b.kex,true);assert.equal(b.mode,4);
  assert.equal(b.ports[1],0);assert.equal(b.ports[2],0o23);
  b.tap('+');assert.equal(b.ports[1],1);assert.equal(b.ports[2],3);
});
test('keys are acted upon on release, once per press',()=>{
  const b=make();b.press('+');b.run(1000);assert.equal(b.ports[1],0);
  b.release();b.run(1000);assert.equal(b.ports[1],1);
  b.run(1000);assert.equal(b.ports[1],1);
});
test('four-digit addresses, three-digit data entry, readback and page-local increment',()=>{
  const b=make();keys(b,['0','1','2','3']);assert.equal(b.ports[1],0o123);
  keys(b,['DA','2','5','7']);assert.equal(b.program[0o123],0o257);assert.equal(b.ports[2],0o257);
  keys(b,['AD','0','1','2','3']);assert.equal(b.ports[2],0o257);
  keys(b,['0','3','7','7','+']);assert.equal(b.ports[1],0);
});
test('AD cycles PM, SM, IO; monitor really accesses each selected space',()=>{
  const b=make();keys(b,['AD','AD']);assert.equal(b.mode,2);
  keys(b,['0','0','2','0','DA','1','2','3']);assert.equal(b.storage[0o20],0o123);
  assert.equal(b.program[0o20],0);
  keys(b,['AD','AD']);assert.equal(b.mode,1);
  b.ports[3]=0xa5;keys(b,['0','0','0','3']);assert.equal(b.ports[2],0xa5);
  b.tap('+');keys(b,['DA','2','5','2']);assert.equal(b.ports[4],0o252);
  keys(b,['AD','AD']);assert.equal(b.mode,4);
});
test('GO executes user program; KEX preserves user memory and output latches',()=>{
  const b=make();b.tap('GO');assert.equal(b.kex,false);
  for(const value of [0,1,0x80,0xa5,255]){b.ports[3]=value;b.run(100);assert.equal(b.ports[4],value);}
  b.program[100]=0x69;b.enterKex();b.run();
  assert.equal(b.kex,true);assert.equal(b.ports[4],255);assert.equal(b.program[100],0x69);
});
test('GO reaches a program on page one using actual page-2 jump stub',()=>{
  const b=make();b.program.set([0x23,0x69,0x1b,4,0xf1,0],256);
  keys(b,['1','0','0','0','GO']);assert.equal(b.kex,false);assert.equal(b.cpu.pg,1);
  assert.equal(b.ports[4],0x69);assert.equal(b.program[2*256+0o316],0xf1);
  assert.equal(b.program[2*256+0o317],0);
});
test('page 3 rejects writes and KEX recovers from a stopped program',()=>{
  const b=make();const rom=b.program.slice(768);
  keys(b,['3','0','0','0','DA']);assert.throws(()=>b.tap('1'),/ROM/);
  assert.deepEqual(b.program.slice(768),rom);
  b.enterKex();b.run();assert.equal(b.kex,true);
});
test('HEX loader rejects ROM data, including explicitly zero-filled ROM',()=>{
  assert.throws(()=>readHex(':0103000000FC\n:00000001FF',{requireReset:false,addressLimit:768}),/range/);
});
test('logical and rotate instructions preserve expected flags and results',()=>{
  const image=new Uint8Array(1024);
  image.set([0x23,0x81,0x07,0x93,0x05,0x9b,0x2b,0xa0,0x33,0x0f]);
  const c=new CPU(image);c.step();c.step();c.step();
  assert.equal(c.r[3],0x40);assert.equal(c.z,true);assert.equal(c.link,false);
  c.step();c.step();assert.equal(c.r[3],0xa0);assert.equal(c.link,false);
  c.step();assert.equal(c.r[3],0);assert.equal(c.z,true);
  c.step();assert.equal(c.r[3],0);assert.equal(c.z,true);
});

test('enter the complete switch/lamp program by keypad, then run it',()=>{
  const b=make();b.program.fill(0,0,768);
  keys(b,['0','0','0','0','DA']);
  const bytes=[0o23,3,0o33,4,0o360,0];
  for(let i=0;i<bytes.length;i++) {
    if(i)b.tap('+');
    keys(b,bytes[i].toString(8).padStart(3,'0'));
  }
  assert.deepEqual([...b.program.slice(0,6)],bytes);
  keys(b,['AD','0','0','0','0','GO']);
  b.ports[3]=0x5a;b.run(100);
  assert.equal(b.kex,false);assert.equal(b.ports[4],0x5a);
});
test('selected storage page is displayed in the S field and kept separate',()=>{
  const b=make();keys(b,['AD','AD','2','0','0','7','DA','0','6','5']);
  assert.equal(b.mode,2);assert.equal((b.ports[0]>>>3)&7,2);
  assert.equal(b.storage[2*256+7],0o65);assert.equal(b.storage[7],0);
});
test('keyboard routine retains corrected figure 8.10 bytes',()=>{
  const b=make();
  assert.deepEqual([...b.program.slice(768,783)],
    [0x16,5,0x3e,0x2f,255,0xeb,0,0,0x17,5,0x2f,255,0xe3,8,0x0f]);
});
