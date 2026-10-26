<?php
require_once __DIR__.'/includes/bootstrap.php'; require_once __DIR__.'/includes/online.php';
$tab=($_GET['tab']??'')==='ranked'?'ranked':'overall'; $rows=[]; $note='';
if($tab==='ranked'){
  try{ $rows=$pdo->query("SELECT u.username,r.elo,r.games,r.wins,r.losses,r.draws,r.peak_elo FROM player_ratings r JOIN users u ON u.id=r.user_id WHERE u.status='active' AND r.games>0 ORDER BY r.elo DESC, r.wins DESC LIMIT 50")->fetchAll(); }
  catch(Throwable $e){ $note='Tabel ranked belum dibuat. Import database/migration_online.sql terlebih dahulu.'; }
}else{
  $rows=$pdo->query("SELECT u.username,s.total_matches,s.wins,s.losses,CASE WHEN s.total_matches>0 THEN ROUND(s.wins/s.total_matches*100) ELSE 0 END win_rate FROM users u JOIN player_statistics s ON s.user_id=u.id WHERE u.status='active' ORDER BY s.wins DESC, win_rate DESC, s.total_matches DESC, u.username ASC LIMIT 50")->fetchAll();
}
$pageTitle='Leaderboard';include __DIR__.'/includes/header.php'; ?>
<section class="page-head reveal"><div><div class="eyebrow">GLOBAL RANKINGS</div><h1>THE <span>LEADERBOARD.</span></h1><p class="muted">Peringkat overall dari semua pertandingan, atau peringkat ELO dari mode ranked online.</p></div></section>
<div class="tabs" style="margin-inline:max(5vw,22px)"><a class="<?= $tab==='overall'?'active':'' ?>" href="leaderboard.php"><span>OVERALL</span></a><a class="<?= $tab==='ranked'?'active':'' ?>" href="leaderboard.php?tab=ranked"><span>♛ RANKED ELO</span></a></div>
<?php if($tab==='ranked'): ?>
<section class="panel leaderboard"><div class="leader-row leader-head ranked"><span>RANK</span><span>PLAYER</span><span>TIER</span><span>ELO</span><span>W / L / D</span><span>PEAK</span></div>
<?php if($note): ?><div class="empty-state"><?= e($note) ?></div><?php elseif(!$rows): ?><div class="empty-state">Belum ada pertandingan ranked. Mainkan mode RANKED untuk masuk papan peringkat!</div>
<?php else: foreach($rows as $i=>$r): $t=rating_tier((int)$r['elo']); ?>
<div class="leader-row ranked"><span class="rank">#<?= $i+1 ?></span><b><?= e($r['username']) ?></b><span><i class="tier-badge" style="--tc:<?= e($t['color']) ?>"><?= e($t['name']) ?></i></span><span class="rate"><?= (int)$r['elo'] ?></span><span><?= (int)$r['wins'] ?> / <?= (int)$r['losses'] ?> / <?= (int)$r['draws'] ?></span><span><?= (int)$r['peak_elo'] ?></span></div>
<?php endforeach; endif; ?></section>
<?php else: ?>
<section class="panel leaderboard"><div class="leader-row leader-head"><span>RANK</span><span>PLAYER</span><span>MATCHES</span><span>W / L</span><span>WIN RATE</span></div><?php if(!$rows): ?><div class="empty-state">Belum ada pemain di papan peringkat. Jadilah yang pertama!</div><?php else: foreach($rows as $i=>$r): ?><div class="leader-row"><span class="rank">#<?= $i+1 ?></span><b><?= e($r['username']) ?></b><span><?= (int)$r['total_matches'] ?></span><span><?= (int)$r['wins'] ?> / <?= (int)$r['losses'] ?></span><span class="rate"><?= (int)$r['win_rate'] ?>%</span></div><?php endforeach; endif; ?></section>
<?php endif; ?>
<?php include __DIR__.'/includes/footer.php'; ?>
