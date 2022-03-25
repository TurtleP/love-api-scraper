import csv
import json
import re
from argparse import ArgumentParser
from pathlib import Path

import urllib3

__FUNCTION_STR_REGEX__ = re.compile(".*\{.*\"(.*)\".*Wrap.*")

__LOVE_API_URL__ = "https://love2d-community.github.io/love-api/love-api.json"
__LOVE_API_JSON__ = Path("love_api.json")

__LOVE_API_DATA__ = None


def get_description(api, obj: str, method: str, is_object: bool = False) -> list | None:
    # A stupidly ineffecient function to handle all of this, needs less code duplication

    data = list()

    json_dict = api["modules"]

    if not is_object:
        for root_item in json_dict:
            if obj.lower() == root_item["name"].lower():
                for method_item in root_item["functions"]:
                    if method.lower() == method_item["name"].lower():
                        data.append(root_item["name"])
                        data.append(
                            method_item["description"].strip().replace("\n", "").replace('"', ""))
                        break
    else:
        # Check SuperTypes first
        for root_item in api["types"]:
            if obj.lower() == root_item["name"].lower():
                for method_item in root_item["functions"]:
                    if method.lower() == method_item["name"].lower():
                        data.append(root_item["name"])
                        data.append(
                            method_item["description"].strip().replace("\n", "").replace('"', ""))
                        break

        for root_item in json_dict:
            for type_item in root_item["types"]:
                if obj.lower() == type_item["name"].lower():
                    for method_item in type_item["functions"]:
                        if method.lower() == method_item["name"].lower():
                            data.append(type_item["name"])
                            data.append(
                                method_item["description"].strip().replace("\n", "").replace('"', ""))
                            break

    return data


def create_csv_file(api: dict, name: str, path: Path, is_object=False):
    __output__ = Path("output")
    __output__.mkdir(exist_ok=True)

    __contents__ = path.read_text()
    __separator__ = "."

    file_name = name
    if not is_object:
        file_name = f"love.{name}"
    else:
        __separator__ = ":"

    __output__ /= file_name

    with open(f"{__output__}.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["Function Name", "Description"])

        matches = __FUNCTION_STR_REGEX__.findall(__contents__)

        for match in matches:
            # Skip internal functions
            if "_" in match:
                continue

            # [Name, Description]
            data = get_description(api, name, match, is_object)

            if data and data[0]:
                match = f"[{match}](https://love2d.org/wiki/{data[0]}{__separator__}{match})"

            value = ""
            if len(data) > 0:
                value = data[1]

            writer.writerow([match, value])


def collect_calls(path: Path) -> dict:
    result = dict()

    result["modules"] = dict()
    result["objects"] = dict()

    for item in path.rglob("*.cpp"):
        filepath = str(item)
        if "source" in filepath:
            if "wrap" in filepath:
                if "modules" in filepath:
                    result["modules"][item.parent.name] = item
                elif "objects" in filepath:
                    value = item.parent.name
                    if item.parent.name == "gamepad":
                        value = "joystick"

                    result["objects"][value] = item

    return result


def download_api() -> dict:
    if not __LOVE_API_JSON__.exists():
        http = urllib3.PoolManager()
        response = http.request("GET", __LOVE_API_URL__, preload_content=False)

        with __LOVE_API_JSON__.open("wb") as file:
            while True:
                data = response.read(0x200)

                if not data:
                    break

                file.write(data)

        response.release_conn()

    with __LOVE_API_JSON__.open("r") as file:
        return json.load(file)


def main():
    __parser__ = ArgumentParser()
    __parser__.add_argument("path", type=Path)

    __parsed__ = __parser__.parse_args()

    __data__ = dict()

    __api__ = download_api()

    if __parsed__.path:
        __data__ = collect_calls(__parsed__.path)
    else:
        print(f"Invalid path: {__parsed__.path}")

    for module, file in __data__["modules"].items():
        create_csv_file(__api__, module, file)

    for object, file in __data__["objects"].items():
        create_csv_file(__api__, object, file, True)


if __name__ == "__main__":
    main()
