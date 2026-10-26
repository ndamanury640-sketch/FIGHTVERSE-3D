<?php
// Server-to-server endpoint: called by server/online-server.js when an online match ends.
// Authenticated with HMAC-SHA256(body, ONLINE_SECRET) in the X-Signature header (no browser session).
declare(strict_types=1);
require_once __DIR__.'/../config/database.php';
require_once __DIR__.'/../includes/online.php';
header('Content-Type: application/json; charset=utf-8');
$raw = file_get_contents('php://input') ?: '';
$sig = $_SERVER['HTTP_X_SIGNATURE'] ?? '';
if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !hash_equals(hash_hmac('sha256', $raw, ONLINE_SECRET), $sig)) { http_response_code(403); echo json_encode(['ok' => false, 'error' => 'forbidden']); exit; }
$b = json_decode($raw, true);
$valid = fn($s) => in_array($s['result'] ?? '', ['win', 'loss', 'draw'], true);
if (!is_array($b) || empty($b['matchId']) || !isset($b['a'], $b['b']) || !$valid($b['a']) || !$valid($b['b'])) { http_response_code(422); echo json_encode(['ok' => false, 'error' => 'bad payload']); exit; }
$ranked = !empty($b['ranked']); $dur = max(0, min(999, (int)($b['duration'] ?? 0)));
$slug = fn($s) => preg_replace('/[^a-z0-9-]/', '', strtolower((string)$s));
try {
    $pdo->beginTransaction();
    $dup = $pdo->prepare('INSERT IGNORE INTO online_matches(match_id,ranked) VALUES(?,?)'); $dup->execute([substr((string)$b['matchId'], 0, 32), $ranked ? 1 : 0]);
    if ($dup->rowCount() === 0) { $pdo->rollBack(); echo json_encode(['ok' => true, 'saved' => false, 'duplicate' => true]); exit; }
    $ids = [(int)$b['a']['uid'], (int)$b['b']['uid']]; $rows = [];
    foreach ($ids as $uid) {
        $pdo->prepare('INSERT IGNORE INTO player_ratings(user_id) VALUES(?)')->execute([$uid]);
        $q = $pdo->prepare('SELECT * FROM player_ratings WHERE user_id=? FOR UPDATE'); $q->execute([$uid]); $rows[] = $q->fetch();
    }
    if (!$rows[0] || !$rows[1]) throw new RuntimeException('user missing');
    $ea = (int)$rows[0]['elo']; $eb = (int)$rows[1]['elo']; $na = $ea; $nb = $eb;
    if ($ranked) { $score = $b['a']['result'] === 'win' ? 1.0 : ($b['a']['result'] === 'draw' ? .5 : 0.0); [$na, $nb] = elo_next($ea, $eb, $score, (int)$rows[0]['games'], (int)$rows[1]['games']); }
    $charQ = $pdo->prepare('SELECT id FROM characters WHERE slug=?');
    $cid = function($s) use ($charQ, $slug) { $charQ->execute([$slug($s)]); return (int)$charQ->fetchColumn(); };
    $c = [$cid($b['a']['char'] ?? ''), $cid($b['b']['char'] ?? '')];
    $sides = [[$b['a'], $ids[0], $c[0], $c[1], $ea, $na, $rows[0]], [$b['b'], $ids[1], $c[1], $c[0], $eb, $nb, $rows[1]]];
    $out = [];
    foreach ($sides as $i => [$s, $uid, $mine, $theirs, $old, $new, $row]) {
        $r = $s['result'];
        if ($mine && $theirs) $pdo->prepare('INSERT INTO matches(player_id,player_character_id,opponent_character_id,game_mode,difficulty,result,duration_seconds,damage_dealt,successful_hits) VALUES(?,?,?,?,"normal",?,?,0,0)')->execute([$uid, $mine, $theirs, $ranked ? 'ranked' : 'online', $r, $dur]);
        $pdo->prepare('INSERT INTO player_statistics(user_id,total_matches,wins,losses,draws,total_damage) VALUES(?,1,?,?,?,0) ON DUPLICATE KEY UPDATE total_matches=total_matches+1,wins=wins+VALUES(wins),losses=losses+VALUES(losses),draws=draws+VALUES(draws)')->execute([$uid, $r === 'win' ? 1 : 0, $r === 'loss' ? 1 : 0, $r === 'draw' ? 1 : 0]);
        if ($ranked) $pdo->prepare('UPDATE player_ratings SET elo=?,peak_elo=GREATEST(peak_elo,?),games=games+1,wins=wins+?,losses=losses+?,draws=draws+? WHERE user_id=?')->execute([$new, $new, $r === 'win' ? 1 : 0, $r === 'loss' ? 1 : 0, $r === 'draw' ? 1 : 0, $uid]);
        $out[$i] = ['old' => $old, 'new' => $new, 'tier' => rating_tier($new)['name']];
    }
    $pdo->commit();
    echo json_encode(['ok' => true, 'saved' => true, 'a' => $out[0], 'b' => $out[1]]);
} catch (Throwable $e) { if ($pdo->inTransaction()) $pdo->rollBack(); http_response_code(500); echo json_encode(['ok' => false, 'error' => 'db error']); }
