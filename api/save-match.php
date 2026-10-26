<?php
require_once __DIR__.'/../includes/bootstrap.php';
header('Content-Type: application/json; charset=utf-8');
if($_SERVER['REQUEST_METHOD']!=='POST'){http_response_code(405);echo json_encode(['ok'=>false,'error'=>'Method not allowed']);exit;}
if(!current_user()){http_response_code(401);echo json_encode(['ok'=>false,'error'=>'Login required']);exit;}
$body=json_decode(file_get_contents('php://input'),true)??[];
if(!hash_equals($_SESSION['csrf']??'',(string)($body['csrf']??''))){http_response_code(419);echo json_encode(['ok'=>false,'error'=>'CSRF validation failed']);exit;}
$slug=preg_replace('/[^a-z0-9-]/','',strtolower((string)($body['character']??'')));$opp=preg_replace('/[^a-z0-9-]/','',strtolower((string)($body['opponent']??'')));$result=$body['result']??'';$mode=$body['mode']??'versus';
if(!in_array($result,['win','loss','draw'],true)||!in_array($mode,['versus','training'],true)){http_response_code(422);echo json_encode(['ok'=>false,'error'=>'Invalid match data']);exit;}
if($mode==='training'){echo json_encode(['ok'=>true,'saved'=>false,'message'=>'Training tidak disimpan sebagai ranked match']);exit;}
try{
 $pdo->beginTransaction();
 $q=$pdo->prepare('SELECT id FROM characters WHERE slug=? AND is_active=1');$q->execute([$slug]);$playerChar=$q->fetchColumn();
 $q->execute([$opp]);$opponentChar=$q->fetchColumn();
 if(!$playerChar||!$opponentChar)throw new RuntimeException('Character not found');
 $duration=max(0,min(999,(int)($body['duration']??0)));$damage=max(0,min(100000,(int)($body['damage']??0)));$hits=max(0,min(9999,(int)($body['hits']??0)));
 $q=$pdo->prepare('INSERT INTO matches(player_id,player_character_id,opponent_character_id,game_mode,difficulty,result,duration_seconds,damage_dealt,successful_hits) VALUES(?,?,?,"versus",?,?, ?,?,?)');
 $q->execute([current_user()['id'],$playerChar,$opponentChar,in_array($body['difficulty']??'normal',['easy','normal','hard'],true)?$body['difficulty']:'normal',$result,$duration,$damage,$hits]);
 $q=$pdo->prepare("INSERT INTO player_statistics(user_id,total_matches,wins,losses,draws,total_damage) VALUES(?,1,?,?,?,?) ON DUPLICATE KEY UPDATE total_matches=total_matches+1,wins=wins+VALUES(wins),losses=losses+VALUES(losses),draws=draws+VALUES(draws),total_damage=total_damage+VALUES(total_damage)");
 $q->execute([current_user()['id'],$result==='win'?1:0,$result==='loss'?1:0,$result==='draw'?1:0,$damage]);$pdo->commit();echo json_encode(['ok'=>true,'saved'=>true]);
}catch(Throwable $e){if($pdo->inTransaction())$pdo->rollBack();http_response_code(400);echo json_encode(['ok'=>false,'error'=>'Match could not be saved']);}
