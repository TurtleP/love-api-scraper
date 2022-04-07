import csv
import re
from pathlib import Path

__FUNCTION_STR_REGEX__ = re.compile(r".*\{.*\"(.*)\".*Wrap.*")

import logging


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

    def get_wiki_format(self) -> str:
        raise NotImplementedError

    def get_filename(self) -> str:
        return f"{self.name}.csv"

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

            for match in matches:
                # Skip internal functions
                if "_" in match:
                    continue

                try:
                    description = self.methods[match]
                    writer.writerow([match, ""])
                    del self.methods[match]
                except KeyError:
                    if API.__DEBUG__:
                        logging.error(
                            f"No description for {self.get_wiki_format()}{match}!")

            for key, value in self.methods.items():
                writer.writerow([key, ""])
