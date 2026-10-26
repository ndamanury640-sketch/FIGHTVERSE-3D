<?php require_once __DIR__.'/includes/bootstrap.php'; require_once __DIR__.'/includes/ui.php'; require_once __DIR__.'/includes/vsart.php';
$pageTitle='FIGHTVERSE 3D Arena'; $chars=json_decode(file_get_contents(__DIR__.'/assets/character-pack/manifest.json'),true)['characters'];
include __DIR__.'/includes/header.php'; ?>
<section class="hero hero-vs">
  <?php vs_art('cyber-x','inferno','hero'); ?>
  <div class="hero-copy">
    <div class="eyebrow"><span class="pulse"></span> REALTIME ANIME 3D COMBAT</div>
    <h1 class="glitch">ENTER THE<br><span>FIGHTVERSE.</span></h1>
    <p>Pilih petarungmu, kuasai combo, lalu lepaskan ultimate sinematik di 6 arena berbeda. Main lawan CPU, online bersama teman, atau naikkan peringkat di mode ranked, langsung di browser, termasuk di HP.</p>
    <div class="hero-actions">
      <a class="button primary" href="characters.php">PLAY NOW <span>↗</span></a>
      <a class="button ghost" href="#roster">EXPLORE FIGHTERS</a>
    </div>
    <div class="hero-meta">
      <div><strong data-count="10">10</strong><small>FIGHTERS</small></div>
      <div><strong data-count="6">6</strong><small>ARENAS</small></div>
      <div><strong>ONLINE</strong><small>RANKED ELO</small></div>
    </div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">
  <?php for($k=0;$k<2;$k++): foreach(['10 UNIQUE FIGHTERS','TOON SHADING','ULTIMATE CUT-INS','BLOOM VFX','COMBO CANCELS','NEON RIFT ARENA','RANKED LEADERBOARD'] as $t): ?><span><?= $t ?></span><em>◆</em><?php endforeach; endfor; ?>
</div></div>

<section class="section">
  <div class="section-heading reveal"><div><div class="eyebrow">WHY FIGHTVERSE</div><h2>BUILT FOR <span class="grad">STYLE.</span></h2></div></div>
  <div class="feature-grid">
    <div class="feature reveal" style="--c:#ff4b6b"><div class="feature-ico">⚔</div><h3>Combo &amp; Cancel</h3><p>Rangkai jab, cross, dan tendangan, lalu cancel ke heavy atau special saat serangan mengenai lawan.</p></div>
    <div class="feature reveal" style="--c:#53e6d2;--d:80ms"><div class="feature-ico">✦</div><h3>Ultimate Sinematik</h3><p>Layar membeku, banner nama skill, kamera mengitari karakter, lalu barrage tebasan dan finisher.</p></div>
    <div class="feature reveal" style="--c:#a56bff;--d:160ms"><div class="feature-ico">◈</div><h3>6 Arena &amp; HP</h3><p>Dojo sakura, benteng es, gunung lava, kuil badai, dunia digital. Kontrol sentuh joystick siap dipakai di HP.</p></div>
    <div class="feature reveal" style="--c:#ffb44a;--d:240ms"><div class="feature-ico">♛</div><h3>Online &amp; Ranked</h3><p>Lawan pemain lain lewat room code atau antrean ranked berbasis ELO, lengkap dengan tier Bronze sampai Master.</p></div>
  </div>
</section>

<section class="section" id="roster">
  <div class="section-heading reveal"><div><div class="eyebrow">CHOOSE YOUR DESTINY</div><h2>THE <span class="grad">FIGHTERS</span></h2></div><a class="text-link" href="characters.php">CHARACTER SELECT ↗</a></div>
  <div class="fcard-grid">
    <?php foreach($chars as $i=>$c) fighter_card($c,$i,current_user()?'game.php?character='.$c['slug']:'register.php','PLAY AS '.strtoupper($c['name'])); ?>
  </div>
</section>

<section class="section controls-section">
  <div class="section-heading reveal"><div><div class="eyebrow">QUICK START</div><h2>CONTROLS</h2></div></div>
  <div class="keys reveal">
    <div><kbd>W A S D</kbd><span>Bergerak</span></div><div><kbd>SPACE</kbd><span>Lompat</span></div><div><kbd>J</kbd><span>Light (tekan beruntun = combo)</span></div>
    <div><kbd>K</kbd><span>Heavy</span></div><div><kbd>L</kbd><span>Special</span></div><div><kbd>U</kbd><span>Ultimate</span></div><div><kbd>I</kbd><span>Block</span></div><div><kbd>SHIFT</kbd><span>Dash</span></div>
  </div>
</section>

<section class="cta-strip reveal"><div><div class="eyebrow">YOUR LEGEND STARTS HERE</div><h2>READY TO THROW DOWN?</h2></div><a class="button primary" href="<?= current_user()?'characters.php':'register.php' ?>">ENTER THE ARENA ↗</a></section>
<?php include __DIR__.'/includes/footer.php'; ?>
