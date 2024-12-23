import os
import pathlib


def find_files(root_directory, extensions: list[str], recursive: bool = False):
    available_files = (
        _find_files_recursively(root_directory, extensions=extensions)
        if recursive
        else [os.path.join(root_directory, f) for f in os.listdir(root_directory) if _get_extension(f) in extensions]
    )

    return available_files


def _find_files_recursively(root_directory, extensions: list[str]):
    available_files = []
    for root, _, files in os.walk(root_directory):
        for filename in files:
            if _get_extension(filename) in extensions:
                available_files.append(os.path.join(root, filename))
    return available_files


def _get_extension(file_name):
    # Special case for hidden files (starting with a dot)
    if file_name.startswith("."):
        return file_name
    return pathlib.Path(file_name).suffix.lower()
