-- Run this ONCE on an existing database to enable Online / Ranked (fresh installs: schema.sql already includes it).
USE fightverse_db;
ALTER TABLE matches MODIFY game_mode ENUM('versus','training','online','ranked') NOT NULL DEFAULT 'versus';
CREATE TABLE IF NOT EXISTS player_ratings (
 user_id BIGINT UNSIGNED PRIMARY KEY,
 elo SMALLINT UNSIGNED NOT NULL DEFAULT 1000,
 peak_elo SMALLINT UNSIGNED NOT NULL DEFAULT 1000,
 games INT UNSIGNED NOT NULL DEFAULT 0,
 wins INT UNSIGNED NOT NULL DEFAULT 0,
 losses INT UNSIGNED NOT NULL DEFAULT 0,
 draws INT UNSIGNED NOT NULL DEFAULT 0,
 updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 INDEX idx_rating_elo(elo),
 CONSTRAINT fk_rating_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS online_matches (
 match_id VARCHAR(32) PRIMARY KEY,
 ranked TINYINT(1) NOT NULL DEFAULT 0,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
