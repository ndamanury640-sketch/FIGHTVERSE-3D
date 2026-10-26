// select.js — character / mode / arena select screen (reference-style roster grid + big splash + START).
import { sfx } from './sfx.js';
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const root = $('#select'); if (root) {
  const chars = JSON.parse($('#roster-data').textContent), by = Object.fromEntries(chars.map(c => [c.slug, c]));
  const logged = root.dataset.logged === '1';
  const st = { slug: chars[5].slug, mode: 'versus', arena: 'crimson-dojo' };
  try { const s = JSON.parse(localStorage.getItem('fv_sel') || '{}'); if (by[s.slug]) st.slug = s.slug; if (['versus', 'training', 'online', 'ranked'].includes(s.mode)) st.mode = s.mode; if (s.arena) st.arena = s.arena; } catch (e) {}
  const q = new URLSearchParams(location.search); if (by[q.get('character')]) st.slug = q.get('character');
  const NOTES = { versus: 'Lawan AI lawan acak. Cocok untuk latihan dan mencoba ultimate.', training: 'Dummy latihan: tidak melawan balik dan HP otomatis pulih.', online: 'Quick match, atau buat room dan bagikan kodenya ke teman. Butuh server online.', ranked: 'Antrean ranked dengan lawan sepadan. Menang = ELO naik. Butuh server online.' };
  const splash = $('#splash'), img = $('#sp-img');
  function showChar(slug, silent) {
    const c = by[slug]; if (!c) return; st.slug = slug;
    $$('.tile[data-slug]').forEach(t => t.classList.toggle('active', t.dataset.slug === slug));
    splash.style.setProperty('--c', c.color); splash.style.setProperty('--c2', c.color2); root.style.setProperty('--c', c.color); root.style.setProperty('--c2', c.color2);
    splash.classList.remove('swap'); void splash.offsetWidth; splash.classList.add('swap');
    img.src = `assets/ui-previews/cut/${slug}.png`; img.alt = c.name;
    $('#sp-name').textContent = c.name.toUpperCase(); $('#sp-title').textContent = (c.style || '').toUpperCase(); $('#sp-no').textContent = String(chars.indexOf(c) + 1).padStart(2, '0');
    $('#sp-desc').textContent = c.description; $('#sp-ult').textContent = c.ult; $('#start-ult').textContent = c.ult;
    $$('#sp-stats i').forEach(i => { const v = c.stats[i.dataset.k]; i.style.setProperty('--v', v * 10 + '%'); i.nextElementSibling.textContent = v; });
    if (!silent) sfx.select();
  }
  function setMode(m) {
    st.mode = m; $$('.mode').forEach(b => b.classList.toggle('active', b.dataset.mode === m));
    let note = NOTES[m]; if ((m === 'online' || m === 'ranked') && !logged) note = 'Login dulu untuk bermain online / ranked.'; if (m === 'ranked' && logged) note += ` ELO kamu: ${root.dataset.elo} (${root.dataset.tier}).`; $('#mode-note').textContent = note; sfx.ui();
  }
  function setArena(id, silent) {
    st.arena = id; let name = '';
    $$('.arena').forEach(b => { const on = b.dataset.arena === id; b.classList.toggle('active', on); if (on) name = b.dataset.name; });
    $('#arena-label').textContent = name; if (!silent) sfx.ui();
  }
  $$('.tile[data-slug]').forEach(t => { t.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover)').matches) showChar(t.dataset.slug); }); t.addEventListener('click', () => showChar(t.dataset.slug)); t.addEventListener('focus', () => showChar(t.dataset.slug, true)); });
  $$('.mode').forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
  $$('.arena').forEach(b => b.addEventListener('click', () => setArena(b.dataset.arena)));
  const tiles = $$('.tile[data-slug]');
  addEventListener('keydown', e => {
    const i = tiles.findIndex(t => t.dataset.slug === st.slug); let n = i;
    if (e.key === 'ArrowRight') n = (i + 1) % tiles.length; else if (e.key === 'ArrowLeft') n = (i - 1 + tiles.length) % tiles.length; else if (e.key === 'ArrowDown') n = Math.min(tiles.length - 1, i + 7); else if (e.key === 'ArrowUp') n = Math.max(0, i - 7); else if (e.key === 'Enter') { start(); return; } else return;
    e.preventDefault(); showChar(tiles[n].dataset.slug);
  });
  function start() {
    if ((st.mode === 'online' || st.mode === 'ranked') && !logged) { location.href = 'login.php'; return; }
    try { localStorage.setItem('fv_sel', JSON.stringify(st)); } catch (e) {}
    sfx.start(); $('#wipe').classList.add('go'); document.body.classList.add('leaving');
    const url = `game.php?character=${encodeURIComponent(st.slug)}&mode=${st.mode}&arena=${encodeURIComponent(st.arena)}`;
    setTimeout(() => { location.href = url; }, 620);
  }
  $('#start-btn').addEventListener('click', start);
  showChar(st.slug, true); setMode(st.mode); setArena(st.arena, true);
}
