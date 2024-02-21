"""
Overview
========

This module provides a CardsManager class for managing user cards data using SQLite database. 
It also includes a Cards class for handling card operations such as saving, loading, updating, and deleting.

Classes
=======

CardsManager:
    A class for managing user cards data using SQLite database.

    Methods:
        - save(user_id: str, cards: Dict[str, Any]) -> None: Saves user cards data.
        - load(user_id: str) -> Dict[str, Any]: Loads user cards data.
        - close(): Closes the database connection.

Cards:
    A class for handling card operations such as saving, loading, updating, and deleting.

    Methods:
        - save(): Saves the current card data.
        - load(): Loads the card data.
        - update(input: Input, cha_dict: Dict[str, Any], qid: str = "") -> None: Updates card data.
        - get(input: Input, qid: str = "") -> Dict[str, Any]: Retrieves card data.
        - delete(input: Input, qid: str = "") -> bool: Deletes card data.
"""

import pickle
import sqlite3

from pathlib import Path
from functools import wraps
from typing import Dict, Any, Generic, List, Literal, Set, TypeVar, Union

from infini.input import Input
from yaml.loader import FullLoader

from diceutils.exceptions import TooManyCardsError

from .utils import get_user_id, get_group_id

CARDS = {}
MAX_CARDS_PER_USER = 5
ROOT_PATH: Path = Path.home().joinpath(".dicergirl", "data")


class CachedProperty:
    """A decorator for caching property values."""

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance not in self.cache:
            self.cache[instance] = self.func(instance)
        return self.cache[instance]


def cached_method(func):
    """A decorator for caching method results."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_method_cache"):
            self._method_cache = {}
        # Convert args and kwargs to hashable objects
        args_key = pickle.dumps(args)
        kwargs_key = pickle.dumps(kwargs)
        cache_key = (func, args_key, kwargs_key)
        if cache_key not in self._method_cache:
            self._method_cache[cache_key] = func(self, *args, **kwargs)
        return self._method_cache[cache_key]

    return wrapper


class CardsManagerMeta(type):
    """Metaclass for caching methods in CardsManager class."""

    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if callable(attr_value):
                dct[attr_name] = cached_method(attr_value)
        return super().__new__(cls, name, bases, dct)


class CardsManager(metaclass=CardsManagerMeta):
    """A class for managing user cards data using SQLite database."""

    def __init__(
        self,
        db_path: Union[str, Path] = ":memory:",
        max_cards_per_user: Union[int, str] = MAX_CARDS_PER_USER,
    ):
        """Initialize CardsManager.

        Args:
            db_path (Union[str, Path], optional): Path to the SQLite database file.. Defaults to ":memory:".
            max_cards_per_user (Union[int, str], optional): Defaults to MAX_CARDS_PER_USER.
        """
        self.db_path = db_path
        self.max_cards_per_user = int(max_cards_per_user)
        self.conn = sqlite3.connect(db_path)
        self._create_table()
        self._method_cache = {}

    def _create_table(self):
        """Create table for storing user cards if not exists."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_cards (
                user_id TEXT,
                card_data TEXT
            )
        """
        )
        self.conn.commit()

    def save(self, user_id: str, cards: List[Dict[str, Any]]) -> None:
        """
        Save user cards data.

        Args:
            user_id (str): User ID.
            cards (Dict[str, Any]): Dictionary containing user cards data.

        Raises:
            TooManyCardsError: If the number of cards exceeds the maximum allowed limit.
        """
        if len(cards) > self.max_cards_per_user and self.db_path == ":memory:":
            raise TooManyCardsError("Exceeded maximum allowed cards per user")
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user_cards WHERE user_id=?", (user_id,))
        self.conn.commit()
        cursor.execute("INSERT INTO user_cards VALUES (?, ?)", (user_id, str(cards)))
        self.conn.commit()

    def load(self, target: str = "*") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load user cards data.

        Parameters:
            user_id (str): User ID or 'all' to load all data.

        Returns:
            Dict[str, Any]: Dictionary containing user cards data.
        """
        cursor = self.conn.cursor()
        if target.lower() == "*":
            cursor.execute("SELECT user_id, card_data FROM user_cards")
            result = cursor.fetchall()
            return {user_id: eval(card_data) for user_id, card_data in result}
        else:
            user_id = target
            cursor.execute(
                "SELECT card_data FROM user_cards WHERE user_id=?", (user_id,)
            )
            return eval(result[0]) if (result := cursor.fetchone()) else []

    def close(self):
        """Close the database connection."""
        self.conn.close()


class Cards(dict):
    """A class for handling card operations such as saving, loading, updating, and deleting."""

    cards_manager = CardsManager()

    def __init__(self, mode: str = "Unknown Mode"):
        """
        Initialize Cards.

        Parameters:
            mode (str, optional): Mode of the cards. Defaults to "Unknown Mode".
        """
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.mode = mode
        self.load()

    def save(self):
        """Save the current card data."""
        for user_id, user_data in self.data.items():
            self.cards_manager.save(user_id, user_data)

    def load(self, target: Union[Set[str], str] = "*"):
        """Load the card data."""
        if isinstance(target, str):
            if target == "*":
                self.data = self.cards_manager.load()  # type: ignore[dict]
            else:
                user_data = self.cards_manager.load(target)
                if len(user_data) > 0:
                    self.data[tartget] = user_data  # type: ignore[list]
        elif isinstance(target, set):
            for user_id in target:
                user_data = self.cards_manager.load(user_id)
                if len(user_data) > 0:
                    self.data[user_id] = user_data  # type: ignore[list]

    def update(
        self, user_id: str, index: int = 0, cha_dict: Union[Dict[str, Any], None] = None
    ) -> None:
        """Update Card Data.

        Args:
            user_id (str): target user id.
            index (int): card index.
            cha_dict (Dict[str, Any]): card content.
        """
        if cha_dict is None:
            cha_dict = {}
        self.data[user_id][index].update(cha_dict)
        self.save()

    def get(
        self, user_id: str, index: Union[int, None] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Get Card Data.

        Args:
            user_id (str): user id.
            index (int): index to select.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]], None]: card data.
        """
        data = self.data.get(user_id, None)
        return data if index is None else data[index] if data is not None else None

    def delete(self, user_id: str, index: Union[int, None] = None) -> bool:
        """
        Delete card data.

        Parameters:
            input (Input): Input object.
            qid (str, optional): Query ID. Defaults to "".

        Returns:
            bool: True if deletion is successful, False otherwise.
        """
        if self.data.get(user_id, None) is not None:
            if index is None:
                del self.data[user_id]
                self.save()
                return True
            if self.data[user_id].get(index, None) is not None:  # type: ignore[dict]
                del self.data[user_id][index]
                self.save()
                return True
        return False
