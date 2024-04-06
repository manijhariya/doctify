import os
import re
from pathlib import Path
from typing import Optional

import git
import jsonlines
import pandas

from constants import Language
from logger import doctify_logger
from treesitter import Treesitter, TreesitterMethodNode


class Scarper:
    def __init__(self, repo_url, save_path):
        self.repo_url = repo_url
        self.repo_save_path = save_path
        self.repo_save_path += self.repo_url.split("/")[4]
        self.ignores = [".git"]

    def download_repo(self):
        doctify_logger.info(f"Cloning {self.repo_url} into {self.repo_save_path}")
        git.Repo.clone_from(self.repo_url, self.repo_save_path)

    def scrape_function_docstring(self):
        all_method_comments = []
        for filename in self.filenames:
            if not filename:
                continue

            with open(filename, "r") as file_content:
                file_bytes = file_content.read().encode()

            treesitter_parser = Treesitter.create_treesitter(Language.PYTHON)
            treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
                file_bytes
            )

            for node in treesitterNodes:
                method_name = node.name
                source_code, docstring = self.__clean_code__(
                    node.method_source_code, node.doc_comment
                )

                if not docstring:
                    doctify_logger.warning(
                        f"{filename} -> {method_name} has no valid doc_comment"
                    )
                    continue

                if not source_code:
                    doctify_logger.warning(
                        f"{filename} -> {method_name} has no source code"
                    )
                    continue

                all_method_comments.append(
                    {
                        "filaname": str(filename),
                        "method_name": method_name,
                        "code": source_code,
                        "docstring": docstring,
                    }
                )
        return all_method_comments

    def run(self):
        self.download_repo()
        self.all_file_paths = []
        complete_filenames = []
        for dirpath, dirnames, filenames in os.walk(self.repo_save_path):
            if dirpath in self.ignores:
                continue

            complete_filenames.extend(
                list(
                    map(
                        lambda x: (
                            Path(dirpath) / x
                            if os.path.splitext(x)[-1] == ".py"
                            else None
                        ),
                        filenames,
                    )
                )
            )

        self.filenames = set(complete_filenames)
        doctify_logger.info(
            f"{self.repo_save_path} repo has {len(self.filenames)} files"
        )
        self.all_method_comments = self.scrape_function_docstring()

    def __clean_code__(self, source_code, docstring):
        if not docstring:
            return None, None
        source_code = source_code.replace(docstring, "")
        docstring = docstring.replace('"', "")
        docstring = docstring.replace("'", "")
        return source_code, docstring  # re.sub('\s+', ' ', source_code)

    def __save_as_jsonl__(self, data_save_path):
        with jsonlines.open(data_save_path, mode="w") as writer:
            writer.write_all(self.all_method_comments)

    def __save_as_csv__(self, data_save_path):
        pass

    def save_data(self, data_save_path, filetype: Optional[str] = None):
        os.makedirs(data_save_path, exist_ok=True)

        filepath = (
            Path(data_save_path) / f"docstrings_{self.repo_save_path.split('/')[-1]}"
        )
        if filetype and filetype == "csv":
            filepath = filepath.with_suffix(".csv")
            self.__save_as_csv__(filepath)
        else:
            filepath = filepath.with_suffix(".jsonl")
            self.__save_as_jsonl__(filepath)


if __name__ == "__main__":
    repos = [
        "https://github.com/numpy/numpy",
        "https://github.com/scikit-learn/scikit-learn",
        "https://github.com/scipy/scipy",
        "https://github.com/pandas-dev/pandas",
    ]

    for repo in repos:
        s = Scarper(repo, "./data/raw/")
        s.run()
        s.save_data("data/processed/")

