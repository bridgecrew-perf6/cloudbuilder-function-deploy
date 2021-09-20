import os
import re
import shutil
from glob import glob
from argparse import ArgumentParser, RawTextHelpFormatter

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument(
    "function",
    type=str,
    metavar="function",
    help="the path of the function the target will be included into."
)
parser.add_argument(
    "to_import",
    type=str,
    metavar="to_import",
    help="the path to the 'common function' to include."
)
parser.add_argument(
    "package",
    type=str,
    metavar="package",
    help="the base package of the 'common function'.\n"
         "this part will be removed from imports in the function."
)

arguments, unknown_arguments = parser.parse_known_args()
PACKAGE = arguments.package
IMPORT_REGEX = re.compile(r"^from\s([^\s]+)\simport\s(.*)$")


def process_line(line: str) -> str:
    result = IMPORT_REGEX.search(line)
    if result:
        package = result.group(1)
        to_replace = PACKAGE + "."
        if package.startswith(to_replace):
            line = line.replace(to_replace, "")

    elif line.startswith(f"import {PACKAGE}"):
        print(line)
        line = None

    return line


def main():
    to_import = arguments.to_import
    function = arguments.function

    if not os.path.isdir(to_import):
        print(f"'{to_import}' is not a path.")
        return 1
    elif not os.path.isdir(function):
        print(f"'{function}' is not a path.")
        return 1

    for file in glob(os.path.join(function, "**/*.py"), recursive=True):
        with open(file, "r") as open_file:
            lines = open_file.readlines()

        for i, line in enumerate(lines):
            lines[i] = process_line(line)

        lines = [line for line in lines if line]

        with open(file, "w") as open_file:
            open_file.writelines(lines)

    shutil.copytree(to_import, function, dirs_exist_ok=True)

    return 0


if __name__ == "__main__":
    exit(main())
