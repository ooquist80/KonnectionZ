from datetime import datetime
from venv import logger

from pymysql.cursors import DictCursor

from app.db.client import DatabaseClient
from app.models.game import GameRead
from app.models.gameset import GameSetNotFoundError
from app.repositories.gameset_repository import GameSetRepository


class GameRepository:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client
        self.gameset_repository = GameSetRepository(database_client)

    def create(self, gameset_id: int, user_id: int, dailygame) -> GameRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                gameset = self.gameset_repository.get_by_id(gameset_id)
                if gameset is None:
                    raise GameSetNotFoundError()
                start_time = datetime.now()
                cursor.execute(
                    """
                    INSERT INTO games (user_id, gameset_id, start_time, dailygame)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, gameset_id, start_time, dailygame)
                )
                game_id = cursor.lastrowid
            connection.commit()

        return GameRead(id=game_id, user_id=user_id, dailygame=dailygame, gameset=gameset,
                        start_time=start_time)

    def get_by_id(self, game_id) -> GameRead | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, gameset_id, dailygame, miss_count, start_time, end_time
                    FROM games
                    WHERE id = %s
                    """, game_id
                )
                game_row = cursor.fetchone()
                if game_row is None:
                    return None
                cursor.execute(
                    """
                    SELECT wordset_id 
                    FROM games_wordsets gw
                    WHERE game_id = %s
                    ORDER BY gw.id;
                    """, (game_row["id"],)
                )
                wordset_rows = cursor.fetchall()
                completed_wordset_ids = []
                for wordset_row in wordset_rows:
                    completed_wordset_ids.append(wordset_row["wordset_id"])
                gameset = self.gameset_repository.get_by_id(game_row["gameset_id"])
                if gameset is None:
                    raise GameSetNotFoundError()
        return GameRead(id=game_id,
                          user_id=game_row["user_id"],
                          gameset=gameset,
                          dailygame=game_row["dailygame"],
                          miss_count=game_row["miss_count"],
                          start_time=game_row["start_time"],
                          end_time=game_row["end_time"],
                          completed_wordsets=completed_wordset_ids)

    def get_by_user_id(self, user_id: int) -> list[GameRead]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, gameset_id, dailygame, miss_count, start_time, end_time
                    FROM games
                    WHERE user_id = %s
                    """, user_id
                )
                game_rows = cursor.fetchall()
                games = []
                for game_row in game_rows:
                    cursor.execute(
                        """
                        SELECT wordset_id 
                        FROM games_wordsets 
                        WHERE game_id = %s
                        """, (game_row["id"],)
                    )
                    wordset_rows = cursor.fetchall()
                    gameset = self.gameset_repository.get_by_id(game_row["gameset_id"])
                    if gameset is None:
                        logger.warning(f"No gameset found for game_id {game_row['id']}")
                    else:
                        completed_wordset_ids = []
                        for wordset_row in wordset_rows:
                            completed_wordset_ids.append(wordset_row["wordset_id"])
                        games.append(GameRead(id=game_row["id"],
                                              user_id=game_row["user_id"],
                                              gameset=gameset,
                                              dailygame=game_row["dailygame"],
                                              miss_count=game_row["miss_count"],
                                              start_time=game_row["start_time"],
                                              end_time=game_row["end_time"],
                                              completed_wordsets=completed_wordset_ids))
        return games


    def get_all(self) -> list[GameRead]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, gameset_id, dailygame, miss_count, start_time, end_time
                    FROM games
                    """
                )
                game_rows = cursor.fetchall()
                games = []
                for game_row in game_rows:
                    cursor.execute(
                        """
                        SELECT wordset_id 
                        FROM games_wordsets 
                        WHERE game_id = %s
                        """, (game_row["id"],)
                    )
                    wordset_rows = cursor.fetchall()
                    gameset = self.gameset_repository.get_by_id(game_row["gameset_id"])
                    if gameset is None:
                        logger.warning(f"No gameset found for game_id {game_row['id']}")
                    else:
                        completed_wordset_ids = []
                        for wordset_row in wordset_rows:
                            completed_wordset_ids.append(wordset_row["wordset_id"])
                        games.append(GameRead(id=game_row["id"],
                                            user_id=game_row["user_id"],
                                            gameset=gameset,
                                            dailygame=game_row["dailygame"],
                                            miss_count=game_row["miss_count"],
                                            start_time=game_row["start_time"],
                                            end_time=game_row["end_time"],
                                            completed_wordsets=completed_wordset_ids))
        return games


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

    def increment_miss_count(self, game_id) -> None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE games
                    SET miss_count = miss_count + 1
                    WHERE id = %s
                    """,
                    game_id
                )
            connection.commit()
