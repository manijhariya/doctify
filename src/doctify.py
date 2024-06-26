import os
import re
from pathlib import Path
from typing import Dict

from src.constants import Language
from src.inference import Inference
from src.logger import doctify_logger
from src.treesitter import Treesitter, TreesitterMethodNode

model_name = "manijhriya/phi2-doctify"
inference = Inference(model_name)

RE_FUNCTION_DEF = re.compile(r"((\n|.)*?:\n)")
RE_FUNCTION_INDENTATION = re.compile(r"^(\s*)")


def get_updated_code(docstring_content: Dict[str, str]) -> str:
    """
    Update the docstring with the docstring content.

    Parameters
    ----------
    docstring_content : Dict[str, str]
        The docstring content.

    Returns
    -------
    str
        The updated docstring.

    Raises
    ------
    Exception
        If the docstring cannot be updated.
    """
    original_code = docstring_content["original_code"]
    docstring = docstring_content["generated_docstring"]
    try:
        function_def = RE_FUNCTION_DEF.findall(original_code)[0][0]
        function_body = original_code.replace(function_def, "")
        indentation = " " * len(RE_FUNCTION_INDENTATION.findall(function_body)[0])
        return (
            function_def
            + f'{indentation}"""\n{indentation}'
            + docstring
            + f'\n{indentation}"""\n'
            + function_body
        )
    except Exception as err:
        doctify_logger.error(
            f"{docstring_content['filepath']} -> {docstring_content['method_name']} -> Error while reading file for writing docstring skipping... \t Error : {err}"
        )


def write_docsstring_to_file(docstring_content: Dict[str, str]):
    """
    Write docstring to file.

    Parameters
    ----------
    docstring_content : dict
        Dictionary containing the filepath, method_name and the docstring content.
    """
    doctify_logger.info(
        f"{docstring_content['filepath']} -> {docstring_content['method_name']} Writing docstring..."
    )
    try:
        with open(docstring_content["filepath"], "r", encoding="utf-8") as file:
            file_content = file.read()

    except Exception as err:
        doctify_logger.error(
            f"{docstring_content['filepath']} -> {docstring_content['method_name']} -> Error while reading file for writing docstring skipping... \t Error : {err}"
        )
        return

    start_pos = file_content.find(docstring_content["original_code"])
    updated_code = get_updated_code(docstring_content)
    if updated_code and start_pos != -1:
        end_pos = start_pos + len(docstring_content["original_code"])
        modified_lines = updated_code.split("\n")
        indented_modified_code = "\n".join(modified_lines)
        modified_content = (
            file_content[:start_pos] + indented_modified_code + file_content[end_pos:]
        )

        try:
            with open(docstring_content["filepath"], "w", encoding="utf-8") as file:
                file.write(modified_content)

        except Exception as err:
            doctify_logger.error(
                f"{docstring_content['filepath']} -> {docstring_content['method_name']} -> Error while writing to file for writing docstring skipping... \t Error : {err}"
            )
            return


def generate_docstring_for_file(filepath: Path):
    """
    Generate docstring for all files in the directory.

    Parameters
    ----------
    filepath : Path
        Path to the directory containing the files to be processed.
    """
    docstring_contents = []

    try:
        with open(filepath, "r") as file_content:
            file_bytes = file_content.read().encode()

    except Exception as err:
        doctify_logger.error(
            f"{filepath} -> Error while reading file skipping... \t Error : {err}"
        )
        return

    treesitter_parser = Treesitter.create_treesitter(Language.PYTHON)

    try:
        treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
            file_bytes
        )
    except Exception as err:
        doctify_logger.error(
            f"{filepath} -> Error while Parsing this file skipping... \t Error : {err}"
        )
        return

    for node in treesitterNodes:
        if node.doc_comment:
            doctify_logger.warning(
                f"{filepath} -> {node.name} -> already has docstring skipping... "
            )
            continue

        doctify_logger.info(f"{filepath} -> {node.name} -> Generating docstring...")

        try:
            docstring = inference.generate_docstring(node.method_source_code)
        except Exception as err:
            doctify_logger.error(
                f"{filepath} -> {node.name} -> Error while generating docstring skipping... \t Error : {err}"
            )
            return ""

        docstring_contents.append(
            {
                "filepath": filepath,
                "method_name": node.name,
                "original_code": node.method_source_code,
                "generated_docstring": docstring,
            }
        )

    list(map(write_docsstring_to_file, docstring_contents))


def generate_docstring_for_directory(start_dir: Path):
    """
    Generate docstring for all.py files in a directory.

        Parameters
        ----------
        start_dir : Path
            The directory to start the recursion.
    """
    if not isinstance(start_dir, Path):
        raise ValueError("start directory is not a Path object.")

    doctify_logger.info(f"Working on {str(start_dir.cwd())}")
    complete_filenames = []
    for dirpath, dirnames, filenames in os.walk(start_dir):
        complete_filenames.extend(
            list(
                map(
                    lambda x: (
                        Path(dirpath) / x if os.path.splitext(x)[-1] == ".py" else None
                    ),
                    filenames,
                )
            )
        )

    filenames = list(set(complete_filenames))
    doctify_logger.info(f"{len(filenames)} Files needs to be documented..")
    for filename in filenames:
        generate_docstring_for_file(filename)


def main(*args, **kwargs):
    """
    Generate docstrings for all files in the given directory.

    Parameters
    ----------
    filepath : str, optional
        Path to the file to generate docstrings for.
    path : str, optional
        Path to the directory to generate docstrings for.
    """
    if filepath := kwargs.get("filepath"):
        generate_docstring_for_file(filepath)

    elif path := kwargs.get("path"):
        generate_docstring_for_directory(path)

    else:
        doctify_logger.error("Nothing to work with exiting..")
        SystemExit(1)
