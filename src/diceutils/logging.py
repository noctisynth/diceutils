from diceutils.exceptions import TooManyLoggersError
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Literal, Optional, Tuple, Union

import sqlite3

MAX_LOGGERS_PER_SESSION = 3


class LogManager:
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
            CREATE TABLE IF NOT EXISTS log (
                session_id TEXT,
                id TEXT,
                user_id TEXT,
                user_role TEXT,
                card_name TEXT,
                date TEXT,
                data TEXT,
                message_sequence TEXT
            );
            """
        )
        self.conn.commit()
        cursor.close()

    def _insert(
        self,
        cursor: sqlite3.Cursor,
        data: Tuple[str, str, str, str, str, str, str, str],
    ):
        cursor.execute(
            """
            INSERT INTO log (session_id, id, user_id, user_role, card_name, date, data, message_sequence) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            data,
        )

    def add(
        self,
        session_id: str,
        id: str,
        *,
        user_id: str,
        user_role: Literal["KP", "PL", "OB", "DICER"],
        card_name: str,
        date: str,
        data: str,
        message_sequence: str,
    ) -> None:
        count = self.count(session_id)
        if (
            count == MAX_LOGGERS_PER_SESSION and int(id) >= MAX_LOGGERS_PER_SESSION
        ) or count > MAX_LOGGERS_PER_SESSION:
            raise TooManyLoggersError(
                f"Too many loggers, expected less than {MAX_LOGGERS_PER_SESSION}, "
                f"but given index is '{id}'."
            )
        cursor = self.conn.cursor()
        self._insert(
            cursor,
            (
                session_id,
                id,
                user_id,
                user_role,
                card_name,
                date,
                data,
                message_sequence,
            ),
        )
        self.conn.commit()
        cursor.close()

    def count(self, session_id: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(DISTINCT id) AS unique_ids FROM log WHERE session_id = ?;",
            (session_id,),
        )
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def loadall(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT session_id, id, user_id, user_role, card_name, date, data FROM log"
        )
        result = cursor.fetchall()
        datas: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for session_id, id, user_id, user_role, card_name, date, data in result:
            if session_id not in datas:
                datas[session_id] = {}
            if id not in datas[session_id]:
                datas[session_id][id] = []

            datas[session_id][id].append(
                {
                    "user_id": user_id,
                    "user_role": user_role,
                    "card_name": card_name,
                    "date": date,
                    "data": eval(data),
                }
            )

        cursor.close()
        return datas

    def load(self, session_id: str, id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id, user_role, card_name, date, data FROM log "
            "WHERE session_id = ? AND id = ?",
            (session_id, id),
        )

        result = cursor.fetchall()
        datas: List[Dict[str, Any]] = []
        for user_id, user_role, card_name, date, data in result:
            datas.append(
                {
                    "user_id": user_id,
                    "user_role": user_role,
                    "card_name": card_name,
                    "date": date,
                    "data": eval(data),
                }
            )

        cursor.close()
        return datas

    def remove(self, session_id: str, id: str, message_sequence: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM log WHERE session_id = ? AND id = ? AND message_sequence = ?",
            (session_id, id, message_sequence),
        )
        self.conn.commit()
        cursor.close()

    def clear(self, session_id: str, id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM log WHERE session_id = ? AND id = ?", (session_id, id)
        )
        self.conn.commit()
        cursor.close()

    def close(self):
        self.conn.close()


class Logger:
    log_manager: LogManager

    def __init__(self, db_path: Union[Path, str] = "dicergirl.db"):
        self.log_manager = LogManager(db_path)
        self.db_path = db_path
        self.logs = {}

    def __repr__(self) -> str:
        return f"Logger(db='{self.db_path}')"

    def rescue(self) -> None:
        self.log_manager.close()

    def load(self, session_id: str, id: Union[int, str]) -> List[Dict[str, Any]]:
        return self.log_manager.load(session_id=session_id, id=str(id))

    def loadall(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        return self.log_manager.loadall()

    def next_id(self, session_id: str):
        return (
            count
            if (count := self.log_manager.count(session_id)) <= MAX_LOGGERS_PER_SESSION
            else None
        )

    def add(
        self,
        session_id: str,
        id: Union[str, int],
        *,
        user_id: str,
        user_role: Literal["KP", "PL", "OB", "DICER"] = "OB",
        card_name: str = "User",
        data: List[Any] = [],
        date: Optional[Union[str, datetime]] = None,
        message_sequence: str = "",
    ) -> None:
        id = str(id)
        if not data:
            raise ValueError("Could not log an empty data.")
        if not isinstance(user_role, str) or user_role.upper() not in (
            "KP",
            "PL",
            "OB",
            "DICER",
        ):
            raise ValueError(f"Unknown user role '{user_role}'.")
        if not message_sequence or not isinstance(message_sequence, str):
            raise ValueError("Message sequence string is require.")
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d %H:%M:%S")

        self.log_manager.add(
            session_id,
            id,
            user_id=user_id,
            user_role=user_role,
            card_name=card_name,
            date=date,
            data=str(data),
            message_sequence=message_sequence,
        )

    def remove(self, session_id: str, id: Union[str, int], message_sequence: str):
        self.log_manager.remove(
            session_id=session_id, id=str(id), message_sequence=message_sequence
        )

    def clear(self, session_id: str, id: Union[str, int]) -> None:
        self.log_manager.clear(session_id=session_id, id=str(id))
