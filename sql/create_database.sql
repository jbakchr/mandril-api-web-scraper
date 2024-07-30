CREATE TABLE IF NOT EXISTS characters
(
  character_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  character_name TEXT NOT NULL,
  character_desc TEXT
);

CREATE TABLE IF NOT EXISTS episodes
(
  episode_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  season INT NOT NULL,
  episode INT NOT NULL
);

CREATE TABLE IF NOT EXISTS appearances
(
  appearance_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  character_id INT NOT NULL,
  episode_id INT NOT NULL,
  FOREIGN KEY (character_id) REFERENCES characters(character_id)
  FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
);