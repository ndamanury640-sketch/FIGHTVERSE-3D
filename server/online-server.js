#!/usr/bin/env node
/* FIGHTVERSE online server — zero dependencies (Node 18+).
 *   node server/online-server.js
 * Handles: auth (HMAC token from PHP), ranked matchmaking (ELO), casual quick match, private room codes,
 * state/event relay between the two fighters, and match-result reporting to PHP (api/online-result.php).
 * Config is read from ../config/online.php (ONLINE_SECRET, ONLINE_WS_PORT, ONLINE_RESULT_URL); env vars override.
 */
'use strict';
const http = require('http'), crypto = require('crypto'), fs = require('fs'), path = require('path');

function readPhpConfig() {
  const out = {};
  try {
    const src = fs.readFileSync(path.join(__dirname, '..', 'config', 'online.php'), 'utf8');
    for (const m of src.matchAll(/define\(\s*'(\w+)'\s*,\s*(?:'([^']*)'|(\d+))\s*\)/g)) out[m[1]] = m[2] !== undefined ? m[2] : Number(m[3]);
  } catch (e) { console.warn('[config] config/online.php not found, using defaults/env'); }
  return out;
}
const cfg = readPhpConfig();
const SECRET = process.env.ONLINE_SECRET || cfg.ONLINE_SECRET || 'change-this-secret';
const PORT = Number(process.env.PORT || cfg.ONLINE_WS_PORT || 8787);
const RESULT_URL = process.env.ONLINE_RESULT_URL || cfg.ONLINE_RESULT_URL || 'http://127.0.0.1/fightverse-3d/api/online-result.php';
const MIN_SEC = Number(process.env.MIN_MATCH_SECONDS !== undefined ? process.env.MIN_MATCH_SECONDS : 6);
const ARENAS = ['crimson-dojo', 'frozen-citadel', 'volcano-forge', 'storm-peak', 'digital-void', 'neon-rift'];
const CHARS = ['inferno', 'frostbite', 'volt', 'shadow-reaper', 'titan', 'cyber-x', 'jade-monk', 'toxic-fang', 'glitch', 'storm-ronin'];
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);

/* ------------------------------------------------------------------ tokens --- */
function verifyToken(tok) {
  if (typeof tok !== 'string' || tok.length > 600) return null;
  const [p, sig] = tok.split('.'); if (!p || !sig) return null;
  const want = crypto.createHmac('sha256', SECRET).update(p).digest('hex');
  const a = Buffer.from(sig), b = Buffer.from(want); if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try { const d = JSON.parse(Buffer.from(p, 'base64url').toString()); if (!d.uid || d.exp < Date.now() / 1000) return null; return d; } catch (e) { return null; }
}

/* ------------------------------------------------------------ minimal WebSocket --- */
const GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11', MAX_PAYLOAD = 16 * 1024;
class Conn {
  constructor(sock, onMsg, onClose) { this.sock = sock; this.buf = Buffer.alloc(0); this.frag = []; this.fragOp = 0; this.alive = true; this.onMsg = onMsg; this.onClose = onClose; this.closed = false;
    sock.on('data', d => this.feed(d)); sock.on('close', () => this.end()); sock.on('error', () => this.end()); sock.setNoDelay(true); }
  end() { if (this.closed) return; this.closed = true; try { this.sock.destroy(); } catch (e) {} this.onClose(); }
  feed(chunk) {
    this.buf = Buffer.concat([this.buf, chunk]);
    if (this.buf.length > MAX_PAYLOAD * 4) return this.close(1009);
    for (;;) {
      const b = this.buf; if (b.length < 2) return;
      const fin = !!(b[0] & 0x80), op = b[0] & 0x0f, masked = !!(b[1] & 0x80); let len = b[1] & 0x7f, off = 2;
      if (len === 126) { if (b.length < 4) return; len = b.readUInt16BE(2); off = 4; } else if (len === 127) { if (b.length < 10) return; const big = b.readBigUInt64BE(2); if (big > BigInt(MAX_PAYLOAD)) return this.close(1009); len = Number(big); off = 10; }
      if (len > MAX_PAYLOAD) return this.close(1009); if (!masked) return this.close(1002);
      if (b.length < off + 4 + len) return;
      const mask = b.subarray(off, off + 4), data = Buffer.from(b.subarray(off + 4, off + 4 + len)); for (let i = 0; i < len; i++) data[i] ^= mask[i & 3];
      this.buf = b.subarray(off + 4 + len);
      if (op === 8) return this.close(1000); if (op === 9) { this.frame(10, data); continue; } if (op === 10) { this.alive = true; continue; }
      if (op === 1 || op === 2) { this.fragOp = op; this.frag = [data]; } else if (op === 0) this.frag.push(data); else return this.close(1002);
      if (fin) { const full = Buffer.concat(this.frag); this.frag = []; if (this.fragOp === 1) this.onMsg(full.toString('utf8')); }
    }
  }
  frame(op, payload) {
    if (this.closed) return; const len = payload.length; let h;
    if (len < 126) h = Buffer.from([0x80 | op, len]); else if (len < 65536) { h = Buffer.alloc(4); h[0] = 0x80 | op; h[1] = 126; h.writeUInt16BE(len, 2); } else { h = Buffer.alloc(10); h[0] = 0x80 | op; h[1] = 127; h.writeBigUInt64BE(BigInt(len), 2); }
    try { this.sock.write(Buffer.concat([h, payload])); } catch (e) { this.end(); }
  }
  send(obj) { this.frame(1, Buffer.from(typeof obj === 'string' ? obj : JSON.stringify(obj))); }
  close(code = 1000) { if (this.closed) return; const p = Buffer.alloc(2); p.writeUInt16BE(code); this.frame(8, p); setTimeout(() => this.end(), 50); }
}

/* ----------------------------------------------------------------- game state --- */
const clients = new Set(), queues = { ranked: [], casual: [] }, rooms = new Map(), matches = new Map();
const rid = n => crypto.randomBytes(n).toString('hex'), sanitize = (v, list, d) => (list.includes(v) ? v : d);
const eloExpect = (a, b) => 1 / (1 + Math.pow(10, (b - a) / 400));
function eloApply(ea, eb, scoreA, ga = 20, gb = 20) { const ka = ga < 10 ? 40 : 24, kb = gb < 10 ? 40 : 24; return [Math.round(ea + ka * (scoreA - eloExpect(ea, eb))), Math.round(eb + kb * ((1 - scoreA) - eloExpect(eb, ea)))]; }

function removeFromQueues(c) { for (const k of Object.keys(queues)) queues[k] = queues[k].filter(q => q.c !== c); for (const [code, r] of rooms) if (r.host === c) rooms.delete(code); }

function startMatch(a, b, mode) {
  const id = rid(6), m = { id, mode, players: [a.c, b.c], picks: [a, b], ready: new Set(), reports: [null, null], left: [false, false], ended: false, started: Date.now(), timer: null };
  matches.set(id, m); a.c.match = m; b.c.match = m; a.c.side = 0; b.c.side = 1;
  const arena = sanitize(a.arena, ARENAS, ARENAS[Math.floor(Math.random() * ARENAS.length)]), seed = Math.floor(Math.random() * 1e9);
  [a, b].forEach((p, i) => { const o = i ? a : b; p.c.send({ t: 'match', id, side: i, mode, arena, seed, you: { char: p.char }, opp: { name: o.c.name, elo: o.c.elo, char: o.char } }); });
  log('match', id, mode, a.c.name, 'vs', b.c.name, arena);
}
setInterval(() => { // matchmaking tick
  const now = Date.now();
  for (const mode of ['ranked', 'casual']) {
    const q = queues[mode]; q.sort((x, y) => x.since - y.since);
    for (let i = 0; i < q.length; i++) {
      const A = q[i]; if (!A) continue;
      for (let j = i + 1; j < q.length; j++) {
        const B = q[j]; if (!B || A.c.uid === B.c.uid) continue;
        const wait = Math.max(now - A.since, now - B.since) / 1000, range = mode === 'ranked' ? Math.min(900, 100 + wait * 25) : 99999;
        if (Math.abs(A.c.elo - B.c.elo) <= range) { queues[mode] = q.filter(x => x !== A && x !== B); startMatch(A, B, mode); return; }
      }
    }
    for (const p of queues[mode]) if (now - p.lastInfo > 2000) { p.lastInfo = now; p.c.send({ t: 'queued', mode, wait: Math.round((now - p.since) / 1000), size: queues[mode].length }); }
  }
}, 1000);
setInterval(() => { for (const c of clients) { if (!c.conn.alive) { c.conn.end(); continue; } c.conn.alive = false; c.conn.frame(9, Buffer.alloc(0)); } }, 20000);

/* ------------------------------------------------------------- result handling --- */
async function finalize(m, reason) {
  if (m.ended) return; m.ended = true; clearTimeout(m.timer); matches.delete(m.id);
  const [p0, p1] = m.players, r = m.reports; let winner = null; // 0 | 1 | 'draw' | null(unresolved)
  const duration = Math.round((Date.now() - m.started) / 1000);
  if (m.left[0] && !m.left[1]) winner = 1; else if (m.left[1] && !m.left[0]) winner = 0; else if (m.left[0] && m.left[1]) winner = null;
  else if (r[0] && r[1]) { if (r[0] === 'win' && r[1] === 'loss') winner = 0; else if (r[0] === 'loss' && r[1] === 'win') winner = 1; else if (r[0] === 'draw' && r[1] === 'draw') winner = 'draw'; else winner = 'draw'; }
  else if (r[0] === 'loss') winner = 1; else if (r[1] === 'loss') winner = 0; else winner = null;
  if (duration < MIN_SEC && winner !== null && !m.left[0] && !m.left[1]) winner = null; // suspiciously short
  const res = i => winner === null ? null : winner === 'draw' ? 'draw' : (winner === i ? 'win' : 'loss'), ranked = m.mode === 'ranked';
  let out = null;
  if (winner !== null) {
    const body = JSON.stringify({ matchId: m.id, ranked, duration, a: { uid: p0.uid, char: m.picks[0].char, result: res(0) }, b: { uid: p1.uid, char: m.picks[1].char, result: res(1) } });
    try {
      const sig = crypto.createHmac('sha256', SECRET).update(body).digest('hex');
      const resp = await fetch(RESULT_URL, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Signature': sig }, body, signal: AbortSignal.timeout(5000) });
      const j = await resp.json(); if (j && j.ok) out = j;
    } catch (e) { log('result post failed:', e.message); }
    if (!out) { const score = winner === 'draw' ? .5 : winner === 0 ? 1 : 0; const [na, nb] = ranked ? eloApply(p0.elo, p1.elo, score) : [p0.elo, p1.elo]; out = { ok: true, saved: false, a: { old: p0.elo, new: na }, b: { old: p1.elo, new: nb } }; }
  }
  [p0, p1].forEach((c, i) => { const e = out && (i ? out.b : out.a); c.send({ t: 'result', result: res(i), ranked, reason, saved: !!(out && out.saved !== false), elo: e ? { old: e.old, new: e.new, delta: e.new - e.old } : null, tier: e && e.tier || null }); if (e && ranked) c.elo = e.new; c.match = null; });
  log('match end', m.id, winner, reason);
}

function onLeave(c) {
  clients.delete(c); removeFromQueues(c);
  const m = c.match; if (!m || m.ended) return; m.left[c.side] = true;
  const o = m.players[1 - c.side]; if (o && !o.conn.closed) o.send({ t: 'opp_left' });
  setTimeout(() => finalize(m, 'disconnect'), 300);
}

function handle(c, raw) {
  let d; try { d = JSON.parse(raw); } catch (e) { return; } if (!d || typeof d.t !== 'string') return;
  const now = Date.now();
  if (d.t === 'auth') { const v = verifyToken(d.token); if (!v) { c.send({ t: 'err', msg: 'Token tidak valid / kedaluwarsa. Muat ulang halaman.' }); return c.conn.close(4001); }
    for (const o of clients) if (o !== c && o.uid === v.uid) { o.send({ t: 'err', msg: 'Login dari tab lain.' }); o.conn.close(4002); }
    c.uid = v.uid; c.name = String(v.name || 'Player').slice(0, 24); c.elo = Number(v.elo) || 1000; c.auth = true; return c.send({ t: 'hello', name: c.name, elo: c.elo, online: clients.size }); }
  if (!c.auth) return;
  switch (d.t) {
    case 'queue': { if (c.match) return; removeFromQueues(c); const mode = d.mode === 'ranked' ? 'ranked' : 'casual'; queues[mode].push({ c, since: now, lastInfo: 0, char: sanitize(d.char, CHARS, 'cyber-x'), arena: d.arena }); c.send({ t: 'queued', mode, wait: 0, size: queues[mode].length }); break; }
    case 'cancel': removeFromQueues(c); c.send({ t: 'cancelled' }); break;
    case 'create': { if (c.match) return; removeFromQueues(c); let code; do code = crypto.randomBytes(3).toString('hex').toUpperCase().slice(0, 5); while (rooms.has(code)); rooms.set(code, { host: c, char: sanitize(d.char, CHARS, 'cyber-x'), arena: d.arena, at: now }); c.send({ t: 'room', code }); break; }
    case 'join': { if (c.match) return; const code = String(d.code || '').toUpperCase().trim(), r = rooms.get(code); if (!r || r.host === c || r.host.closed) return c.send({ t: 'err', msg: 'Kode room tidak ditemukan.' });
      rooms.delete(code); removeFromQueues(c); startMatch({ c: r.host, char: r.char, arena: r.arena }, { c, char: sanitize(d.char, CHARS, 'cyber-x'), arena: d.arena }, 'casual'); break; }
    case 'ready': { const m = c.match; if (!m || m.ended) return; m.ready.add(c.side); if (m.ready.size === 2) { m.started = Date.now(); m.players.forEach(p => p.send({ t: 'go' })); } break; }
    case 's': case 'ev': { const m = c.match; if (!m || m.ended) return; if (d.t === 's') { if (now - (c.lastS || 0) < 30) return; c.lastS = now; } const o = m.players[1 - c.side]; if (o) { d.f = c.side; o.send(d); } break; }
    case 'end': { const m = c.match; if (!m || m.ended) return; const r = ['win', 'loss', 'draw'].includes(d.result) ? d.result : 'draw'; m.reports[c.side] = r; const o = m.players[1 - c.side]; if (m.reports[0] && m.reports[1]) finalize(m, 'reported'); else if (!m.timer) m.timer = setTimeout(() => finalize(m, 'timeout'), 6000); break; }
    case 'ping': c.send({ t: 'pong', ts: d.ts }); break;
  }
}

/* -------------------------------------------------------------------- server --- */
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify({ ok: true, service: 'fightverse-online', players: clients.size, queued: { ranked: queues.ranked.length, casual: queues.casual.length }, matches: matches.size }));
});
server.on('upgrade', (req, sock) => {
  const key = req.headers['sec-websocket-key']; if (!key || (req.headers.upgrade || '').toLowerCase() !== 'websocket') { sock.destroy(); return; }
  sock.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + crypto.createHash('sha1').update(key + GUID).digest('base64') + '\r\n\r\n');
  const c = { send: o => c.conn.send(o), auth: false, match: null, side: 0, elo: 1000, name: '?', uid: 0 };
  c.conn = new Conn(sock, raw => handle(c, raw), () => onLeave(c)); Object.defineProperty(c, 'closed', { get: () => c.conn.closed }); clients.add(c);
  setTimeout(() => { if (!c.auth) c.conn.close(4000); }, 8000);
});
if (require.main === module) {
  server.listen(PORT, () => { log(`FIGHTVERSE online server listening on :${PORT}`); log(`result endpoint: ${RESULT_URL}`); if (SECRET === 'change-this-secret') log('WARNING: ONLINE_SECRET is still the default. Edit config/online.php!'); });
}
module.exports = { server, eloApply, verifyToken, _state: { clients, queues, rooms, matches } };
