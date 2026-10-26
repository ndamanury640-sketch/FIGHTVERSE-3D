// sfx.js — procedural WebAudio sound effects (no audio files). Shared by the game and the site UI.
let ctx = null, master = null, muted = false;
try { muted = localStorage.getItem('fv_mute') === '1'; } catch (e) {}
function ac() {
  if (!ctx) { const C = window.AudioContext || window.webkitAudioContext; if (!C) return null; ctx = new C(); master = ctx.createGain(); master.gain.value = muted ? 0 : .55; master.connect(ctx.destination); }
  if (ctx.state === 'suspended') ctx.resume(); return ctx;
}
function tone(f0, f1, dur, vol = .3, type = 'sine', delay = 0) {
  const c = ac(); if (!c || muted) return; const t = c.currentTime + delay, o = c.createOscillator(), g = c.createGain();
  o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(.001, t + dur); o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + .02);
}
function noise(dur, f0 = 3000, f1 = 300, vol = .3, q = 1.2, type = 'bandpass', delay = 0) {
  const c = ac(); if (!c || muted) return; const t = c.currentTime + delay, n = Math.floor(c.sampleRate * dur), b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
  const s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain(); s.buffer = b; f.type = type; f.Q.value = q; f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(Math.max(40, f1), t + dur);
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(.001, t + dur); s.connect(f); f.connect(g); g.connect(master); s.start(t);
}
export const sfx = {
  unlock() { ac(); },
  get muted() { return muted; },
  setMuted(v) { muted = !!v; try { localStorage.setItem('fv_mute', muted ? '1' : '0'); } catch (e) {} if (master) master.gain.value = muted ? 0 : .55; },
  hit(heavy) { noise(heavy ? .22 : .12, 2600, 200, heavy ? .55 : .35, 1.5); tone(heavy ? 140 : 190, 45, heavy ? .26 : .14, heavy ? .6 : .4, 'sine'); if (heavy) tone(70, 30, .4, .5, 'sine', .02); },
  block() { noise(.1, 5000, 1800, .25, 4, 'highpass'); tone(520, 300, .1, .2, 'triangle'); },
  slash() { noise(.2, 800, 5200, .25, .9, 'bandpass'); },
  swing() { noise(.14, 600, 3000, .14, .8, 'bandpass'); },
  jump() { tone(220, 520, .12, .12, 'sine'); },
  dash() { noise(.25, 400, 4000, .3, .7, 'bandpass'); tone(160, 380, .2, .1, 'sawtooth'); },
  land() { noise(.1, 500, 80, .25, .8, 'lowpass'); },
  proj() { tone(300, 900, .25, .25, 'sawtooth'); noise(.3, 500, 3000, .2, 1); },
  charge() { tone(90, 700, 1, .3, 'sawtooth'); tone(180, 1400, 1, .15, 'square'); noise(1, 300, 6000, .15, 2, 'bandpass'); },
  ult() { noise(.8, 6000, 80, .6, .8, 'lowpass'); tone(110, 30, .9, .7, 'sine'); tone(880, 440, .5, .25, 'square'); },
  ko() { noise(1, 1800, 60, .6, .8, 'lowpass'); tone(160, 25, 1.2, .6, 'sine'); },
  win() { [523, 659, 784, 1047].forEach((f, i) => tone(f, f, .35, .22, 'triangle', i * .12)); },
  ui() { tone(900, 1300, .05, .08, 'square'); },
  click() { tone(500, 900, .08, .15, 'square'); noise(.06, 4000, 2000, .1, 2, 'highpass'); },
  select() { tone(660, 990, .12, .18, 'triangle'); tone(990, 1320, .12, .12, 'triangle', .08); },
  start() { tone(220, 880, .4, .3, 'sawtooth'); noise(.4, 500, 5000, .3, 1); }
};
window.FVSFX = sfx;
