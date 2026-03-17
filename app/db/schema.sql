CREATE TABLE IF NOT EXISTS difficulties (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL
);

INSERT INTO difficulties (id, `name`)
VALUES
    (1, 'Easy'),
    (2, 'Medium'),
    (3, 'Hard')
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

CREATE TABLE IF NOT EXISTS wordsets (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `category` VARCHAR(100) NOT NULL,
    `difficulty` INT NOT NULL,
    KEY `wordsets_difficulties_FK` (`difficulty`),
    CONSTRAINT `wordsets_difficulties_FK` FOREIGN KEY (`difficulty`) REFERENCES `difficulties` (`id`)
);

CREATE TABLE IF NOT EXISTS words (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `word` VARCHAR(255) NOT NULL,
    `wordset_id` INT NOT NULL,
    KEY `words_wordsets_FK` (`wordset_id`),
    CONSTRAINT `words_wordsets_FK` FOREIGN KEY (`wordset_id`) REFERENCES `wordsets` (`id`)
);

CREATE TABLE IF NOT EXISTS games (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `date` VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS konnectionz.games (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	`date` DATE NOT NULL,
	CONSTRAINT games_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS konnectionz.games_wordsets (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	game_id INT NOT NULL,
	wordset_id INT NOT NULL,
    KEY games_wordsets_games_FK (game_id),
    KEY games_wordsets_wordsets_FK (wordset_id),
	CONSTRAINT games_wordsets_games_FK FOREIGN KEY (game_id) REFERENCES konnectionz.games(id),
	CONSTRAINT games_wordsets_wordsets_FK FOREIGN KEY (wordset_id) REFERENCES konnectionz.wordsets(id)
);
