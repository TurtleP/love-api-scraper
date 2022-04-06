from pathlib import Path

from .api import API


class Module(API):

    def __init__(self, api_dict: dict, filepath: Path):
        super().__init__(filepath)

        # Our Methods
        self.get_methods(api_dict["modules"])
