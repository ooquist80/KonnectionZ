from pymysql.cursors import DictCursor
from datetime import datetime
from app.models.game import GameRead, GameWrite, GameRecord
from app.models.wordset import WordsetRead
from app.db.client import DatabaseClient


class GameRepository:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, game_write : GameWrite) -> GameRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO games (user_id, gameset_id, start_time)
                    VALUES (%s, %s, %s)
                    """,
                    (game_write.user_id, game_write.gameset_id, game_write.start_time)
                )
                game_id = cursor.lastrowid
            connection.commit()
        return GameRead(id=game_id, user_id=game_write.user_id, gameset_id=game_write.gameset_id,
                        start_time=game_write.start_time)

    def get_by_id(self, game_id) -> GameRecord | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, gameset_id, start_time, end_time
                    FROM games
                    WHERE id = %s
                    """, (game_id,)
                )
                game_row = cursor.fetchone()
                if game_row is None:
                    return None
                cursor.execute(
                    """
                    SELECT wordset_id 
                    FROM games_wordsets 
                    WHERE game_id = %s
                    """, (game_row["id"],)
                )
                wordset_rows = cursor.fetchall()
                completed_wordset_ids = []
                for wordset_row in wordset_rows:
                    completed_wordset_ids.append(wordset_row["wordset_id"])
                completed_wordset_ids = list(set(completed_wordset_ids))
        return GameRecord(id=game_id,
                          user_id=game_row["user_id"],
                          gameset_id=game_row["gameset_id"],
                          start_time=game_row["start_time"],
                          end_time=game_row["end_time"],
                          completed_wordset_ids=completed_wordset_ids)


    def get_all(self) -> list[GameRecord]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, gameset_id, start_time, end_time
                    FROM games
                    """,
                )
                game_rows = cursor.fetchall()
                game_records = []
                for game_row in game_rows:
                    cursor.execute(
                        """
                        SELECT wordset_id 
                        FROM games_wordsets 
                        WHERE game_id = %s
                        """, (game_row["id"],)
                    )
                    wordset_rows = cursor.fetchall()
                    completed_wordset_ids = []
                    for wordset_row in wordset_rows:
                        completed_wordset_ids.append(wordset_row["wordset_id"])
                    completed_wordset_ids = list(set(completed_wordset_ids))
                    game_records.append(GameRecord(id=game_row["id"],
                                            user_id=game_row["user_id"],
                                            gameset_id=game_row["gameset_id"],
                                            start_time=game_row["start_time"],
                                            end_time=game_row["end_time"],
                                            completed_wordset_ids=completed_wordset_ids))
        return game_records


    def add_completed_wordset(self, game_id, wordset_id) -> None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO games_wordsets (game_id, wordset_id)
                    VALUES (%s, %s)
                    """,
                    (game_id, wordset_id)
                )
            connection.commit()

    def add_game_end_time(self, game_id, end_time):
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE games
                    SET end_time = %s
                    WHERE id = %s
                    """,
                    (end_time, game_id)
                )
            connection.commit()





