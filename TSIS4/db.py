from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


@dataclass
class LeaderboardRow:
    username: str
    score: int
    level_reached: int
    played_at: datetime


class DatabaseManager:
    def __init__(self) -> None:
        self.connection = None
        self.available = False

    def connect(self) -> bool:
        try:
            self.connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                cursor_factory=DictCursor,
            )
            self.connection.autocommit = True
            self.available = True
            self.init_schema()
            return True
        except Exception as exc:
            print(f"[DB] Connection failed: {exc}")
            self.available = False
            self.connection = None
            return False

    def init_schema(self) -> None:
        if not self.connection:
            return

        query = """
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
        """
        with self.connection.cursor() as cur:
            cur.execute(query)

    def get_or_create_player_id(self, username: str) -> Optional[int]:
        if not self.connection:
            return None

        with self.connection.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
            row = cur.fetchone()
            if row:
                return row["id"]

            cur.execute(
                "INSERT INTO players(username) VALUES (%s) RETURNING id;",
                (username,),
            )
            created = cur.fetchone()
            return created["id"] if created else None

    def save_game_session(self, username: str, score: int, level_reached: int) -> None:
        if not self.connection:
            return

        player_id = self.get_or_create_player_id(username)
        if player_id is None:
            return

        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game_sessions(player_id, score, level_reached)
                VALUES (%s, %s, %s);
                """,
                (player_id, score, level_reached),
            )

    def get_personal_best(self, username: str) -> int:
        if not self.connection:
            return 0

        with self.connection.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(gs.score), 0) AS best_score
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                WHERE p.username = %s;
                """,
                (username,),
            )
            row = cur.fetchone()
            return int(row["best_score"]) if row else 0

    def get_top_10(self) -> list[LeaderboardRow]:
        if not self.connection:
            return []

        with self.connection.cursor() as cur:
            cur.execute(
                """
                SELECT p.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC, gs.played_at ASC
                LIMIT 10;
                """
            )
            rows = cur.fetchall()

        return [
            LeaderboardRow(
                username=row["username"],
                score=row["score"],
                level_reached=row["level_reached"],
                played_at=row["played_at"],
            )
            for row in rows
        ]
