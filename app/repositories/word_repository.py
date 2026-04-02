import datetime

from pymysql.cursors import DictCursor

from app.models.word import WordIndDB
from app.db.client import DatabaseClient
from app.models.wordset import WordsetRead


class WordRepository:
    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    def get_by_id(self, wordset_id: int) -> WordIndDB:
        with self.database_client.connect() as connection:
            with connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, word FROM word WHERE id = %s
                    """,
                    (wordset_id,)
                )
                word_row = cursor.fetchone()
            connection.commit()
        if word_row is None:
            return None
        return WordIndDB(id=word_row["id"], word=word_row["word"])