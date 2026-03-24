from pymysql.cursors import DictCursor

from app.models.user import User
from app.db.client import DatabaseClient

class UserRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, email: str, username: str, password: str) -> User:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (email, username, password) VALUES (%s, %s, %s)
                    """,
                    (email, username, password)
                )
                user_id = cursor.lastrowid
            connection.commit()
        return User(id=user_id, email=email, username=username)

    def get_by_id(self, user_id: int) -> User | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, email, username FROM users WHERE id = %s
                    """,
                    (user_id,)
                )
                user_row = cursor.fetchone()

        if user_row is None:
            return None
        return User(id=user_row["id"], email=user_row["email"], username=user_row["username"])