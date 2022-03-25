import csv
from pathlib import Path

output_dir = Path("output")

with open("missing_api.txt", "w") as file:
    for filepath in output_dir.glob("*.csv"):
        with filepath.open("r") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for reader_row in reader:
                if not reader_row["Description"]:
                    file.write(
                        f"{filepath.name[:-4]} -> {reader_row['Function Name']}\n")
