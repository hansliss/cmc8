import {Midahs} from './board.mjs';
import {readHex} from '../shared/cpu.mjs';

const $ = id => document.getElementById(id);
const octal = (value, width = 3) => value.toString(8).padStart(width, '0');
let monitor, defaultProgram, board, previous;
let paused = false, error = null, notice = null;
let programName = 'Switches → lamps', simulatedTarget = 0;

function startup(image) {
  board = new Midahs(monitor, image);
  simulatedTarget = board.cpu.time;
  previous = undefined;
  error = null;
  notice = null;
  paused = false;
  $('pause').textContent = 'Pause';
  draw();
}

function recover() {
  if (!board) return;
  board.enterKex();
  simulatedTarget = board.cpu.time;
  error = null;
  notice = null;
  paused = false;
  $('pause').textContent = 'Pause';
}

function fail(problem) {
  error = problem.message;
  paused = true;
  release();
  $('pause').textContent = 'Resume';
}

function press(key) {
  if (!board || error || board.key !== null) return;
  board.press(key);
  document.querySelector(`[data-key="${key}"]`)?.classList.add('pressed');
}

function release() {
  board?.release();
  document.querySelectorAll('.pressed').forEach(key => key.classList.remove('pressed'));
}

for (const name of ['7', '6', '5', 'GO', '4', '3', '2', 'AD', '1', '0', '+', 'DA']) {
  const button = document.createElement('button');
  button.textContent = name;
  button.dataset.key = name;
  button.addEventListener('pointerdown', event => {
    event.preventDefault();
    button.setPointerCapture(event.pointerId);
    press(name);
  });
  button.addEventListener('pointerup', release);
  button.addEventListener('pointercancel', release);
  // Assistive activation has no pointer hold. Supply a pulse long enough
  // for the running CPU to observe it across several animation frames.
  button.addEventListener('click', event => {
    if (event.detail === 0) {
      press(name);
      setTimeout(release, 100);
    }
  });
  $('keys').append(button);
}

for (let bit = 7; bit >= 0; bit--) {
  const lamp = document.createElement('div');
  lamp.className = 'lamp-item';
  const light = document.createElement('span');
  light.className = 'lamp';
  light.id = `lamp-${bit}`;
  lamp.append(light, document.createTextNode(String(bit)));
  $('lamps').append(lamp);

  const label = document.createElement('label');
  const input = document.createElement('input');
  input.type = 'checkbox';
  input.setAttribute('aria-label', `Input switch bit ${bit}`);
  input.dataset.bit = bit;
  input.onchange = () => {
    if (board) board.ports[3] = (board.ports[3] & ~(1 << bit)) | (Number(input.checked) << bit);
  };
  label.append(input, document.createTextNode(String(bit)));
  $('switches').append(label);
}

const shortcuts = {Enter: 'GO', a: 'AD', d: 'DA', '+': '+', '=': '+'};
function keyName(event) {
  if (/^[0-7]$/.test(event.key)) return event.key;
  return shortcuts[event.key.toLowerCase()] || shortcuts[event.key];
}
window.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    event.preventDefault();
    release();
    recover();
    return;
  }
  if (['INPUT', 'SELECT', 'SUMMARY'].includes(event.target.tagName)) return;
  const key = keyName(event);
  if (key) {
    event.preventDefault();
    if (!event.repeat) press(key);
  }
});
window.addEventListener('keyup', event => {
  if (board?.key === keyName(event)) release();
});
window.addEventListener('blur', release);

$('kex').onclick = () => { release(); recover(); };
$('pause').onclick = () => {
  paused = !paused;
  $('pause').textContent = paused ? 'Resume' : 'Pause';
  simulatedTarget = board?.cpu.time || 0;
};
$('step').onclick = () => {
  if (!board) return;
  paused = true;
  $('pause').textContent = 'Resume';
  try { board.cpu.step(); }
  catch (problem) { fail(problem); }
  draw();
};
$('restore').onclick = () => {
  if (defaultProgram) {
    programName = 'Switches → lamps';
    startup(defaultProgram);
  }
};
$('load').onchange = async event => {
  const file = event.target.files[0];
  if (!file || !monitor) return;
  try {
    const image = readHex(await file.text(), {addressLimit: 768});
    programName = file.name;
    startup(image);
  } catch (problem) {
    notice = `Load failed: ${problem.message}`;
  }
  event.target.value = '';
};

function draw() {
  if (!board) return;
  const ports = board.ports, cpu = board.cpu;
  const page = octal(ports[0]);
  $('page').textContent = [0, 1, 2].map(i => (ports[6] & (1 << i)) ? page[i] : ' ').join('');
  $('address').textContent = octal(ports[1]);
  $('data').textContent = octal(ports[2]);
  for (let bit = 0; bit < 8; bit++) {
    $('lamp-' + bit).classList.toggle('on', Boolean(ports[4] & (1 << bit)));
  }
  for (const input of $('switches').querySelectorAll('input')) {
    input.checked = Boolean(ports[3] & (1 << Number(input.dataset.bit)));
  }
  $('mode').textContent = board.kex ? `KEX · ${cpu.r[3] & 1 ? 'DA' : 'AD'}` : 'USER PROGRAM';
  $('cpu').textContent = `PG ${cpu.pg} · N ${cpu.n} · PC ${octal(cpu.r[cpu.n])} · `
    + `Z ${Number(cpu.z)} · L ${Number(cpu.link)} · ${cpu.time.toFixed(3)} s`;
  $('registers').textContent = Array.from(cpu.r, (value, i) => `R${i} ${octal(value)}`).join('   ');
  $('status').textContent = error ? `${error} — press KEX to recover`
    : notice || `${programName} · ${paused ? 'Paused' : 'Running'}`;
  $('step').disabled = !paused || Boolean(error);
}

function frame(now) {
  if (board && !paused && !error) {
    const dt = previous === undefined ? 0 : Math.min((now - previous) / 1000, 0.1);
    simulatedTarget += dt * Number($('speed').value);
    try {
      // Bound work per frame so even unusual user code keeps the panel responsive.
      for (let budget = 0; board.cpu.time < simulatedTarget && budget < 20000; budget++) {
        board.cpu.step();
      }
      simulatedTarget = Math.min(simulatedTarget, board.cpu.time + 0.1);
    } catch (problem) {
      fail(problem);
    }
  }
  previous = now;
  draw();
  requestAnimationFrame(frame);
}

async function loadDefaults() {
  try {
    const texts = await Promise.all(['monitor.hex', 'switches.hex'].map(async name => {
      const response = await fetch(name);
      if (!response.ok) throw Error(`Cannot load ${name}`);
      return response.text();
    }));
    monitor = readHex(texts[0], {requireReset: false});
    defaultProgram = readHex(texts[1]);
    startup(defaultProgram);
  } catch (problem) {
    $('status').textContent = problem.message;
  }
}

loadDefaults();
requestAnimationFrame(frame);
