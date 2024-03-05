"""
@author         :     HsiangNianian<i@jyunko.cn>,
                      苏向夜<fu050409@163.com>
@date           :     Feb. 23, 2024.
@description    :     This Module Provides Access to the Database and 
                      Database Connection Functions for Cards Management. 
"""

import pickle
import sqlite3

from pathlib import Path
from functools import wraps
from typing import Dict, Any, List, Optional, Set, Union

from diceutils.exceptions import TooManyCardsError, UnkownMode

MAX_CARDS_PER_USER = 9


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


class CardsPool(object):
    _cards_pool = {}
    _cache_cards_pool = {}

    @CachedProperty
    def cards_pool(self):
        return self._cards_pool

    @CachedProperty
    def cache_cards_pool(self):
        return self._cache_cards_pool

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return self._cards_pool.__repr__()

    @staticmethod
    def register(mode_name: str):
        if mode_name not in CardsPool._cards_pool.keys():
            CardsPool._cards_pool[mode_name] = Cards(mode=mode_name, store=True)
            CardsPool._cache_cards_pool[mode_name] = Cards(mode=mode_name)

    @staticmethod
    def get(mode_name: str) -> Optional["Cards"]:
        return CardsPool._cards_pool.get(mode_name)

    @staticmethod
    def reload(mode_name: str):
        if mode_name not in CardsPool._cards_pool.keys():
            raise UnkownMode(f'Mode "{mode_name}" was not regitered yet.')
        CardsPool._cards_pool[mode_name] = Cards(mode=mode_name, store=True)
        CardsPool._cache_cards_pool[mode_name] = Cards(mode=mode_name)


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
                card_data TEXT,
                selected_card INTERGER
            )
        """
        )
        self.conn.commit()
        cursor.close()

    def save(
        self, cards: Dict[str, List[Dict[str, Any]]], selected_cards: Dict[str, int]
    ) -> None:
        """Save user cards data.

        Args:
            cards (Dict[str, List[Dict[str, Any]]]): Dictionary containing user cards data.
                The keys represent the user IDs.

        Raises:
            TooManyCardsError: If the number of cards exceeds the maximum allowed limit.
        """
        if not cards:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM user_cards")
            self.conn.commit()
            cursor.close()
            return

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user_cards")
        for user_id, card_data in cards.items():
            if len(card_data) > self.max_cards_per_user:
                raise TooManyCardsError("Exceeded maximum allowed cards per user")
            cursor.execute(
                "INSERT INTO user_cards VALUES (?, ?, ?)",
                (user_id, str(card_data), selected_cards.get(user_id) or 0),
            )
        self.conn.commit()
        cursor.close()

    def load(
        self, target: str = "*"
    ) -> tuple[Union[Dict[str, Any], List[Dict[str, Any]]], Union[Dict[str, int], int]]:
        """Load user cards data.

        Parameters:
            target (str): User ID or '*' to load all data.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Dictionary containing user cards data.
        """
        cursor = self.conn.cursor()
        if target.lower() == "*":
            cursor.execute("SELECT user_id, card_data, selected_card FROM user_cards")
            result = cursor.fetchall()
            datas = {}
            selected_cards = {}
            for user_id, card_data, selected_card in result:
                datas[user_id] = eval(card_data)
                selected_cards[user_id] = selected_card
            cursor.close()
            return datas, selected_cards
        else:
            user_id = target
            cursor.execute(
                "SELECT card_data, selected_card FROM user_cards WHERE user_id=?",
                (user_id,),
            )
            results = (
                (eval(result[0]), result[1])
                if (result := cursor.fetchone())
                else ([], 0)
            )
            cursor.close()
            return results

    def close(self):
        """Close the database connection."""
        self.conn.close()


class Cards:
    """A class for handling card operations such as saving, loading, updating, and deleting."""

    cards_manager: CardsManager

    def __init__(self, mode: Optional[str] = None, store: bool = False):
        """Initialize Cards.

        Args:
            mode (str): Mode of the cards.
            store (bool): Decide whether this class save to disk or memory. (Defaults to ``False``)
        """
        if mode is None or not mode:
            mode = "unknown_mode"
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.selected_cards: Dict[str, int] = {}
        self.mode = mode
        self.cards_manager = CardsManager(f"{mode}.db" if store else ":memory:")
        self.load()

    def save(self):
        """Save the current card data."""
        self.cards_manager.save(self.data, self.selected_cards)

    def load(self, target: Union[Set[str], str] = "*"):
        """Load the card data."""
        if isinstance(target, str):
            if target == "*":
                data, selected_cards = self.cards_manager.load()
                assert isinstance(data, dict)
                assert isinstance(selected_cards, dict)
                self.data = data
                self.selected_cards = selected_cards
            else:
                user_data, selected_card = self.cards_manager.load(target)
                assert isinstance(user_data, list)
                assert isinstance(selected_card, int)
                if len(user_data) > 0:
                    self.data[target] = user_data
                    self.selected_cards[target] = selected_card
        elif isinstance(target, set):
            for user_id in target:
                user_data, selected_card = self.cards_manager.load(user_id)
                if len(user_data) > 0:
                    assert isinstance(user_data, list)
                    assert isinstance(selected_card, int)
                    self.data[user_id] = user_data
                    self.selected_cards[user_id] = selected_card

    def _get_selected_id(self, user_id: str) -> int:
        return self.selected_cards.get(user_id) or 0

    def new(self, user_id: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Set up a new card."""
        length = self.count(user_id)
        if length >= MAX_CARDS_PER_USER:
            raise TooManyCardsError(
                f"Cards count for a user should not more than {MAX_CARDS_PER_USER}."
            )
        self.update(user_id, length, attributes=attributes or {})

    def update(
        self,
        user_id: str,
        index: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update Card Data.

        Args:
            user_id (str): target user id.
            index (Optional[int]): card index.
            attributes (Optional[Dict[str, Any]]): card content, default is ``None``.
        """
        index = index or self._get_selected_id(user_id)
        if attributes is None:
            attributes = {}
        if user_id not in self.data:
            self.data[user_id] = []
        if len(self.data[user_id]) == 0:
            self.data[user_id].append(attributes)
        if index > len(self.data[user_id]) - 1:
            self.data[user_id].append(attributes)
        else:
            self.data[user_id][index].update(attributes)
        self.save()

    def get(
        self, user_id: str, index: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get Card Data.

        Args:
            user_id (str): user id.
            index (Optional[int]): index to select.

        Returns:
            Optional[Dict[str, Any]]: card data.
        """
        if index is None:
            index = self._get_selected_id(user_id)

        return (
            self.data.get(user_id, [])[index]
            if 0 <= index < len(self.data.get(user_id, []))
            else None
        )

    def getall(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get all card datas of a user."""
        return self.data.get(user_id)

    def delete(self, user_id: str, index: Optional[int] = None) -> bool:
        """Delete Card Data.

        Args:
            user_id (str): user id.
            index (Optional[int], optional): index of card data. Defaults to ``None``.

        Returns:
            bool: True if deletion is successful, False otherwise.
        """
        if user_id in self.data:
            if index is None:
                del self.data[user_id]
                self.save()
                return True
            if (
                0 <= index < len(self.data[user_id])
                and self.data[user_id][index] is not None
            ):
                del self.data[user_id][index]
                self.save()
                return True

        return False

    def select(self, user_id: str, index: int = 0) -> None:
        """Set a card index as default card."""
        if index > self.count(user_id) - 1:
            raise TooManyCardsError(
                f"This user has only {self.count(user_id)} cards, "
                f"but index {index} was provided."
            )
        self.selected_cards[user_id] = index
        self.save()

    def get_selected_id(self, user_id: str) -> int:
        """Get the current selected card id."""
        return self._get_selected_id(user_id)

    def count(self, user_id: str) -> int:
        """Count the number of a related user's cards."""
        return len(self.data.get(user_id, []))

    def clear(self, user_id: str) -> None:
        """Clear all cards of a user."""
        self.selected_cards[user_id] = 0
        self.data[user_id] = []
        self.save()
