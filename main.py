import csv
import re
from argparse import ArgumentParser
from pathlib import Path

from bs4 import BeautifulSoup

__FUNCTION_STR_REGEX__ = re.compile(".*\{.*\"(.*)\".*Wrap.*")

__WIKI_CONTENT__ = None
with open("api.htm", "r") as wiki:
    __WIKI_CONTENT__ = BeautifulSoup(wiki.read(), features="html5lib")

__WIKI_DIVS__ = __WIKI_CONTENT__.find_all("div", class_="function_section")


def get_description(obj: str, method: str) -> list | None:
    find = f"{obj}_{method}"
    print(f"Grabbing info for {find}..")

    data = list()

    # This is definitely not the most optimal thing
    # You basically HAVE to iterate MOST if not ALL divs before matching
    # The whole thing bout selecting what I needed didn't work, sadly

    for root in __WIKI_DIVS__:
        if find.lower() == root.find("a")["name"].lower():
            description = root.find("p", class_="description")

            data.append(description.getText().replace(
                "\n", "").strip().replace("\"", ""))
            data.append(root.find("a")["name"].split("_")[0])
            break

    return data


def create_csv_file(name: str, path: Path, is_object=False):
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

            data = get_description(name, match)

            if data and data[1]:
                match = f"[{match}](https://love2d.org/wiki/{data[1]}{__separator__}{match})"

            value = ""
            if len(data) > 0:
                value = data[0]

            writer.writerow([match, value])


def main():
    __parser__ = ArgumentParser()
    __parser__.add_argument("path")

    __parsed__ = __parser__.parse_args()

    __modules__ = dict()
    __objects__ = dict()

    if __parsed__.path:
        __filepath__ = Path(__parsed__.path)

        for item in __filepath__.rglob("*.cpp"):
            filepath = str(item)
            if "source" in filepath:
                if "wrap" in filepath:
                    if "modules" in filepath:
                        __modules__[item.parent.name] = item
                    elif "objects" in filepath:
                        __objects__[item.parent.name] = item
    else:
        print(f"Invalid path: {__parsed__.path}")

    for module, file in __modules__.items():
        create_csv_file(module, file)

    for object, file in __objects__.items():
        create_csv_file(object, file, True)


if __name__ == "__main__":
    main()
