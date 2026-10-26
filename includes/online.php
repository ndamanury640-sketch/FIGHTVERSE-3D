<?php
require_once __DIR__.'/../config/online.php';

function online_token(array $user, int $elo): string {
    $payload = ['uid' => (int)$user['id'], 'name' => (string)$user['username'], 'elo' => $elo, 'exp' => time() + 6 * 3600];
    $p = rtrim(strtr(base64_encode(json_encode($payload)), '+/', '-_'), '=');
    return $p . '.' . hash_hmac('sha256', $p, ONLINE_SECRET);
}
function rating_tier(int $elo): array {
    $tiers = [[1900, 'MASTER', '#ff4b6b'], [1700, 'DIAMOND', '#53e6d2'], [1500, 'PLATINUM', '#7ab8ff'], [1300, 'GOLD', '#ffb44a'], [1100, 'SILVER', '#c9d3e6'], [0, 'BRONZE', '#d98a52']];
    foreach ($tiers as $t) if ($elo >= $t[0]) return ['name' => $t[1], 'color' => $t[2]];
    return ['name' => 'BRONZE', 'color' => '#d98a52'];
}
function get_rating(PDO $pdo, int $uid): array {
    $def = ['elo' => 1000, 'peak_elo' => 1000, 'games' => 0, 'wins' => 0, 'losses' => 0, 'draws' => 0];
    try { $q = $pdo->prepare('SELECT elo,peak_elo,games,wins,losses,draws FROM player_ratings WHERE user_id=?'); $q->execute([$uid]); return $q->fetch() ?: $def; }
    catch (Throwable $e) { return $def; } // table missing -> migration not applied yet
}
function elo_expect(int $a, int $b): float { return 1 / (1 + pow(10, ($b - $a) / 400)); }
function elo_next(int $ea, int $eb, float $scoreA, int $ga, int $gb): array {
    $ka = $ga < 10 ? 40 : 24; $kb = $gb < 10 ? 40 : 24;
    return [max(100, (int)round($ea + $ka * ($scoreA - elo_expect($ea, $eb)))), max(100, (int)round($eb + $kb * ((1 - $scoreA) - elo_expect($eb, $ea))))];
}
