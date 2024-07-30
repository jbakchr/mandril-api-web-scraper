DROP TABLE characters;
DROP TABLE episodes;
DROP TABLE appearances;

CREATE TABLE IF NOT EXISTS characters
(
  character_id INT NOT NULL UNIQUE PRIMARY KEY,
  character_name TEXT NOT NULL,
  character_desc TEXT
);

CREATE TABLE IF NOT EXISTS episodes
(
  episode_id INT NOT NULL UNIQUE PRIMARY KEY,
  season INT NOT NULL,
  episode INT NOT NULL
);

CREATE TABLE IF NOT EXISTS appearances
(
  appearance_id INT NOT NULL UNIQUE PRIMARY KEY,
  character_id INT NOT NULL,
  episode_id INT NOT NULL,
  FOREIGN KEY (character_id) REFERENCES characters(character_id)
  FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
);

INSERT INTO characters(character_id, character_name, character_desc)
VALUES 
  (1, "Abraham Mamrelund", "Starfucker"),
  (4, "Alfonso Trendy", "Glemmer ting"),
  (5, "Alfred Balle", "Pædagog");

INSERT INTO episodes(episode_id, season, episode)
VALUES 
  (41, 1, 41),
  (64, 2, 16);

INSERT INTO appearances(appearance_id, character_id, episode_id)
VALUES 
  (1, 1, 41),
  (5, 4, 41),
  (6, 5, 64);