from pathlib import Path

from API.classes.module import Module
from API.classes.object import Object
from mdtable import MDTable

from .api import API


class Page:

    TemplateModule = Path("data/template_module.md")
    TemplateTypes = Path("data/template_types.md")

    def __init__(self, api_items: list):
        with open(str(Page.TemplateModule), "r") as file:
            self.template_module = file.read()

        with open(str(Page.TemplateTypes), "r") as file:
            self.template_types = file.read()

        self.data = dict()
        for item in api_items:
            if type(item) is Module:
                module_name = item.get_name()
                if not module_name in self.data:
                    self.data[module_name] = {"module": item, "types": list()}

            if type(item) is Object:
                self.data[item.get_module()]["types"].append(item)

        self.get_output_dir().mkdir()

        for module, data in self.data.items():
            self.generate_file(module, data)

    def bullet_points(self, items: list):
        result = ""
        for item in items:
            result += f"- {item}\n"

        return result

    def generate_file(self, module: str, data: dict):
        markdown = MDTable(data["module"].get_output_path())
        description = data["module"].get_description()
        self.name = module

        buffer_data = self.template_module.format(
            module_name=module.capitalize(), module_desc=description, csv_table_funcs=markdown.get_table())

        types_data = ""

        for type in data["types"]:
            description = type.get_description()
            supers = type.get_supers()
            markdown = MDTable(type.get_output_path())

            types_data += self.template_types.format(
                type_name=type.get_name().capitalize(), type_desc=description, super_types=self.bullet_points(supers), csv_table_types=markdown.get_table())

        buffer_data += f"{types_data}\n\n"

        with open(self.get_output_path(), "w") as output:
            print(buffer_data, file=output)

    def get_output_dir(self) -> Path:
        return API.__OUTPUT_FOLDER__ / "pages"

    def get_filename(self) -> str:
        return f"love.{self.name}.md"

    def get_output_path(self) -> str:
        return self.get_output_dir() / self.get_filename()
