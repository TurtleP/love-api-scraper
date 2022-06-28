import re
from pathlib import Path

from .api import API


class Module(API):

    def __init__(self, api_dict: dict, filepath: Path):
        super().__init__(filepath)

        # Our Methods
        self.get_methods(api_dict["modules"])

        for root_item in api_dict["modules"]:
            if root_item["name"].lower() == self.name.lower():
                self.description = re.sub(
                    "\s\s+", " ", root_item["description"]).replace("\n", "")

    def get_description(self) -> str:
        return self.description

    def get_output_dir(self) -> Path:
        return API.__OUTPUT_FOLDER__ / "modules"

    def get_wiki_format(self) -> str:
        return f"love.{self.name}."

    def get_filename(self) -> str:
        return f"love.{self.name}.csv"
