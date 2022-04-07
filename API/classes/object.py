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

        # Super-Super Object Methods
        self.get_super_methods(api_dict["types"], supers)

        # Super Object Methods
        for item in api_dict["modules"]:
            self.get_super_methods(item["types"], supers)

        # Our Methods
        for item in api_dict["modules"]:
            self.get_methods(item["types"])

    def get_wiki_format(self) -> str:
        return f"{self.name}:"

    def get_output_dir(self) -> Path:
        return API.__OUTPUT_FOLDER__ / "objects"

    def get_super_methods(self, api_dict: dict, super_info: list):
        for root_item in api_dict:
            if root_item["name"] in super_info:
                for method in root_item["functions"]:
                    self.methods[method["name"]] = method["description"]
