import os
import re
import shutil
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument(
    "--function",
    type=Path,
    metavar="function",
    default=Path("."),
    help="the path of the function to import into."
)
parser.add_argument(
    "--common",
    type=Path,
    metavar="common",
    default=Path("../common"),
    help="the path to the directory containing the common files."
)
parser.add_argument(
    "--common-package",
    type=str,
    metavar="common_package",
    default="functions.common",
    help="the base package of the 'common function'.\n"
         "this part will be replaced with the function_package."
)
parser.add_argument(
    "--function-package",
    type=str,
    metavar="function_package",
    required=False,
    help="the base package of the function.\n"
         "this part will replace the common_package."
)

arguments, unknown_arguments = parser.parse_known_args()

if not os.path.exists(arguments.common) or not os.path.isdir(arguments.common):
    print(f"'{arguments.common}' is not a valid directory.")
    exit(1)

if not os.path.exists(arguments.function) or not os.path.isdir(arguments.function):
    print(f"'{arguments.function}' is not a valid directory.")
    exit(1)

if arguments.function_package:
    FUNCTION_PACKAGE = arguments.function_package
elif arguments.common.name in arguments.common_package:
    FUNCTION_PACKAGE = arguments.common_package.replace(
        arguments.common.resolve().name,
        arguments.function.resolve().name
    )
else:
    print(
        "Could not resolve function_package from common_package.\n"
        "Please check common_package, or consider specifying --function-package"
    )
    exit(1)

COMMON_PACKAGE = arguments.common_package

IMPORT_REGEX = re.compile(r"^(?:from|import)\s([^\s]+)(?:\simport\s.+)?$")


def process_line(line: str) -> str:
    result = IMPORT_REGEX.search(line)
    if result:
        package = result.group(1)
        if package.startswith(COMMON_PACKAGE):
            line = line.replace(COMMON_PACKAGE, FUNCTION_PACKAGE)

    return line


def main():
    for file in arguments.function.glob("**/*.py"):
        with open(file, "r") as open_file:
            lines = open_file.readlines()

        for i, line in enumerate(lines):
            lines[i] = process_line(line)

        lines = [line for line in lines if line]

        with open(file, "w") as open_file:
            open_file.writelines(lines)

    shutil.copytree(str(arguments.common), str(arguments.function), dirs_exist_ok=True)

    return 0


if __name__ == "__main__":
    exit(main())
