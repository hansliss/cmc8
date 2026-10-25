/* Exercise actual browser event handlers against a small DOM test adapter.
 * This checks interaction wiring; it does not replace visual browser testing.
 */
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.dataset = {};
    this.events = {};
    this.textContent = '';
    const classes = new Set();
    this.classList = {
      add: name => classes.add(name),
      remove: name => classes.delete(name),
      toggle: (name, enabled) => enabled ? classes.add(name) : classes.delete(name),
      contains: name => classes.has(name)
    };
  }
  append(...children) { this.children.push(...children); }
  addEventListener(name, handler) { this.events[name] = handler; }
  setAttribute() {}
  setPointerCapture() {}
  querySelectorAll(tag) {
    return this.children.flatMap(child => child instanceof Element
      ? [...(child.tagName === tag.toUpperCase() ? [child] : []), ...child.querySelectorAll(tag)] : []);
  }
}

test('faceplate keys, switches, KEX, pause and file-error feedback', async () => {
  const html = readFileSync(new URL('index.html', import.meta.url), 'utf8');
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(match => [match[1], new Element()]));
  const all = () => Object.values(elements).flatMap(element => [element, ...element.querySelectorAll('button'), ...element.querySelectorAll('span')]);
  globalThis.document = {
    getElementById: id => elements[id] || all().find(element => element.id === id),
    createElement: tag => new Element(tag),
    createTextNode: text => text,
    querySelector: selector => all().find(element => element.dataset.key === selector.match(/data-key="(.+)"/)[1]),
    querySelectorAll: () => all().filter(element => element.classList.contains('pressed'))
  };
  const windowEvents = {};
  globalThis.window = {addEventListener: (name, handler) => {windowEvents[name] = handler;}};
  globalThis.fetch = async name => ({ok: true, text: async () => readFileSync(new URL(name, import.meta.url), 'utf8')});
  let nextFrame, now = 0;
  globalThis.requestAnimationFrame = callback => {nextFrame = callback;};
  elements.speed.value = '10';
  await import('./app.mjs');
  await new Promise(resolve => setImmediate(resolve));
  const advance = () => {now += 20; nextFrame(now);};
  advance(); advance();
  assert.equal(elements.data.textContent, '023');
  assert.match(elements.mode.textContent, /KEX.*AD/);

  const tap = key => {
    const button = elements.keys.children.find(child => child.dataset.key === key);
    button.events.pointerdown({preventDefault() {}, pointerId: 1});
    advance(); button.events.pointerup(); advance();
  };
  tap('+'); assert.equal(elements.address.textContent, '001');
  for (const key of ['0','0','0','0','GO']) tap(key);
  assert.equal(elements.mode.textContent, 'USER PROGRAM');
  const switch7 = elements.switches.querySelectorAll('input').find(input => input.dataset.bit == 7);
  switch7.checked = true; switch7.onchange(); advance();
  assert.ok(document.getElementById('lamp-7').classList.contains('on'));

  elements.pause.onclick(); advance();
  assert.match(elements.status.textContent, /Paused/);
  assert.equal(elements.step.disabled, false);
  elements.step.onclick(); advance(); assert.match(elements.status.textContent, /Paused/);
  windowEvents.keydown({key: 'Escape', target: new Element('input'), preventDefault() {}});
  advance(); assert.match(elements.mode.textContent, /KEX/);

  await elements.load.onchange({target: {files: [{name: 'bad.hex', text: async () => 'invalid'}]}});
  advance(); assert.match(elements.status.textContent, /Load failed/);
  advance(); assert.match(elements.status.textContent, /Load failed/);
});
