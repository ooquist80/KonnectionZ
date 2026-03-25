from pymysql.cursors import DictCursor
from datetime import datetime
from app.models.game import Game
from app.db.client import DatabaseClient


class GameRepository:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, user_id: int, gameset_id: int, start_time: datetime) -> Game:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO games (user_id, gameset_id, start_time)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, gameset_id, start_time)
                )
                game_id = cursor.lastrowid
            connection.commit()
        return Game(id=game_id, user_id=user_id, gameset_id=gameset_id, start_time=start_time)

    def get_by_id(self, game_id) -> Game | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, gameset_id, start_time, end_time, completed_wordsets
                    FROM games
                    WHERE id = %s
                    """, (game_id,)
                )
                game_row = cursor.fetchone()
                if game_row is None:
                    return None
                if game_row["completed_wordsets"] is not None:
                    completed_wordsets = [int(wordset_id) for wordset_id in game_row["completed_wordsets"].split(",")]
                else:
                    completed_wordsets = None
        return Game(id=game_row["id"], user_id=game_row["user_id"], gameset_id=game_row["gameset_id"],
                    start_time=game_row["start_time"], end_time=game_row["end_time"],
                    completed_wordsets=completed_wordsets)
