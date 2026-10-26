<?php
// Shared UI helpers (fighter cards etc.)
function fighter_card(array $c, int $i, string $href, string $cta = 'SELECT FIGHTER'): void {
    $st = $c['stats'] ?? [];
    $hex = ltrim($c['color'] ?? '#53e6d2', '#'); $lum = (0.299*hexdec(substr($hex,0,2)) + 0.587*hexdec(substr($hex,2,2)) + 0.114*hexdec(substr($hex,4,2))) / 255;
    $ct = $lum > 0.62 ? '#0a0d14' : '#ffffff';
    $labels = ['power' => 'POWER', 'speed' => 'SPEED', 'range' => 'RANGE', 'technique' => 'TECH'];
    ?>
    <article class="fcard reveal" style="--c:<?= e($c['color'] ?? '#53e6d2') ?>;--c2:<?= e($c['color2'] ?? '#ffffff') ?>;--t:<?= $ct ?>;--d:<?= $i * 60 ?>ms" data-tilt>
        <a class="fcard-art" href="<?= e($href) ?>" aria-label="<?= e($c['name']) ?>">
            <img src="assets/ui-previews/<?= e($c['slug']) ?>.png" alt="<?= e($c['name']) ?>" loading="lazy" width="640" height="800">
            <span class="fcard-no"><?= str_pad((string)($i + 1), 2, '0', STR_PAD_LEFT) ?></span>
            <span class="fcard-tag"><?= e(strtoupper($c['style'] ?? 'FIGHTER')) ?></span>
            <span class="fcard-shine"></span>
        </a>
        <div class="fcard-body">
            <h3><?= e(strtoupper($c['name'])) ?></h3>
            <p class="fcard-desc"><?= e($c['description']) ?></p>
            <div class="fcard-stats">
                <?php foreach ($labels as $k => $label): $v = (int)($st[$k] ?? 5); ?>
                <div><span><?= $label ?></span><i style="--v:<?= $v * 10 ?>%"></i><b><?= $v ?></b></div>
                <?php endforeach; ?>
            </div>
            <div class="fcard-ult"><span>ULTIMATE</span><b><?= e($c['ult'] ?? '') ?></b></div>
            <a class="button primary full" href="<?= e($href) ?>"><?= e($cta) ?> <span>↗</span></a>
        </div>
    </article>
    <?php
}

function fv_arenas(): array {
    return [
        ['id' => 'crimson-dojo',   'name' => 'CRIMSON DOJO',      'desc' => 'Dojo senja, gerbang torii, lentera dan kelopak sakura'],
        ['id' => 'frozen-citadel', 'name' => 'FROZEN CITADEL',    'desc' => 'Benteng es di bawah aurora, salju turun'],
        ['id' => 'volcano-forge',  'name' => 'VOLCANO FORGE',     'desc' => 'Lantai obsidian retak dan sungai lava'],
        ['id' => 'storm-peak',     'name' => 'STORM PEAK TEMPLE', 'desc' => 'Kuil puncak badai, petir dan hujan'],
        ['id' => 'digital-void',   'name' => 'DIGITAL VOID',      'desc' => 'Dunia data dengan portal raksasa'],
        ['id' => 'neon-rift',      'name' => 'NEON RIFT',         'desc' => 'Arena kota neon klasik'],
    ];
}
function fv_modes(): array {
    return [
        'versus'   => ['VS CPU', 'Lawan AI', '⚔'],
        'training' => ['TRAINING', 'Latihan combo', '◎'],
        'online'   => ['ONLINE', 'Quick match / room', '◈'],
        'ranked'   => ['RANKED', 'Naikkan ELO', '♛'],
    ];
}
