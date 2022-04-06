import csv
import re
from pathlib import Path

__FUNCTION_STR_REGEX__ = re.compile(r".*\{.*\"(.*)\".*Wrap.*")

import logging

logging.basicConfig(filename='debug.log',
                    encoding='utf-8', level=logging.DEBUG)


class API:

    __DEBUG_FOLDER__ = Path("debug")
    __DEBUG__ = True

    __OUTPUT_FOLDER__ = Path("output")

    def __init__(self, filepath: Path, is_object=False):
        self.name = filepath.stem.split("_")[1]
        if "module" in self.name:
            self.name = self.name.replace("module", "")

        self.filepath = filepath

        self.methods = dict()
        self.is_object = is_object

    def dump(self):
        if not API.__DEBUG_FOLDER__.exists():
            API.__DEBUG_FOLDER__.mkdir()

        with open(f"debug/{self.get_name()}.txt", "w") as file:
            for key, value in self.methods.items():
                print(f"{key}: {value}", file=file)

    def get_methods(self, api_dict: dict):
        for root_item in api_dict:
            if root_item["name"].lower() == self.name.lower():
                for method in root_item["functions"]:
                    self.methods[method["name"]
                                 ] = method["description"].replace("\n", " ")

    def get_name(self) -> str:
        return self.name

    def generate(self):
        if API.__DEBUG__:
            self.dump()

        if not API.__OUTPUT_FOLDER__.exists():
            API.__OUTPUT_FOLDER__.mkdir()

        contents = self.filepath.read_text()

        filename = self.name
        if not self.is_object:
            filename = f"love.{self.name}"

        print(f"Generating file for {filename}.csv..")

        if API.__DEBUG__:
            logging.info(f"Generating file for {filename}.csv..")

        save_path = API.__OUTPUT_FOLDER__ / filename

        with open(f"{save_path}.csv", "w", newline='') as csvfile:
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
                        logging.error(f"No description for {match}!")

            for key, value in self.methods.items():
                writer.writerow([key, ""])
