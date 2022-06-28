from logging import root
from pathlib import Path

from .api import API


class Object(API):

    def __init__(self, api_dict: dict, supers: dict, filepath: Path):
        super().__init__(filepath)

        if self.name == "gamepad":
            self.name = "joystick"
        elif self.name == "luathread":
            self.name = "thread"

        self.supers = supers

        # Super-Super Object Methods
        self.get_super_methods(api_dict["types"], supers)

        # Super Object Methods
        for item in api_dict["modules"]:
            self.get_super_methods(item["types"], supers)

        # Our Methods
        self.module = ""
        self.description = ""

        for item in api_dict["modules"]:
            self.get_methods(item["types"])
            for root_item in item["types"]:
                if root_item["name"].lower() == self.name.lower():
                    self.module = item["name"]
                    self.description = root_item["description"]

        if not self.module and "data" in self.name:
            self.module = "data"

        self.score = 1

    def get_description(self) -> str:
        return self.description

    def get_supers(self) -> list:
        return self.supers

    def get_name(self) -> str:
        return self.name

    def get_module(self) -> str:
        return self.module

    def get_wiki_format(self) -> str:
        return f"{self.name}:"

    def get_output_dir(self) -> Path:
        return API.__OUTPUT_FOLDER__ / "objects"

    def get_super_methods(self, api_dict: dict, super_info: list):
        for root_item in api_dict:
            if root_item["name"] in super_info:
                for method in root_item["functions"]:
                    self.methods[method["name"]] = method["description"]
