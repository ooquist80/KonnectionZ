from pymysql.cursors import DictCursor

from app.models.wordset import Wordset, WordsetRegisteredInGameError, WordsetNotFoundError
from app.db.client import DatabaseClient


class WordsetRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, *, category: str, difficulty: int, words: list[str]) -> Wordset:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO wordsets (category, difficulty)
                    VALUES (%s, %s);
                    """,
                    (category, difficulty),
                )
                wordset_id = cursor.lastrowid
                cursor.executemany(
                    """
                    INSERT INTO words (`word`, `wordset_id`)
                    VALUES (%s, %s);
                    """,
                    [(word, wordset_id) for word in words],
                )
            connection.commit()

        return self.get_by_id(wordset_id)

    def get_by_id(self, wordset_id: int) -> Wordset | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT w.id,
                           w.category,
                           w.difficulty
                    FROM wordsets w
                    WHERE w.id = %s
                    """,
                    (wordset_id,)
                )
                wordset_row = cursor.fetchone()

                if not wordset_row:
                    return None

                cursor.execute(
                    """
                    SELECT w.word
                    FROM words w
                    WHERE w.wordset_id = %s;
                    """,
                    (wordset_id,)
                )
                word_rows = cursor.fetchall()
                words = [word_row["word"] for word_row in word_rows]

                return Wordset(id=wordset_row["id"], category=wordset_row["category"],
                               difficulty=wordset_row["difficulty"], words=words)

    def get_all(self) -> list[Wordset]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
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
                wordset_ids = [row["id"] for row in wordset_rows]
                cursor.execute(
                    """
                    SELECT w.wordset_id, w.word
                    FROM words w
                    WHERE w.wordset_id IN %s;
                    """,
                    (wordset_ids,)
                )
                word_rows = cursor.fetchall()
                word_dict = {}
                for word_row in word_rows:
                    if word_row["wordset_id"] not in word_dict:
                        word_dict[word_row["wordset_id"]] = []
                    word_dict[word_row["wordset_id"]].append(word_row["word"])

                result = []
                for wordset_row in wordset_rows:
                    result.append(Wordset(
                        id=wordset_row["id"],
                        category=wordset_row["category"],
                        difficulty=wordset_row["difficulty"],
                        words=word_dict.get(wordset_row["id"], [])
                    )
                    )

        return result

    def delete(self, wordset_id: int) -> bool:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT game_id
                    FROM games_wordsets
                    WHERE wordset_id = %s;
                    """,
                    (wordset_id,)
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
                    (wordset_id,),
                )
                cursor.execute(
                    """
                    DELETE
                    FROM wordsets
                    WHERE id = %s;
                    """,
                    (wordset_id,),
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
                    (difficulty_id,),
                )
                row = cursor.fetchone()

        return row is not None
