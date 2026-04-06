from pymysql.cursors import DictCursor

from app.db.client import DatabaseClient
from app.models.play import PlayGameSet


class PlayRepository:
    def __init__(self, client: DatabaseClient):
        self.database_client: DatabaseClient = client

    def get_play_gamesets_by_user_id(self, user_id: int, daily_game_id: int) -> list[PlayGameSet]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT gs.id, gs.name, gs.daily_date, g.user_id, g.miss_count, g.start_time, g.end_time
                    FROM konnectionz.gamesets gs
                    LEFT JOIN konnectionz.games g 
                    ON g.gameset_id = gs.id AND g.user_id = %s;
                    """, user_id)
                rows = cursor.fetchall()
            connection.commit()
        play_gamesets= []
        for row in rows:
            if row["id"] != daily_game_id:
                play_gamesets.append(PlayGameSet(id=row["id"],
                                                 name=row["name"],
                                                 daily_date=row["daily_date"],
                                                 miss_count=row["miss_count"],
                                                 start_time=row["start_time"],
                                                 end_time=row["end_time"]))
        return play_gamesets

    def get_play_gameset_by_id(self, user_id, daily_game_id):
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT gs.id, gs.name, gs.daily_date, g.user_id, g.miss_count, g.start_time, g.end_time
                    FROM konnectionz.gamesets gs
                    LEFT JOIN konnectionz.games g 
                    ON g.gameset_id = gs.id AND g.user_id = %s
                    WHERE gs.id = %s;
                    """, (user_id, daily_game_id)
                )
                row = cursor.fetchone()
            connection.commit()

        return PlayGameSet(id=row["id"],
                           name=row["name"],
                           daily_date=row["daily_date"],
                           miss_count=row["miss_count"],
                           start_time=row["start_time"],
                           end_time=row["end_time"])



