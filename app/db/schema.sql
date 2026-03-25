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

CREATE TABLE IF NOT EXISTS gamesets (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `date` VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS gamesets_wordsets (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	gameset_id INT NOT NULL,
	wordset_id INT NOT NULL,
    KEY gamesets_wordsets_gamesets_FK (gameset_id),
    KEY gamesets_wordsets_wordsets_FK (wordset_id),
	CONSTRAINT gamesets_wordsets_gamesets_FK FOREIGN KEY (gameset_id) REFERENCES konnectionz.gamesets(id),
	CONSTRAINT gamesets_wordsets_wordsets_FK FOREIGN KEY (wordset_id) REFERENCES konnectionz.wordsets(id)
);

CREATE TABLE IF NOT EXISTS games (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `gameset_id` INT NOT NULL,
    `start_time` DATETIME NOT NULL,
    `end_time` DATETIME,
    `completed_wordsets` VARCHAR(255),
    KEY `games_gamesets_FK` (`gameset_id`),
    KEY `games_users_FK` (`user_id`),
    CONSTRAINT `games_gamesets_FK` FOREIGN KEY (`gameset_id`) REFERENCES `gamesets` (`id`),
    CONSTRAINT `games_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) NOT NULL,
    `username` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL
);