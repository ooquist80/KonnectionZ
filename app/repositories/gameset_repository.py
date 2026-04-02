import datetime

from pymysql.cursors import DictCursor

from app.models.gameset import GameSetRead, GameSetNotFoundError, GameSetInDb
from app.db.client import DatabaseClient
from app.repositories.wordset_repository import WordsetRepository


class GameSetRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client
        self.wordset_repository = WordsetRepository(database_client)

    def create(self, date: datetime.datetime, name, wordsets: list[int]) -> GameSetRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO gamesets (date, name)
                    VALUES (%s, %s)
                    """,
                    (date, name)
                )
                game_id = cursor.lastrowid
                data = [(game_id, wordset) for wordset in wordsets]
                cursor.executemany(
                    """
                    INSERT INTO gamesets_wordsets (gameset_id, wordset_id)
                    VALUES (%s, %s)
                    """,
                    data
                )
            connection.commit()
        return GameSetRead(id=game_id, date=date, name=name, wordsets=wordsets)

    def get_by_id(self, game_id: int) -> GameSetRead | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, name, `date`
                    FROM gamesets
                    WHERE id = %s
                    """,
                    (game_id,),
                )
                game_row = cursor.fetchone()

                if game_row is None:
                    return None
                cursor.execute(
                    """
                    SELECT wordset_id
                    FROM gamesets_wordsets
                    WHERE gameset_id = %s
                    """,
                    (game_id,),
                )
                wordset_rows = cursor.fetchall()
                wordsets = []
                for wordset_row in wordset_rows:
                    wordsets.append(self.wordset_repository.get_by_id(wordset_row["wordset_id"]))
        return GameSetRead(id=game_row["id"], date=game_row["date"], name=game_row["name"], wordsets=wordsets)

    def delete(self, game_id: int) -> bool:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    DELETE
                    FROM games
                    WHERE id = %s
                    """,
                    (game_id,),
                )
                deleted = cursor.rowcount > 0

            if deleted:
                connection.commit()
                return deleted
            else:
                connection.rollback()
                raise GameSetNotFoundError(game_id)
