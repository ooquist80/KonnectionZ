from datetime import datetime

from pymysql.cursors import DictCursor

from app.models.gameset import GameSetRead, GameSetNotFoundError
from app.db.client import DatabaseClient
from app.repositories.wordset_repository import WordsetRepository


class GameSetRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client
        self.wordset_repository = WordsetRepository(database_client)

    def create(self, date: datetime, daily_date: datetime | None, name: str, wordset_ids: list[int]) -> GameSetRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO gamesets (date, daily_date, name)
                    VALUES (%s, %s, %s)
                    """,
                    (date, daily_date, name)
                )
                game_id = cursor.lastrowid
                data = [(game_id, wordset_id) for wordset_id in wordset_ids]
                cursor.executemany(
                    """
                    INSERT INTO gamesets_wordsets (gameset_id, wordset_id)
                    VALUES (%s, %s)
                    """,
                    data
                )
                wordsets = []
                for wordset_id in wordset_ids:
                    wordsets.append(self.wordset_repository.get_by_id(wordset_id))
            connection.commit()
        return GameSetRead(id=game_id, date=date, daily_date=daily_date, name=name, wordsets=wordsets)

    def get_by_id(self, gameset_id: int) -> GameSetRead | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, daily_date, name, `date`
                    FROM gamesets
                    WHERE id = %s
                    """,
                    gameset_id
                )
                gameset_row = cursor.fetchone()

                if gameset_row is None:
                    return None
                cursor.execute(
                    """
                    SELECT wordset_id
                    FROM gamesets_wordsets
                    WHERE gameset_id = %s
                    """,
                    gameset_id
                )
                wordset_rows = cursor.fetchall()
                wordsets = []
                for wordset_row in wordset_rows:
                    wordsets.append(self.wordset_repository.get_by_id(wordset_row["wordset_id"]))
        return GameSetRead(id=gameset_row["id"], daily_date=gameset_row["daily_date"], date=gameset_row["date"], name=gameset_row["name"], wordsets=wordsets)

    def get_all(self) -> list[GameSetRead]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute("""
                SELECT id, daily_date, name, date
                FROM gamesets
                """)
                gameset_rows = cursor.fetchall()
                gamesets = []
                for gameset_row in gameset_rows:
                    cursor.execute(
                        """
                        SELECT wordset_id
                        FROM gamesets_wordsets
                        WHERE gameset_id = %s
                        """,
                        gameset_row["id"]
                    )
                    wordset_id_rows = cursor.fetchall()
                    wordsets = []
                    for wordset_id_row in wordset_id_rows:
                        wordsets.append(self.wordset_repository.get_by_id(wordset_id_row["wordset_id"]))
                    gamesets.append(GameSetRead(id=gameset_row["id"],
                                                daily_date=gameset_row["daily_date"],
                                                name=gameset_row["name"],
                                                date=gameset_row["date"],
                                                wordsets=wordsets))
            connection.commit()
        return gamesets




    def delete(self, gameset_id: int) -> bool:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    DELETE
                    FROM gamesets
                    WHERE id = %s
                    """,
                    gameset_id
                )
                deleted = cursor.rowcount > 0

            if deleted:
                connection.commit()
                return deleted
            else:
                connection.rollback()
                raise GameSetNotFoundError(gameset_id)

    def get_latest_daily_gameset_id(self) -> int:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute("""
                    SELECT id
                    FROM gamesets
                    WHERE daily_date IS NOT NULL
                    ORDER BY daily_date DESC
                    LIMIT 1
                    """)
                gameset_row = cursor.fetchone()
            connection.commit()
        return gameset_row["id"]