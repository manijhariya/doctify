import argparse
import sys
from pathlib import Path

from src.doctify import main as doctify_main
from src.logger import doctify_logger

parser = argparse.ArgumentParser(
        prog="doctify",
        description="Generate docstring for any file and repo",
        epilog="Thanks for using %(prog)s! :)",
    )

parser.add_argument(
    "directory",
    help="Specify the directory path to generate docstrings for all files.",
    nargs="?",
)
parser.add_argument(
    "-f",
    "--file",
    required=False,
    help="Specify the file path to generate docstrings for this file.",
)
parser.add_argument(
    "-p",
    "--path",
    required=False,
    help="Specify the directory path to generate docstrings for all files.",
)

parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
parsed_args = parser.parse_args()


def main():
    if parsed_args.file:
        target_file = Path(parsed_args.file)

        if not target_file.exists():
            doctify_logger.error("The target file doesn't exist")
            raise SystemExit(1)
        else:
            doctify_logger.info(f"working on {target_file.absolute()}")
            doctify_main(filepath=target_file)

    elif parsed_args.path:
        target_path = Path(parsed_args.path)

        if not target_path.exists():
            doctify_logger.error("The target path doesn't exist")
            raise SystemExit(1)
        else:
            doctify_logger.info(f"working on {target_path.absolute()}")
            doctify_main(path=target_path.absolute())

    elif parsed_args.directory:
        target_dir = Path(parsed_args.directory)

        if not target_dir.exists():
            doctify_logger.error("The target directory doesn't exist")
            raise SystemExit(1)
        else:
            doctify_logger.info(f"working on {target_dir.absolute()}")
            doctify_main(path=target_dir.absolute())
    else:
        doctify_logger.error("Please specify at least one argument or -h for help.")
        raise SystemExit(1)
