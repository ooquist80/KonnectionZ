from datetime import datetime

from pymysql.cursors import DictCursor

from app.db.client import DatabaseClient
from app.models.comment import CommentRead, CommentWrite
from app.models.user import UserRead


class CommentRepository:
    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    def get_by_announcement_id(self, announcement_id):
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT c.id, c.announcement_id, u.username, c.content, c.commented_at
                    FROM comments c 
                    JOIN users u ON c.user_id = u.id                    
                    WHERE c.announcement_id = %s
                    ORDER BY c.commented_at ASC;
                     """, announcement_id
                )
                rows = cursor.fetchall()
                comments = []
            for row in rows:
                comments.append(CommentRead(id=row["id"],
                                            announcement_id=row["announcement_id"],
                                            user_name=row["username"],
                                            commented_at=row["commented_at"],
                                            content=row["content"]))
            connection.commit()
        return comments

    def create_comment(self, user: UserRead, comment_write: CommentWrite) -> CommentRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                current_datetime = datetime.now()
                cursor.execute(
                    """
                    INSERT INTO comments (announcement_id, user_id, commented_at, content)
                    VALUES (%s, %s, %s, %s)
                    """, (comment_write.announcement_id, user.id, current_datetime, comment_write.content)
                )
                last_comment_id = cursor.lastrowid
            connection.commit()
        return CommentRead(id=last_comment_id,
                           announcement_id=comment_write.announcement_id,
                           user_name=user.username,
                           commented_at=current_datetime,
                           content=comment_write.content)

