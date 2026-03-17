import datetime
from app.models.game import Game, GameNotFoundError
from app.db.client import DatabaseClient


class GameRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, date: datetime.datetime, name, wordsets: list[int]) -> GameRead:
        with self.database_client.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO games (date, name) VALUES (%s, %s)                        
                    """,
                    (date, name)
                )
                game_id = cursor.lastrowid
                data = [(game_id, wordset) for wordset in wordsets]
                cursor.executemany(
                    """
                    INSERT INTO games_wordsets (game_id, wordset_id) VALUES (%s, %s)
                    """,
                    data
                )
            connection.commit()
        return Game(id=game_id, date=date, name=name, wordsets=wordsets)

    def get_by_id(self, game_id: int) -> Game | None:
        with self.database_client.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, `date` FROM games WHERE id = %s
                    """,
                    (game_id,),
                )
                game_row = cursor.fetchone()

                if game_row is None:
                    return None
                cursor.execute(
                    """
                    SELECT wordset_id FROM games_wordsets WHERE game_id = %s
                    """,
                    (game_id,),
                )
                wordset_rows = cursor.fetchall()
                wordset_ids = []
                for wordset_row in wordset_rows:
                    wordset_ids.append(wordset_row["wordset_id"])

        return Game(id=game_row["id"], date=game_row["date"], name=game_row["name"], wordsets=wordset_ids)

    def delete(self, game_id: int) -> bool:
        with self.database_client.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM games WHERE id = %s
                    """,
                    (game_id,),
                )
                deleted = cursor.rowcount > 0

            if deleted:
                connection.commit()
                return deleted
            else:
                connection.rollback()
                raise GameNotFoundError(game_id)


