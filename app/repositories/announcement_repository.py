from datetime import datetime

from pymysql.cursors import DictCursor

from app.db.client import DatabaseClient
from app.models.announcement import AnnouncementRead, AnnouncementWrite


class AnnouncementRepository:
    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    def create_announcement(self, announcement_write: AnnouncementWrite) -> AnnouncementRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                announced_at = datetime.now()
                cursor.execute(
                    """
                    INSERT INTO announcements (user_id, announced_at, content)
                    VALUES (%s, %s, %s)
                    """, (announcement_write.user_id, announced_at, announcement_write.content)
                )
                last_row_id = cursor.lastrowid
            connection.commit()
        return AnnouncementRead(id=last_row_id, user_id=announcement_write.user_id, announced_at=announced_at,
                                content=announcement_write.content)


    def get_all_announcements(self) -> list[AnnouncementRead]:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, announced_at, content
                    FROM announcements
                    """)
                announcement_rows = cursor.fetchall()
                announcements = []
                for announcement_row in announcement_rows:
                    announcements.append(AnnouncementRead(id=announcement_row["id"],
                                                          user_id=announcement_row["user_id"],
                                                          announced_at=announcement_row["announced_at"],
                                                          content=announcement_row["content"]))
                return announcements