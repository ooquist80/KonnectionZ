from pymysql.cursors import DictCursor

from app.db.client import DatabaseClient
from app.models.word import WordRead
from app.models.wordset import WordsetRead, WordsetRegisteredInGameError, WordsetNotFoundError, WordsetWrite


class WordsetRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, wordset_write: WordsetWrite) -> WordsetRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO wordsets (category, difficulty)
                    VALUES (%s, %s);
                    """,
                    (wordset_write.category, wordset_write.difficulty),
                )
                wordset_id = cursor.lastrowid
                cursor.executemany(
                    """
                    INSERT INTO words (`word`, `wordset_id`)
                    VALUES (%s, %s);
                    """,
                    [(word, wordset_id) for word in wordset_write.words],
                )
            connection.commit()

        return self.get_by_id(wordset_id)

    def get_by_id(self, wordset_id: int) -> WordsetRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT ws.id as wordset_id, ws.category, ws.difficulty, w.id as word_id, w.word 
                    FROM konnectionz.wordsets ws
                    JOIN konnectionz.words w ON ws.id = w.wordset_id 
                    WHERE ws.id = %s;
                    """, wordset_id
                )
                rows = cursor.fetchall()
                if not rows:
                    raise WordsetNotFoundError(f"Could not find wordset with id {wordset_id}")
                words = []
                for row in rows:
                    words.append(WordRead(id=row["word_id"], word=row["word"]))
                return WordsetRead(id=row["wordset_id"], category=row["category"],
                                   difficulty=row["difficulty"], words=words)

    def get_all(self) -> list[WordsetRead]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                # TODO replace with this query
                # """
                # SELECT ws.id as wordset_id, ws.category, ws.difficulty, w.id as word_id, w.word
                # FROM wordsets ws
                # JOIN words w ON ws.id = w.wordset_id;
                # """

                cursor.execute(
                    """
                    SELECT id,
                           category,
                           difficulty
                    FROM wordsets;
                    """
                )
                wordset_rows = cursor.fetchall()

                if not wordset_rows:
                    return []
                wordsets = []
                for wordset_row in wordset_rows:
                    cursor.execute(
                        """
                        SELECT id, wordset_id, word
                        FROM words
                        WHERE wordset_id = %s;
                        """, wordset_row["id"])
                    words = []
                    for word_row in cursor.fetchall():
                        words.append(WordRead(id=word_row["id"], word=word_row["word"]))
                    wordsets.append(WordsetRead(id=wordset_row["id"], category=wordset_row["category"],
                                                difficulty=wordset_row["difficulty"], words=words))
        return wordsets

    def delete(self, wordset_id: int) -> bool:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT game_id
                    FROM games_wordsets
                    WHERE wordset_id = %s;
                    """,
                    wordset_id
                )
                game_ids = cursor.fetchall()
                if game_ids:
                    raise WordsetRegisteredInGameError()
                cursor.execute(
                    """
                    DELETE
                    FROM words
                    WHERE wordset_id = %s;
                    """,
                    wordset_id
                )
                cursor.execute(
                    """
                    DELETE
                    FROM wordsets
                    WHERE id = %s;
                    """,
                    wordset_id
                )
                deleted = cursor.rowcount > 0

            if deleted:
                connection.commit()
            else:
                connection.rollback()
                raise WordsetNotFoundError()

        return deleted

    def difficulty_exists(self, difficulty_id: int) -> bool:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 1
                    FROM difficulties
                    WHERE id = %s;
                    """,
                    difficulty_id
                )
                row = cursor.fetchone()
        return row is not None

    def update(self, wordset_id: int, wordset_write: WordsetWrite) -> WordsetRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                # rowcount can be 0 when values are unchanged, so verify existence explicitly
                cursor.execute(
                    """
                    SELECT 1
                    FROM wordsets
                    WHERE id = %s;
                    """,
                    wordset_id
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    raise WordsetNotFoundError()

                cursor.execute(
                    """
                    UPDATE wordsets
                    SET category = %s, difficulty = %s
                    WHERE id = %s;
                    """,
                    (wordset_write.category, wordset_write.difficulty, wordset_id),
                )

                cursor.execute(
                    """
                    SELECT id, word
                    FROM words
                    WHERE wordset_id = %s
                    ORDER BY id;
                    """,
                    wordset_id
                )
                word_rows = cursor.fetchall()

                existing_count = len(word_rows)
                incoming_count = len(wordset_write.words)
                overlap_count = min(existing_count, incoming_count)

                if overlap_count > 0:
                    cursor.executemany(
                        """
                        UPDATE words
                        SET word = %s
                        WHERE id = %s;
                        """,
                        [
                            (wordset_write.words[index], word_rows[index]["id"])
                            for index in range(overlap_count)
                        ],
                    )

                if incoming_count > existing_count:
                    cursor.executemany(
                        """
                        INSERT INTO words (word, wordset_id)
                        VALUES (%s, %s);
                        """,
                        [(word, wordset_id) for word in wordset_write.words[existing_count:]],
                    )
                elif incoming_count < existing_count:
                    delete_word_ids = tuple(
                        word_row["id"] for word_row in word_rows[incoming_count:]
                    )
                    placeholders = ", ".join(["%s"] * len(delete_word_ids))
                    cursor.execute(
                        f"""
                        DELETE FROM words
                        WHERE id IN ({placeholders});
                        """,
                        delete_word_ids,
                    )

            connection.commit()

        return WordsetRead(
            id=wordset_id,
            category=wordset_write.category,
            difficulty=wordset_write.difficulty,
            words=wordset_write.words
        )
