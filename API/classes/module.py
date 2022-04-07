from pathlib import Path

from .api import API


class Module(API):

    def __init__(self, api_dict: dict, filepath: Path):
        super().__init__(filepath)

        # Our Methods
        self.get_methods(api_dict["modules"])

    def get_output_dir(self) -> Path:
        return API.__OUTPUT_FOLDER__ / "modules"

    def get_wiki_format(self) -> str:
        return f"love.{self.name}."

    def get_filename(self) -> str:
        return f"love.{self.name}.csv"
