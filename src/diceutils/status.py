from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union

import sqlite3


class StatusManager:
    def __init__(
        self,
        db_path: Union[str, Path] = ":memory:",
    ):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS status (
                session_id TEXT,
                name TEXT,
                status TEXT,
                CONSTRAINT unique_session_name UNIQUE (session_id, name)
            );
            """
        )
        self.conn.commit()

    def _insert(self, cursor: sqlite3.Cursor, data: Tuple[str, str, str]):
        cursor.execute(
            """
            INSERT INTO status (session_id, name, status) 
            VALUES (?, ?, ?)
            ON CONFLICT (session_id, name) DO UPDATE SET status = excluded.status;
            """,
            data,
        )

    def saveall(self, data: Dict[str, Dict[str, str]]) -> None:
        cursor = self.conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        for session_id in data.keys():
            for name, status in data[session_id].items():
                self._insert(cursor, (session_id, name, status))

        self.conn.commit()

    def save(self, session_id: str, name: str, *, status: Optional[str] = None) -> None:
        cursor = self.conn.cursor()
        self._insert(cursor, (session_id, name, str(status)))
        self.conn.commit()

    def load(self) -> Dict[str, Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT session_id, name, status FROM status")
        result = cursor.fetchall()
        datas = {}
        for session_id, name, status in result:
            if session_id not in datas:
                datas[session_id] = {}
            try:
                datas[session_id][name] = eval(status)
            except:
                datas[session_id][name] = status
        return datas

    def close(self):
        self.conn.close()


class Status:
    status_manager: StatusManager

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.status_manager = StatusManager(f"dicergirl.db")
        self.load()

    def __repr__(self) -> str:
        return f"Status(db='dicergirl.db')"

    def saveall(self) -> None:
        self.status_manager.saveall(self.data)

    def rescue(self) -> None:
        self.saveall()
        self.status_manager.close()

    def load(self) -> None:
        self.data = self.status_manager.load()

    def set(self, session_id: str, name: str, status: Any) -> None:
        if session_id not in self.data:
            self.data[session_id] = {}
        self.data[session_id][name] = status
        self.status_manager.save(session_id, name, status=str(status))

    def get(self, session_id: str, name: str) -> Any:
        if session_id not in self.data:
            self.data[session_id] = {}
        if name not in self.data[session_id]:
            self.data[session_id][name] = False
        return self.data[session_id][name]
