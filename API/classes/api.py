import csv
import re
from pathlib import Path

__FUNCTION_STR_REGEX__ = re.compile(r".*\{.*\"(.*)\".*Wrap.*")

import logging

CONSOLE_METHODS = {
    "newBMFontRasterizer": "Creates a new Nintendo 3DS Font Rasterizer",
    "get3D": "Gets whether 3D is enabled on the Nintendo 3DS",
    "get3DDepth": "Gets the slider value for the 3D Depth on the Nintendo 3DS",
    "set3D": "Sets whether Stereoscopic 3D should be enabled on the Nintendo 3DS",
    "getWide": "Gets whether wide mode is enabled on the Nintendo 3DS",
    "setWide": "Sets whether wide mode should be enabled on the Nintendo 3DS",
    "setTextInput": "Displays the Software Keyboard applet for text input. Calls love.textinput on success."
}


class API:

    __DEBUG__ = True

    __OUTPUT_FOLDER__ = Path("output")

    def __init__(self, filepath: Path):
        if API.__DEBUG__:
            logging.basicConfig(filename='debug.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                                encoding='utf-8', level=logging.DEBUG)

        self.name = filepath.stem.split("_")[1].lower()

        if "module" in self.name:
            self.name = self.name.replace("module", "")

        self.filepath = filepath

        self.methods = dict()
        self.get_output_dir().mkdir(exist_ok=True, parents=True)
        self.score = 0

    def get_name(self) -> str:
        return self.name

    def __lt__(self, other):
        return self.score < other.score

    def get_wiki_format(self) -> str:
        raise NotImplementedError

    def get_filename(self, ext="csv") -> str:
        return f"{self.name}.{ext}"

    def get_output_dir(self) -> Path:
        raise NotImplementedError

    def get_output_path(self) -> Path:
        return self.get_output_dir() / self.get_filename()

    def get_methods(self, api_dict: dict):
        for root_item in api_dict:
            if root_item["name"].lower() == self.name.lower():
                for method in root_item["functions"]:
                    self.methods[method["name"]
                                 ] = method["description"].replace("\n", " ")

    def generate(self):
        contents = self.filepath.read_text()

        print(f"Generating file for {self.get_filename()}..")

        if API.__DEBUG__:
            logging.info(f"Generating file for {self.get_filename()}..")

        with open(self.get_output_path(), "w", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Function Name", "Description"])

            matches = __FUNCTION_STR_REGEX__.findall(contents)

            description = ""
            match_info = ""

            for match in matches:
                # Skip internal functions
                if "_" in match:
                    continue

                try:
                    if not match in CONSOLE_METHODS:
                        description = re.sub("\s\s+", " ", self.methods[match])
                        match_info = f"[{match}](https://love2d.org/wiki/love.{self.name}.{match})"
                    else:
                        description = CONSOLE_METHODS[match]
                        match_info = match

                    writer.writerow([match_info, description])

                    del self.methods[match]
                except KeyError:  # found a console-specific thing
                    pass
