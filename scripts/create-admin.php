<?php
// Run locally from terminal: php scripts/create-admin.php username email password
if(PHP_SAPI!=='cli'){http_response_code(403);exit("CLI only.\n");}
require __DIR__.'/../config/database.php';
if($argc<4){fwrite(STDERR,"Usage: php scripts/create-admin.php username email password\n");exit(1);}
[$script,$username,$email,$password]=$argv;
if(!preg_match('/^[A-Za-z0-9_]{3,24}$/',$username)||!filter_var($email,FILTER_VALIDATE_EMAIL)||strlen($password)<12){fwrite(STDERR,"Username/email invalid; admin password must be at least 12 characters.\n");exit(1);}
try{$pdo->beginTransaction();$q=$pdo->prepare("INSERT INTO users(username,email,password_hash,role,status) VALUES(?,?,?,'admin','active')");$q->execute([$username,$email,password_hash($password,PASSWORD_DEFAULT)]);$id=$pdo->lastInsertId();$pdo->prepare('INSERT INTO player_profiles(user_id,display_name) VALUES(?,?)')->execute([$id,$username]);$pdo->prepare('INSERT INTO player_statistics(user_id) VALUES(?)')->execute([$id]);$pdo->commit();echo "Admin account created.\n";}catch(Throwable $e){if($pdo->inTransaction())$pdo->rollBack();fwrite(STDERR,"Could not create admin. Check duplicate username/email and database.\n");exit(1);}
