from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

DB_PATH = os.getenv("TRADE_LOG_DB", "analysis/trade_logs.db")


class TradeLogEntry(BaseModel):
    id: int
    timestamp: str
    symbol: str
    side: str
    quantity: int
    price: float
    indicators: Dict[str, Any]
    reasoning: str
    accountType: str


class TradeLogger:
    def __init__(self) -> None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    indicators TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    execution_metadata TEXT
                );
                """
            )

    def log_trade(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        indicators: Dict[str, Any],
        reasoning: str,
        account_type: str,
        execution_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        timestamp = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO trade_logs
                (timestamp, symbol, side, quantity, price, indicators, reasoning, account_type, execution_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    symbol,
                    side,
                    quantity,
                    price,
                    json.dumps(indicators, ensure_ascii=False),
                    reasoning,
                    account_type,
                    json.dumps(execution_metadata or {}, ensure_ascii=False),
                ),
            )

    def fetch_logs(self) -> List[TradeLogEntry]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, timestamp, symbol, side, quantity, price, indicators, reasoning, account_type
                FROM trade_logs
                ORDER BY timestamp DESC
                """
            )
            rows = cursor.fetchall()
        return [
            TradeLogEntry(
                id=row[0],
                timestamp=row[1],
                symbol=row[2],
                side=row[3],
                quantity=row[4],
                price=row[5],
                indicators=json.loads(row[6]),
                reasoning=row[7],
                accountType=row[8],
            )
            for row in rows
        ]
