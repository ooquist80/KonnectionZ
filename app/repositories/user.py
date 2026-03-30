from pymysql.cursors import DictCursor

from app.models.user import UserRead, UserWrite, UserRecord
from app.db.client import DatabaseClient


class UserRepository:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    def create(self, user_write : UserWrite, hashed_password: str) -> UserRead:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (email, username, password, scopes)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_write.email, user_write.username, hashed_password, user_write.scopes)
                )
                user_id = cursor.lastrowid
                scopes = user_write.scopes.split(",")
            connection.commit()
        return UserRead(id=user_id, email=user_write.email, username=user_write.username, scopes=scopes)

    def get_by_id(self, user_id: int) -> UserRead | None:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, email, username, scopes
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )
                user_row = cursor.fetchone()

        if user_row is None:
            return None
        scopes = user_row["scopes"].split(",")
        return UserRead(id=user_row["id"], email=user_row["email"], username=user_row["username"], scopes=scopes)

    def get_by_username(self, username) -> UserRecord:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, email, username, password, scopes
                    FROM users
                    WHERE username = %s
                    """,
                    (username,)
                )
                user_row = cursor.fetchone()

        if user_row is None:
            return None
        scopes = user_row["scopes"].split(",")
        return UserRecord(id=user_row["id"], email=user_row["email"], username=user_row["username"],
                          password=user_row["password"], scopes=scopes)
