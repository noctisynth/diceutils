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

import yaml
import sqlite3
# ----------------------------------------------------------------
from pathlib import Path
from functools import wraps
from typing import Dict, Any, TypeVar
# ----------------------------------------------------------------
from infini.input import Input
from yaml.loader import FullLoader
# ----------------------------------------------------------------
from .utils import get_user_id, get_group_id

CARDS = {}
ROOT_PATH: Path = Path.home().joinpath(".dicergirl", "data")
MAX_CARDS_PER_USER = 5


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
        cache_key = (func, args, frozenset(kwargs.items()))
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

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize CardsManager.

        Parameters:
            db_path (str): Path to the SQLite database file.
        """
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

    def save(self, user_id: str, cards: Dict[str, Any]) -> None:
        """
        Save user cards data.

        Parameters:
            user_id (str): User ID.
            cards (Dict[str, Any]): Dictionary containing user cards data.

        Raises:
            ValueError: If the number of cards exceeds the maximum allowed limit.
        """
        if len(cards) > MAX_CARDS_PER_USER:
            raise ValueError("Exceeded maximum allowed cards per user")
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user_cards WHERE user_id=?", (user_id,))
        self.conn.commit()
        cursor.execute("INSERT INTO user_cards VALUES (?, ?)", (user_id, str(cards)))
        self.conn.commit()

    def load(self, user_id: str) -> Dict[str, Any]:
        """
        Load user cards data.

        Parameters:
            user_id (str): User ID.

        Returns:
            Dict[str, Any]: Dictionary containing user cards data.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT card_data FROM user_cards WHERE user_id=?", (user_id,))
        return eval(result[0]) if (result := cursor.fetchone()) else {}

    def close(self):
        """Close the database connection."""
        self.conn.close()

class Cards:
    """A class for handling card operations such as saving, loading, updating, and deleting."""

    cards_manager = CardsManager()

    def __init__(self, mode: str = "Unknown Mode"):
        """
        Initialize Cards.

        Parameters:
            mode (str, optional): Mode of the cards. Defaults to "Unknown Mode".
        """
        self.data: Dict[str, Dict[str, Any]] = {}
        self.mode = mode
        self.load()

    def save(self):
        """Save the current card data."""
        user_id = "some_user_id"  # Actual user ID retrieval logic needed
        self.cards_manager.save(user_id, self.data)

    def load(self):
        """Load the card data."""
        user_id = "some_user_id"  # Actual user ID retrieval logic needed
        self.data = self.cards_manager.load(user_id)

    def update(self, input: Input, cha_dict: Dict[str, Any], qid: str = "") -> None:
        """
        Update card data.

        Parameters:
            input (Input): Input object.
            cha_dict (Dict[str, Any]): Dictionary containing updated card data.
            qid (str, optional): Query ID. Defaults to "".
        """
        user_id = "some_user_id"  # Actual user ID retrieval logic needed
        self.data.update({qid or get_user_id(input): cha_dict})
        self.save()

    def get(self, input: Input, qid="") -> Dict[str, Any]:
        """
        Retrieve card data.

        Parameters:
            input (Input): Input object.
            qid (str, optional): Query ID. Defaults to "".

        Returns:
            Dict[str, Any]: Dictionary containing card data.
        """
        user_id = "some_user_id"  # Actual user ID retrieval logic needed
        return self.data.get(qid or get_user_id(input), {})

    def delete(self, input: Input, qid: str = "") -> bool:
        """
        Delete card data.

        Parameters:
            input (Input): Input object.
            qid (str, optional): Query ID. Defaults to "".

        Returns:
            bool: True if deletion is successful, False otherwise.
        """
        user_id = "some_user_id"  # Actual user ID retrieval logic needed
        if qid:
            return self._extracted_from_delete_14(qid, input)
        elif not qid and get_user_id(input) in self.data:
            return self._extracted_from_delete_14(qid, input)
        return False

    # TODO Rename this here and in `delete`
    def _extracted_from_delete_14(self, qid, input):
        del self.data[qid or get_user_id(input)]
        self.save()
        return True