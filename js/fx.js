// fx.js — page-level polish: particle field, cursor glow, reveal-on-scroll, card tilt, count-up, scroll progress.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---- particle field (embers + diamonds drifting upward) ---- */
  const cv = $('#fx-bg');
  if (cv && !reduce) {
    const ctx = cv.getContext('2d'); let W = 0, H = 0, dpr = 1, ps = [], run = true;
    const cols = ['255,75,107', '83,230,210', '165,107,255', '255,180,74'];
    const make = (init) => ({ x: Math.random() * W, y: init ? Math.random() * H : H + 20, r: Math.random() * 2 + .6, vy: -(Math.random() * .35 + .08), vx: (Math.random() - .5) * .15, c: cols[Math.floor(Math.random() * cols.length)], a: Math.random() * .6 + .2, t: Math.random() * 6, d: Math.random() < .25 });
    const resize = () => { dpr = Math.min(devicePixelRatio || 1, 1.5); W = innerWidth; H = innerHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); const n = Math.round(Math.min(90, W * H / 18000)); ps = Array.from({ length: n }, () => make(true)); };
    resize(); addEventListener('resize', resize); document.addEventListener('visibilitychange', () => { run = !document.hidden; if (run) loop(); });
    function loop() {
      if (!run) return; ctx.clearRect(0, 0, W, H);
      for (const p of ps) {
        p.t += .02; p.y += p.vy; p.x += p.vx + Math.sin(p.t) * .1; if (p.y < -20) Object.assign(p, make(false));
        const a = p.a * (.6 + .4 * Math.sin(p.t * 2)); ctx.fillStyle = `rgba(${p.c},${a})`; ctx.shadowColor = `rgba(${p.c},.9)`; ctx.shadowBlur = 10;
        if (p.d) { ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.t); ctx.fillRect(-p.r * 1.4, -p.r * 1.4, p.r * 2.8, p.r * 2.8); ctx.restore(); } else { ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill(); }
      }
      requestAnimationFrame(loop);
    }
    loop();
  }

  /* ---- cursor glow ---- */
  const cur = $('.fx-cursor');
  if (cur && !reduce && matchMedia('(pointer:fine)').matches) addEventListener('pointermove', e => { cur.style.transform = `translate3d(${e.clientX}px,${e.clientY}px,0)`; }, { passive: true });
  else if (cur) cur.style.display = 'none';

  /* ---- reveal on scroll ---- */
  const rv = $$('.reveal');
  if ('IntersectionObserver' in window && rv.length) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    rv.forEach(el => io.observe(el));
  } else rv.forEach(el => el.classList.add('in'));

  /* ---- tilt cards ---- */
  if (!reduce && matchMedia('(pointer:fine)').matches) $$('[data-tilt]').forEach(el => {
    el.addEventListener('pointermove', e => {
      const r = el.getBoundingClientRect(), px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
      el.style.setProperty('--ry', ((px - .5) * 10).toFixed(2) + 'deg'); el.style.setProperty('--rx', ((.5 - py) * 8).toFixed(2) + 'deg');
      el.style.setProperty('--mx', (px * 100).toFixed(1) + '%'); el.style.setProperty('--my', (py * 100).toFixed(1) + '%');
    });
    el.addEventListener('pointerleave', () => { el.style.setProperty('--rx', '0deg'); el.style.setProperty('--ry', '0deg'); });
  });

  /* ---- count up ---- */
  $$('[data-count]').forEach(el => {
    const target = +el.dataset.count; if (!target || reduce) return; el.textContent = '0';
    const io = new IntersectionObserver(es => { if (!es[0].isIntersecting) return; io.disconnect(); const t0 = performance.now(), dur = 1100;
      const step = t => { const k = Math.min(1, (t - t0) / dur); el.textContent = Math.round(target * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); }; requestAnimationFrame(step); });
    io.observe(el);
  });

  /* ---- scroll progress + topbar shrink ---- */
  const bar = $('#scroll-progress'), top = $('.topbar');
  const onScroll = () => { const h = document.documentElement; const k = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight); if (bar) bar.style.transform = `scaleX(${k})`; if (top) top.classList.toggle('small', h.scrollTop > 40); };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* ================= v4 extras: loader, click burst, cursor trail, parallax, UI sounds ================= */
  const sfxp = () => window.FVSFX;
  try { const ld = $('#fv-loader'); if (ld) { if (document.documentElement.classList.contains('no-loader')) ld.remove(); else { sessionStorage.setItem('fv_ld', '1'); setTimeout(() => ld.classList.add('done'), 1100); setTimeout(() => ld.remove(), 1900); } } } catch (e) {}

  // click shockwave + sparks (not over the game canvas)
  addEventListener('pointerdown', e => {
    if (reduce || e.target.closest && e.target.closest('#game-app')) return;
    const r = document.createElement('div'); r.className = 'fx-ripple'; r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; document.body.appendChild(r); setTimeout(() => r.remove(), 700);
    for (let i = 0; i < 9; i++) { const sp = document.createElement('i'), a = Math.random() * 6.283, d = 30 + Math.random() * 60; sp.className = 'fx-spark'; sp.style.cssText = `left:${e.clientX}px;top:${e.clientY}px;--dx:${Math.cos(a) * d}px;--dy:${Math.sin(a) * d}px;--c:${['#ff4b6b', '#53e6d2', '#ffb44a', '#a56bff'][i % 4]}`; document.body.appendChild(sp); setTimeout(() => sp.remove(), 650); }
  }, { passive: true });

  // cursor trail (desktop only)
  if (!reduce && matchMedia('(pointer:fine)').matches) {
    const tc = document.createElement('canvas'); tc.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:9960'; document.body.appendChild(tc);
    const tx = tc.getContext('2d'); let pts = [], TW = 0, TH = 0; const rs = () => { TW = tc.width = innerWidth; TH = tc.height = innerHeight; }; rs(); addEventListener('resize', rs);
    addEventListener('pointermove', e => { pts.push({ x: e.clientX, y: e.clientY, a: 1, s: 3 + Math.random() * 3, h: (performance.now() / 8) % 360 }); if (pts.length > 40) pts.shift(); }, { passive: true });
    (function tick() { tx.clearRect(0, 0, TW, TH); tx.globalCompositeOperation = 'lighter'; for (const p of pts) { p.a -= .035; if (p.a > 0) { tx.fillStyle = `hsla(${p.h},100%,65%,${p.a * .7})`; tx.shadowColor = `hsl(${p.h},100%,60%)`; tx.shadowBlur = 12; tx.beginPath(); tx.arc(p.x, p.y, p.s * p.a, 0, 6.283); tx.fill(); } } pts = pts.filter(p => p.a > 0); requestAnimationFrame(tick); })();
  }

  // mouse parallax for versus key-art
  const arts = $$('.vsart'); if (arts.length && !reduce) { let tx2 = 0, ty2 = 0, raf = 0; addEventListener('pointermove', e => { tx2 = e.clientX / innerWidth * 2 - 1; ty2 = e.clientY / innerHeight * 2 - 1; if (!raf) raf = requestAnimationFrame(() => { raf = 0; arts.forEach(a => { a.style.setProperty('--px', tx2.toFixed(3)); a.style.setProperty('--py', ty2.toFixed(3)); }); }); }, { passive: true }); }

  // UI sounds + sound toggle in the top bar
  let lastHover = null, lastT = 0;
  document.addEventListener('pointerover', e => { const t = e.target.closest && e.target.closest('a.button,button.button,.fcard,.tabs a,.topbar nav a,.feature'); if (t && t !== lastHover && performance.now() - lastT > 70) { lastHover = t; lastT = performance.now(); const s = sfxp(); if (s) s.ui(); } else if (!t) lastHover = null; });
  document.addEventListener('click', e => { const t = e.target.closest && e.target.closest('a.button,button.button,.nav-cta'); if (t) { const s = sfxp(); if (s) s.click(); } });
  const bar2 = $('.topbar'); if (bar2 && !$('#nav-mute')) { const b = document.createElement('button'); b.id = 'nav-mute'; b.type = 'button'; b.className = 'nav-mute'; b.title = 'Sound'; const upd = () => { const s = sfxp(); b.textContent = s && s.muted ? '🔇' : '🔊'; }; b.addEventListener('click', () => { const s = sfxp(); if (s) { s.unlock(); s.setMuted(!s.muted); upd(); if (!s.muted) s.select(); } }); bar2.appendChild(b); setTimeout(upd, 400); }
})();
