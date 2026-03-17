from pathlib import Path

from pymysql import Connection, connect
from pymysql.cursors import DictCursor

from app.core.config import Settings


class DatabaseClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.schema_path = Path(__file__).with_name("schema.sql")

    def connect(self) -> Connection:
        return self._connect(database=self.settings.database_name)

    def initialize(self) -> None:
        with self._connect(database=None) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.settings.database_name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            connection.commit()

        with self.connect() as connection:
            with connection.cursor() as cursor:
                for statement in self._load_schema_statements():
                    cursor.execute(statement)
            connection.commit()

    def _connect(self, *, database: str | None) -> Connection:
        return connect(
            host=self.settings.database_host,
            port=self.settings.database_port,
            user=self.settings.database_user,
            password=self.settings.database_password,
            database=database,
            cursorclass=DictCursor,
            autocommit=False,
        )

    def _load_schema_statements(self) -> list[str]:
        schema_sql = self.schema_path.read_text(encoding="utf-8")

        statements: list[str] = []
        current_lines: list[str] = []

        for line in schema_sql.splitlines():
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("--"):
                continue

            current_lines.append(line)
            if stripped_line.endswith(";"):
                statements.append("\n".join(current_lines))
                current_lines = []

        if current_lines:
            statements.append("\n".join(current_lines))

        return statements

