import {CPU, readHex} from './cpu.mjs';
const $ = id => document.getElementById(id);
const canvas = $('scene'), ctx = canvas.getContext('2d');
let image, cpu, cars = [], arrivals = [0,0,0,0], paused = false, previous;
let programName = 'Book program', randomState;
// Fixed seed makes restart a reproducible experiment. Speeds and arrivals vary.
function random() { randomState = (1664525*randomState+1013904223)>>>0; return randomState/4294967296; }
// Each side approach averages 150 seconds: 75 seconds combined.
function arrivalInterval(lane) {
  return lane < 2 ? 3+random()*9 : 120+random()*60;
}
function restart() {
  cpu = new CPU(image); cars = []; randomState = 1977;
  arrivals = [1,2,arrivalInterval(2),arrivalInterval(3)];
  paused = false; $('pause').textContent = 'Pause'; previous = undefined;
}
async function restore() {
  try {
    const response = await fetch('traffic.hex');
    if (!response.ok) throw Error('Cannot load bundled traffic.hex');
    image = readHex(await response.text()); programName = 'Book program'; restart();
  } catch (error) { $('status').textContent = error.message; }
}
$('pause').onclick = () => { paused = !paused; $('pause').textContent = paused ? 'Resume' : 'Pause'; };
$('reset').onclick = () => { if (image) restart(); };
$('default').onclick = restore;
$('file').onchange = async event => {
  const file = event.target.files[0]; if (!file) return;
  try { const loaded = readHex(await file.text()); image = loaded; programName = file.name; restart(); }
  catch (error) { $('status').textContent = `Load failed: ${error.message}`; }
  event.target.value = '';
};
function traffic(dt) {
  for (let lane=0;lane<4;lane++) {
    arrivals[lane] -= dt;
    if (arrivals[lane] <= 0) {
      if (!cars.some(c=>c.lane===lane && c.position<45)) cars.push({lane,position:-30,speed:35+random()*25,color:['#63b3ed','#edb863','#d18ce0','#edf0e8'][Math.floor(random()*4)]});
      arrivals[lane] = arrivalInterval(lane);
    }
    const queue = cars.filter(c=>c.lane===lane).sort((a,b)=>b.position-a.position);
    let ahead = Infinity;
    for (const car of queue) {
      const side = lane>=2, stop = side ? 225 : 405;
      const green = Boolean(cpu.lamps & (side ? 128 : 4)), yellow = Boolean(cpu.lamps & (side ? 64 : 2));
      let limit = ahead-45;
      if ((!green || yellow) && car.position<=stop) limit = Math.min(limit,stop);
      car.position = Math.max(car.position, Math.min(car.position+car.speed*dt,limit)); ahead = car.position;
    }
  }
  cars = cars.filter(c=>c.position<(c.lane<2?1050:690));
  cpu.tests[1] = cars.some(c=>c.lane===2 && c.position>130 && c.position<=225);
  cpu.tests[3] = cars.some(c=>c.lane===3 && c.position>130 && c.position<=225);
}
function signal(x,y,side) {
  ctx.fillStyle='#111c25'; ctx.fillRect(x-17,y-42,34,84);
  for (let bit=0;bit<3;bit++) {
    ctx.beginPath(); ctx.arc(x,y-27+27*bit,10,0,Math.PI*2);
    ctx.fillStyle = cpu.lamps & (1<<(bit+(side?5:0))) ? ['#ff5555','#ffcc4d','#59e58c'][bit] : '#34434a'; ctx.fill();
  }
}
function draw() {
  ctx.fillStyle='#20392e'; ctx.fillRect(0,0,1000,640);
  ctx.fillStyle='#3c4852'; ctx.fillRect(0,265,1000,110); ctx.fillRect(445,0,110,640);
  ctx.strokeStyle='#a4a99e'; ctx.setLineDash([20,18]); ctx.lineWidth=2;
  for (const [x,y,a,b] of [[0,320,445,320],[555,320,1000,320],[500,0,500,265],[500,375,500,640]]) {ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(a,b);ctx.stroke();}
  ctx.setLineDash([]); ctx.strokeStyle='white'; ctx.lineWidth=4;
  for(const [x,y,a,b] of [[420,325,420,375],[580,265,580,315],[445,240,495,240],[505,400,555,400]]) {ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(a,b);ctx.stroke();}
  ctx.font='18px system-ui'; ctx.fillStyle='#c7d8c6'; ctx.fillText('MAIN ROAD',32,238); ctx.fillText('SIDE ROAD',580,70);
  for (const c of cars) {
    ctx.save();
    if(c.lane===0) ctx.translate(c.position,348);
    if(c.lane===1) {ctx.translate(1000-c.position,292);ctx.rotate(Math.PI);}
    if(c.lane===2) {ctx.translate(472,c.position);ctx.rotate(Math.PI/2);}
    if(c.lane===3) {ctx.translate(528,640-c.position);ctx.rotate(-Math.PI/2);}
    ctx.fillStyle=c.color;ctx.fillRect(-32,-11,32,22);ctx.fillStyle='#173548';ctx.fillRect(-12,-8,7,16);ctx.restore();
  }
  signal(405,420,false);signal(595,220,false);signal(405,205,true);signal(595,435,true);
  ctx.fillStyle='#dce9ef';ctx.font='15px monospace';
  ctx.fillText(`T1 ${Number(cpu.tests[1])}   T3 ${Number(cpu.tests[3])}`,30,600);
}
function frame(now) {
  if(cpu) {
    const dt = previous===undefined ? 0 : Math.min((now-previous)/1000,0.1)*Number($('speed').value);
    if(!paused) {
      try {
        // Small shared time steps keep sensor sampling and vehicle motion coupled.
        for(let remaining=dt;remaining>0;) {
          const step=Math.min(remaining,0.01), target=cpu.time+step;
          traffic(step); while(cpu.time<target) cpu.step(); remaining-=step;
        }
      } catch(error) {paused=true;$('pause').textContent='Resume';$('status').textContent=error.message;}
    }
    draw();
    if(!paused) $('status').textContent=`${programName} · ${cpu.time.toFixed(2)} simulated seconds · ED4 ${cpu.lamps.toString(8).padStart(3,'0')} · ${cars.length} cars`;
    // Keep observations bounded during arbitrarily long interactive sessions.
    if(cpu.writes.length>64) cpu.writes.splice(0,cpu.writes.length-64);
  }
  previous=now;requestAnimationFrame(frame);
}
restore();requestAnimationFrame(frame);
