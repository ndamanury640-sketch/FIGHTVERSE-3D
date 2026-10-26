<?php
declare(strict_types=1);
if (session_status() !== PHP_SESSION_ACTIVE) {
  ini_set('session.use_strict_mode', '1');
  session_set_cookie_params(['httponly'=>true,'samesite'=>'Lax','secure'=>!empty($_SERVER['HTTPS'])]);
  session_start();
}
require_once __DIR__ . '/../config/database.php';
function e($v): string { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }
function csrf_token(): string { if (empty($_SESSION['csrf'])) $_SESSION['csrf']=bin2hex(random_bytes(32)); return $_SESSION['csrf']; }
function csrf_check(): void { if ($_SERVER['REQUEST_METHOD']==='POST' && !hash_equals($_SESSION['csrf'] ?? '', $_POST['csrf'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '')) { http_response_code(419); exit('CSRF token tidak valid. Muat ulang halaman.'); } }
function current_user(): ?array { return $_SESSION['user'] ?? null; }
function require_login(): void { if (!current_user()) { header('Location: login.php'); exit; } }
function require_admin(): void { require_login(); if (current_user()['role'] !== 'admin') { http_response_code(403); exit('Akses ditolak.'); } }
