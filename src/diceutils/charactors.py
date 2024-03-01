from typing import Dict, List, Any, Optional
from diceutils.dicer import Dicer

import json
import re


class Attribute:
    def __init__(self, name: str, _type: type, alias: Optional[List[str]] = None):
        self.name = name
        self.type = _type
        self.alias = alias or []
        self.alias.append(name)

    def __repr__(self):
        return (
            f"Attribute(name={self.name!r}, type={self.type.__name__!r}, "
            f"alias={self.alias!r})"
        )


class AttributeGroup:
    def __init__(self, index: str, name: str, attributes: List[Attribute]):
        self.index = index
        self.name = name
        self.attributes: List[Attribute] = attributes

    def __repr__(self):
        return f"AttributeGroup(index={self.index!r}, attributes={self.attributes})"


class Template:
    def __init__(self, name: str, template: List[AttributeGroup]):
        self.name = name
        self.__raw_template = {group.index: group for group in template}
        # self.__attr_name_to_group_name = {
        #     definition.name: group.group_name
        #     for group in self.__raw_template.values()
        #     for definition in group.definitions
        # }
        self.__template = {
            attr.name: attr for group in template for attr in group.attributes
        }
        self.__template_display = {
            attr.name: attr.alias[0] for group in template for attr in group.attributes
        }
        self.__alias_map = {
            alias: attr.name
            for attr in self.__template.values()
            for alias in attr.alias
        }

    def __repr__(self):
        return f"Template(name={self.name!r}, template={self.__raw_template!r})"

    def get_attr_type(self, name: str):
        if name not in self.__template:
            return None
        return self.__template[name].type

    def get_attr_names_by_group(self, name: str):
        if name not in self.__raw_template:
            raise KeyError(f"Group '{name}' is not defined.")
        return [attribute.name for attribute in self.__raw_template[name].attributes]

    def get_main_name_or_raise(self, name: str) -> str:
        main_name = self.get_main_name(name)
        if not main_name:
            raise ValueError(f"'{name}' does not exist in the template.")
        return main_name

    def get_main_name(self, name: str) -> Optional[str]:
        main_name = self.__alias_map.get(name)
        if self._is_exist(main_name):
            return main_name
        else:
            return None

    def get_display_name(self, name: str) -> Optional[str]:
        return self.__template_display.get(name)

    def has_group(self, group_name: str) -> bool:
        return group_name in self.__raw_template

    def get_group_display_name(self, group_name: str) -> Optional[str]:
        return group.name if (group := self.__raw_template.get(group_name)) else None

    def is_valid_value(self, name: str, value):
        if not self._is_exist(name):
            return False
        if isinstance(value, self.__template[name].type):
            return True
        return False

    def _is_exist(self, name: Optional[str]) -> bool:
        return name in self.__template


class Character:
    def __init__(self, template: Template):
        self.__attributes = {}
        self.template = template

    def __repr__(self):
        return (
            f"Character(name={self.template.name!r}, attributes={self.__attributes!r})"
        )

    def set(self, name: str, value: Any):
        main_name = self.template.get_main_name(name) or name
        attr_type = self.template.get_attr_type(main_name)
        if attr_type and isinstance(value, attr_type):
            self.__attributes[main_name] = value
            return
        if not attr_type and isinstance(value, (int, float)):
            self.__attributes[main_name] = value
            return
        new_value = self._convert_str(value, attr_type)
        if attr_type and not isinstance(new_value, attr_type):
            raise ValueError
        if isinstance(new_value, (int, float)) and str(value).startswith(("+", "-")):
            if name in self.__attributes:
                convert_type = type(self.__attributes[name])
                self.__attributes[main_name] += convert_type(new_value)
                return
        self.__attributes[main_name] = new_value

    def get(self, name: str):
        main_name = self.template.get_main_name(name) or name
        if main_name in self.__attributes:
            return self.__attributes[main_name]

    def get_by_group_name(self, name: str):
        names = self.template.get_attr_names_by_group(name)
        result = {}
        for name in names:
            if name in self.__attributes:
                result[name] = self.__attributes[name]
        return result

    def get_group_display_name(self, name: str) -> Optional[str]:
        return self.template.get_group_display_name(name)

    def has_group(self, name: str) -> bool:
        return self.template.has_group(name)

    def display_group(self, name: str) -> str:
        group = self.get_by_group_name(name)
        results = []
        for attr, data in group.items():
            results.append(f"{self.template.get_display_name(attr)}: {data}")
        return " ".join(results)

    def loads(self, attributes: Dict[str, Any]):
        for key, value in attributes.items():
            self.set(key, value)

    def plain_loads(self, attributes):
        self.__attributes = attributes

    def dumps(self):
        return self.__attributes

    @staticmethod
    def _convert_str(text: str, convert_type: Optional[type] = None):
        def isdigit(s: str):
            return bool(re.match(r"^[+-]?\d+$", s))

        def isfloat(s: str):
            return bool(re.match(r"^[+-]?\d+\.\d+$", s))

        if not convert_type:
            if isdigit(text):
                return int(text)
            elif isfloat(text):
                return float(text)
            elif text == "/":
                return 0
            elif Dicer.check(text):
                return Dicer(text).roll().outcome
        else:
            if convert_type in (list, dict):
                return json.loads(text)
            elif convert_type in (int, float) and Dicer.check(text):
                return Dicer(text).roll().outcome
            else:
                try:
                    return convert_type(text)
                except (ValueError, TypeError):
                    return text
        return text


class TemplateManager:
    _instance = None
    __templates: dict

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TemplateManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.__templates = {}
        return cls._instance

    def add_template(self, name: str, template: List[AttributeGroup]):
        self.__templates[name.lower()] = Template(name, template)

    def get_template(self, name: str):
        if (name := name.lower()) not in self.__templates:
            raise KeyError(f"No template named '{name}'.")
        return self.__templates[name]

    def build_card(self, name: str):
        return Character(self.get_template(name))


manager = TemplateManager()
