<?php
// Versus key-art: two fighters clashing with energy, speed lines and lightning (pure CSS/SVG, lightly animated).
function fv_manifest_map(): array {
    static $map = null;
    if ($map === null) { $map = []; $m = json_decode(file_get_contents(__DIR__.'/../assets/character-pack/manifest.json'), true); foreach ($m['characters'] as $c) $map[$c['slug']] = $c; }
    return $map;
}
function vs_art(string $l, string $r, string $variant = 'hero'): void {
    $m = fv_manifest_map(); $a = $m[$l] ?? reset($m); $b = $m[$r] ?? end($m);
    ?>
    <div class="vsart vsart-<?= e($variant) ?>" style="--l:<?= e($a['color']) ?>;--l2:<?= e($a['color2']) ?>;--r:<?= e($b['color']) ?>;--r2:<?= e($b['color2']) ?>" aria-hidden="true">
        <div class="vs-bg"><i class="vs-burst"></i><i class="vs-swirl"></i><i class="vs-halftone"></i></div>
        <div class="vs-char vs-left"><i class="vs-aura"></i><img src="assets/ui-previews/cut/<?= e($a['slug']) ?>.png" alt=""></div>
        <div class="vs-char vs-right"><i class="vs-aura"></i><img src="assets/ui-previews/cut/<?= e($b['slug']) ?>.png" alt=""></div>
        <div class="vs-clash"></div>
        <svg class="vs-bolt" viewBox="0 0 120 600" preserveAspectRatio="none"><polyline class="b1" points="60,0 44,90 78,160 38,260 82,340 40,430 70,520 56,600"/><polyline class="b2" points="62,0 80,110 36,200 84,290 42,380 76,470 50,600"/></svg>
        <div class="vs-speed"></div>
        <div class="vs-emblem"><span>V</span><span>S</span></div>
        <?php for ($i = 0; $i < 16; $i++): ?><i class="vs-sp" style="--i:<?= $i ?>"></i><?php endfor; ?>
        <?php if ($variant === 'hero'): ?><div class="vs-names"><b><?= e(strtoupper($a['name'])) ?></b><em>VS</em><b><?= e(strtoupper($b['name'])) ?></b></div><?php endif; ?>
    </div>
    <?php
}
