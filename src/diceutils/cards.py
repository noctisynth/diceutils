import yaml

from infini.input import Input
from yaml.loader import FullLoader
from typing import Dict, Any
from pathlib import Path
from .utils import get_user_id, get_group_id

cards = {}


class Cards:
    data_path: Path = Path.home().joinpath(".dicergirl", "data")

    def __init__(self, mode: str = None, cache_path: Path = None):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.mode = mode if mode else "未知模式"
        self.cache_path = (
            cache_path if cache_path else self.data_path / f"{mode}_cards.yaml"
        )
        cards[mode] = self

    def init(self):
        if not self.cache_path.parent.exists():
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        with self.cache_path.open(mode="w", encoding="utf-8") as f:
            yaml.dump({"mode": self.mode, "cards": {}}, f)

    def save(self):
        if not self.cache_path.exists():
            self.init()

        with self.cache_path.open(mode="w", encoding="utf-8") as f:
            yaml.dump({"mode": self.mode, "cards": self.data}, f, allow_unicode=True)

    def load(self) -> dict:
        if not self.cache_path.exists():
            self.init()

        with self.cache_path.open(mode="r", encoding="utf-8") as f:
            data = yaml.load(f, FullLoader)
            if data is None:
                self.data = {}
            else:
                self.data = data["cards"]

        return self.data

    def update(
        self, input: Input, cha_dict: dict, qid: str = "", save: bool = True
    ) -> None:
        group_id = get_group_id(input)
        if not self.data.get(group_id):
            self.data[group_id] = {}

        self.data[group_id].update({qid if qid else get_user_id(input): cha_dict})

        return self.save() if save else None

    def get(self, input: Input, qid=""):
        group_id = get_group_id(input)
        if self.data.get(group_id):
            if self.data[group_id].get(qid if qid else get_user_id(input)):
                return self.data[group_id].get(qid if qid else get_user_id(input))
        else:
            return None

    def delete(self, input: Input, qid: str = "", save: bool = True) -> bool:
        if self.get(input, qid=qid):
            if self.data[get_group_id(input)].get(qid if qid else get_user_id(input)):
                self.data[get_group_id(input)].pop(qid if qid else get_user_id(input))
            if save:
                self.save()
            return True
        return False

    def delete_skill(
        self, input: Input, skill_name: str, qid: str = "", save: bool = True
    ) -> bool:
        if self.get(input, qid=qid):
            data = self.get(input, qid=qid)
            if data["skills"].get(skill_name):
                data["skills"].pop(skill_name)
                self.update(input, data, qid=qid, save=save)
                return True
        return False
