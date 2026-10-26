<?php
require_once __DIR__.'/includes/bootstrap.php'; require_once __DIR__.'/includes/ui.php'; require_once __DIR__.'/includes/online.php';
$manifest=json_decode(file_get_contents(__DIR__.'/assets/character-pack/manifest.json'),true); $chars=$manifest['characters'];
$user=current_user(); $rating=$user?get_rating($pdo,(int)$user['id']):['elo'=>1000]; $tier=rating_tier((int)$rating['elo']);
$pageTitle='Choose Your Fighter'; $bodyClass='select-page'; $extraJs='js/select.js';
include __DIR__.'/includes/header.php'; ?>
<section class="select" id="select" data-logged="<?= $user?1:0 ?>" data-elo="<?= (int)$rating['elo'] ?>" data-tier="<?= e($tier['name']) ?>">
  <div class="select-bg" aria-hidden="true"><i class="sb-burst"></i><i class="sb-dots"></i><i class="sb-swirl"></i></div>
  <header class="select-head"><div><div class="eyebrow">CHARACTER SELECT</div><h1>CHOOSE YOUR <span>FIGHTER.</span></h1></div><div class="select-p1"><b>P1</b><span><?= $user?e(strtoupper($user['username'])):'GUEST' ?></span><?php if($user): ?><em style="--tc:<?= e($tier['color']) ?>"><?= e($tier['name']) ?> · <?= (int)$rating['elo'] ?></em><?php endif; ?></div></header>

  <div class="roster-grid" id="roster-grid" role="listbox" aria-label="Pilih karakter">
    <?php foreach($chars as $i=>$c): ?>
    <button type="button" class="tile<?= $i===5?' active':'' ?>" role="option" data-slug="<?= e($c['slug']) ?>" style="--c:<?= e($c['color']) ?>;--c2:<?= e($c['color2']) ?>;--i:<?= $i ?>">
      <img src="assets/ui-previews/icons/<?= e($c['slug']) ?>.png" alt="<?= e($c['name']) ?>" loading="lazy" width="128" height="128">
      <span class="tile-no"><?= str_pad((string)($i+1),2,'0',STR_PAD_LEFT) ?></span><span class="tile-name"><?= e(strtoupper($c['name'])) ?></span><span class="tile-ring"></span>
    </button>
    <?php endforeach; for($k=0;$k<4;$k++): ?>
    <div class="tile tile-locked" aria-hidden="true" style="--i:<?= 10+$k ?>"><span>?</span><small>SOON</small></div>
    <?php endfor; ?>
  </div>

  <div class="select-stage">
    <div class="splash" id="splash" style="--c:<?= e($chars[5]['color']) ?>;--c2:<?= e($chars[5]['color2']) ?>">
      <div class="splash-glow"></div><div class="splash-rays"></div>
      <div class="splash-tag" id="sp-no">06</div>
      <img id="sp-img" class="splash-img" src="assets/ui-previews/cut/<?= e($chars[5]['slug']) ?>.png" alt="">
      <div class="splash-name"><small id="sp-title"><?= e(strtoupper($chars[5]['style'])) ?></small><h2 id="sp-name"><?= e(strtoupper($chars[5]['name'])) ?></h2></div>
    </div>

    <aside class="select-panel">
      <p class="sp-desc" id="sp-desc"><?= e($chars[5]['description']) ?></p>
      <div class="fcard-stats big" id="sp-stats">
        <?php foreach(['power'=>'POWER','speed'=>'SPEED','range'=>'RANGE','technique'=>'TECH'] as $k=>$lab): ?>
        <div><span><?= $lab ?></span><i style="--v:<?= (int)$chars[5]['stats'][$k]*10 ?>%" data-k="<?= $k ?>"></i><b><?= (int)$chars[5]['stats'][$k] ?></b></div>
        <?php endforeach; ?>
      </div>
      <div class="sp-ult"><span>◆ ULTIMATE</span><b id="sp-ult"><?= e($chars[5]['ult']) ?></b></div>

      <div class="sel-label">MODE</div>
      <div class="mode-row" id="mode-row">
        <?php foreach(fv_modes() as $k=>[$n,$d,$ic]): ?><button type="button" class="mode<?= $k==='versus'?' active':'' ?>" data-mode="<?= $k ?>"><i><?= $ic ?></i><b><?= $n ?></b><small><?= $d ?></small></button><?php endforeach; ?>
      </div>
      <div class="mode-note" id="mode-note"></div>

      <div class="sel-label">ARENA <em id="arena-label"></em></div>
      <div class="arena-row" id="arena-row">
        <?php foreach(fv_arenas() as $i=>$a): ?><button type="button" class="arena<?= $i===0?' active':'' ?>" data-arena="<?= e($a['id']) ?>" data-name="<?= e($a['name']) ?>" data-desc="<?= e($a['desc']) ?>"><img src="assets/arenas/<?= e($a['id']) ?>.png" alt="<?= e($a['name']) ?>" loading="lazy"><span><?= e($a['name']) ?></span></button><?php endforeach; ?>
      </div>

      <button type="button" class="start-btn" id="start-btn"><span class="start-skill">SKILL <b id="start-ult"></b></span><span class="start-go">START <i>▶</i></span></button>
    </aside>
  </div>
</section>
<script type="application/json" id="roster-data"><?= json_encode($chars, JSON_UNESCAPED_UNICODE|JSON_HEX_TAG) ?></script>
<div class="wipe" id="wipe"><i></i><i></i><i></i></div>
<?php include __DIR__.'/includes/footer.php'; ?>
