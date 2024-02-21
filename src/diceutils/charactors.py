import re
from typing import List, Any
import json


class AttributeDefinition:
    def __init__(self, name, _type, alias=None):
        self.name = name
        self.type = _type
        self.alias = alias or []
        self.alias.append(name)

    def __repr__(self):
        return (f"AttributeDefinition(name={self.name!r}, type={self.type.__name__!r}, "
                f"alias={self.alias!r})")


class AttributeDefinitionGroup:
    def __init__(self, name, attributes):
        self.group_name = name
        self.definitions: List[AttributeDefinition] = attributes

    def __repr__(self):
        return f"AttributeDefinitionGroup(name={self.group_name!r}, definitions={self.definitions})"


class Template:
    def __init__(self, template_name, template: List[AttributeDefinitionGroup]):
        self.template_name = template_name
        self.__raw_template = {group.group_name: group for group in template}
        self.__attr_name_to_group_name = {definition.name: group.group_name for group in
                                          self.__raw_template.values() for definition in group.definitions}
        self.__template = {attr.name: attr for group in template for attr in group.definitions}
        self.__alias_map = {alias: attr.name for attr in self.__template.values() for alias in attr.alias}

    def __repr__(self):
        return f"Template(name={self.template_name!r}, template={self.__raw_template!r})"

    def get_attr_type(self, name: str):
        if name not in self.__template:
            return None
        return self.__template[name].type

    def get_attr_names_by_group(self, name):
        if name not in self.__raw_template:
            raise KeyError(f"Group '{name}' is not defined.")
        return [definition.name for definition in self.__raw_template[name].definitions]

    def get_main_name_or_raise(self, name: str) -> str:
        main_name = self.get_main_name(name)
        if not main_name:
            raise ValueError(f"'{name}' does not exist in the template.")
        return main_name

    def get_main_name(self, name: str) -> str | None:
        main_name = self.__alias_map.get(name)
        if self._is_exist(main_name):
            return main_name
        else:
            return None

    def is_valid_value(self, name: str, value):
        if not self._is_exist(name):
            return False
        if isinstance(value, self.__template[name].type):
            return True
        return False

    def _is_exist(self, name: str) -> bool:
        return name in self.__template


class Character:
    def __init__(self, template_name, template):
        self.__attributes = {}
        self.template_name = template_name
        self.template = template

    def __repr__(self):
        return f"Character(name={self.template_name!r}, attributes={self.__attributes!r})"

    def set(self, name: str, value):
        main_name = self.template.get_main_name(name) or name
        attr_type = self.template.get_attr_type(name)
        if attr_type and isinstance(value, attr_type):
            self.__attributes[main_name] = value
            return
        if not attr_type and isinstance(value, (int, float)):
            self.__attributes[main_name] = value
            return
        new_value = self._convert_str(value, attr_type)
        if attr_type and not isinstance(new_value, attr_type):
            return
        if isinstance(new_value, (int, float)) and str(value).startswith(("+", "-")):
            if name in self.__attributes:
                convert_type = type(self.__attributes[name])
                self.__attributes[main_name] += convert_type(new_value)
                return
        self.__attributes[main_name] = new_value

    def get(self, name: str):
        main_name = self.template.get_main_name(name)
        if main_name in self.__attributes:
            return self.__attributes[main_name]

    def get_by_group_name(self, name: str):
        names = self.template.get_attr_names_by_group(name)
        result = {}
        for name in names:
            if name in self.__attributes:
                result[name] = self.__attributes[name]
        return result

    def load(self, **kwargs):
        for key, value in kwargs.items():
            self.set(key, value)

    def import_data(self, attributes):
        self.__attributes = attributes

    def export_data(self):
        return self.__attributes

    @staticmethod
    def _convert_str(text: str, convert_type=None):
        def isdigit(s: str):
            return bool(re.match(r"^[+-]?\d+$", s))

        def isfloat(s: str):
            return bool(re.match(r"^[+-]?\d+\.\d+$", s))

        if not convert_type:
            if isdigit(text):
                return int(text)
            elif isfloat(text):
                return float(text)
        else:
            if convert_type in [list, dict]:
                return json.loads(text)
            else:
                try:
                    return convert_type(text)
                except (ValueError, TypeError):
                    return text
        return text


class TemplateManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TemplateManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.__templates = {}
        return cls._instance

    def add_template(self, name: str, template: List[AttributeDefinitionGroup]):
        self.__templates[name] = Template(name, template)
        print(self.__templates)

    def get_template(self, name: str):
        if name not in self.__templates:
            raise KeyError("No template.")
        return self.__templates[name]

    def build_card(self, name: str):
        return Character(name, self.get_template(name))
