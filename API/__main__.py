import json
import re
import shutil
from argparse import ArgumentParser
from pathlib import Path

import urllib3

from .classes.module import Module
from .classes.object import Object

__TYPE_VALUE_REGEX__ = re.compile(r".*::type\(\"(.*)\", &(.*).*\)")

__API_URL__ = "https://love2d-community.github.io/love-api/love-api.json"
__API_FILE__ = Path("love_api.json")

__SOURCE_PATH__ = Path("G:\GitHub\C++\lovepotion\source")


def download_api() -> dict:
    if not __API_FILE__.exists():
        http = urllib3.PoolManager()
        response = http.request("GET", __API_URL__, preload_content=False)

        with __API_FILE__.open("wb") as file:
            data = response.read(0x200)

            while data:
                file.write(data)
                data = response.read(0x200)
            else:
                response.release_conn()

    with __API_FILE__.open("r") as file:
        return json.load(file)


def get_type(supers: dict, filepath: str):
    with open(filepath, "r") as file:
        buffer = file.read()
        info = __TYPE_VALUE_REGEX__.findall(buffer)

        if len(info) > 0:
            info = info[0]

            if info[0] == "Gamepad":
                info[0] = "Joystick"

            supers[info[0].lower()] = info[1].split("::")[0]


def get_super_items(object_name: str, type_info: str) -> list:
    result = ["Object"]

    if type_info == "Drawable":
        result.append("Drawable")

    if "Joint" in type_info or "joint" in type_info:
        result.append("Joint")

    if "Shape" in type_info:
        result.append("Shape")

    if type_info == "Data" or type_info == "data":
        result.append("Data")

    if type_info == "Threadable":
        result.append("Threadable")

    if type_info == "Texture":
        result.extend(["Texture", "Drawable"])

    if type_info == "image":
        result.extend(["Texture", "Drawable"])

    if type_info != "Object" and not type_info in result:
        print(f"No type info for {type_info}")

    return result


def gather_calls(api_data: dict, source_path: Path):
    api_supers = dict()

    for item in source_path.rglob("*.cpp"):
        api_item = None
        filepath = str(item)

        if "objects" in filepath:
            if not "wrap" in item.name:
                get_type(api_supers, filepath)

        if "wrap" in item.name:
            if "modules" in filepath:
                api_item = Module(api_data, item)
            else:
                value = item.parent.name

                if value == "gamepad":
                    value = "joystick"

                supers = list()

                try:
                    supers = get_super_items(value, api_supers[value])
                except KeyError:
                    supers = get_super_items(value, value)

                api_item = Object(api_data, supers, item)

        if api_item:
            api_item.generate()


def cleanup():
    stuff = ["debug", "output"]
    for value in stuff:
        if Path(value).is_dir():
            shutil.rmtree(value)


def main():
    __parser__ = ArgumentParser()
    __parser__.add_argument("path", type=Path, default=__SOURCE_PATH__)

    __parsed__ = __parser__.parse_args()

    if __parsed__.path:
        cleanup()
        gather_calls(download_api(), __parsed__.path)
    else:
        print(f"Invalid path: {__parsed__.path}")


if __name__ == "__main__":
    main()
