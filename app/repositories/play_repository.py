from pymysql.cursors import DictCursor

from app.db.client import DatabaseClient
from app.models.play import PlayGameSet


class PlayRepository:
    def __init__(self, client: DatabaseClient):
        self.database_client: DatabaseClient = client

    def get_play_gameset(self, user_id: int) -> PlayGameSet:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT gs.id, gs.name, gs.daily, g.turn_count, g.start_time, g.end_time
                    FROM konnectionz.gamesets gs
                    LEFT JOIN konnectionz.games g ON g.gameset_id = gs.id 
                    WHERE g.user_id = %s OR g.user_id IS NULL;;
                    """, user_id)
                rows = cursor.fetchall()
            connection.commit()
        play_gamesets = []
        for row in rows:
            play_gamesets.append(PlayGameSet(id=row["id"],
                                             name=row["name"],
                                             daily=row["daily"],
                                             turn_count=row["turn_count"],
                                             start_time=row["start_time"],
                                             end_time=row["end_time"]))
        return play_gamesets



