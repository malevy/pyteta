import pathlib
import shutil
import os
from config import Config

_SOURCE_PLACEHOLDER_ROOT = pathlib.Path("SOURCE/")
_STUDENT_PLACEHOLDER_ROOT = pathlib.Path("STUDENT/")

tool_descriptions = [
    {
        "type": "function",
        "function": {
            "name": "ListFiles",
            "description": "list the contents of a given folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "folderspec": {
                        "type": "string",
                        "description": "the path to the folder of interest. e.q. SOURCE/",
                    }
                },
                "required": ["folderspec"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "CreateFolder",
            "description": "Creates a folder by creating all nonexistent parent folders first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folderspec": {
                        "type": "string",
                        "description": "the path to the folder to create. e.q. STUDENT/",
                    }
                },
                "required": ["folderspec"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "CopyFolder",
            "description": "Recursively copies an entire folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sourcespec": {
                        "type": "string",
                        "description": "the path to the source of the items to copy. e.q. SOURCE/",
                    },
                    "destspec": {
                        "type": "string",
                        "description": "the path to the destination folder. e.q. STUDENT/",
                    },
                },
                "required": ["sourcespec", "destspec"],
            },
        },
    },
]


def _make_real_path(placeHolderRoot, newRoot, fakePath):
    relativePortion = fakePath.relative_to(placeHolderRoot)
    return newRoot.joinpath(relativePortion)


def _path_start_with(path, start):
    return path.is_relative_to(start)


def list_files(params, config=Config):
    folder = pathlib.Path(params["folderspec"])

    real_folder = None
    if _path_start_with(folder, _SOURCE_PLACEHOLDER_ROOT):
        real_folder = _make_real_path(
            _SOURCE_PLACEHOLDER_ROOT, config.SourceRoot, folder
        )
    elif _path_start_with(folder, _STUDENT_PLACEHOLDER_ROOT):
        real_folder = _make_real_path(
            _STUDENT_PLACEHOLDER_ROOT, config.StudentRoot, folder
        )
    else:
        return {
            "status": "error",
            "message": f"folderspec does not start with {_SOURCE_PLACEHOLDER_ROOT} or {_STUDENT_PLACEHOLDER_ROOT}",
        }

    if not real_folder.exists():
        return {"status": "error", "message": f"{folder} does not exist"}

    response = {
        "status": "success",
        "folderSpec": f"{folder}",
        "files": [],
        "folders": [],
    }

    for item in real_folder.iterdir():
        if item.is_file():
            response["files"].append(item.name)
        elif item.is_dir():
            response["folders"].append(item.name)

    return response


def create_folder(params, config=Config):
    folder = pathlib.Path(params["folderspec"])

    if not _path_start_with(folder, _STUDENT_PLACEHOLDER_ROOT):
        return {
            "status": "error",
            "message": f"the new folder should be a within {_STUDENT_PLACEHOLDER_ROOT}",
        }

    folder_to_create = _make_real_path(
        _STUDENT_PLACEHOLDER_ROOT, config.StudentRoot, folder
    )
    folder_to_create.mkdir(parents=True, exist_ok=True)

    return {
        "status": "success",
        "folderSpec": f"{folder}",
        "message": "folder was created successfully",
    }


def copy_folder(params, config=Config):
    source = pathlib.Path(params["sourcespec"])
    dest = pathlib.Path(params["destspec"])

    real_source = None
    if _path_start_with(source, _SOURCE_PLACEHOLDER_ROOT):
        real_source = _make_real_path(
            _SOURCE_PLACEHOLDER_ROOT, config.SourceRoot, source
        )
    elif _path_start_with(source, _STUDENT_PLACEHOLDER_ROOT):
        real_source = _make_real_path(
            _STUDENT_PLACEHOLDER_ROOT, config.StudentRoot, source
        )
    else:
        return {
            "status": "error",
            "message": f"sourcespec does not start with {_SOURCE_PLACEHOLDER_ROOT} or {_STUDENT_PLACEHOLDER_ROOT}",
        }

    if not _path_start_with(dest, _STUDENT_PLACEHOLDER_ROOT):
        return {
            "status": "error",
            "message": f"destspec must be within {_STUDENT_PLACEHOLDER_ROOT}",
        }
    real_dest = _make_real_path(_STUDENT_PLACEHOLDER_ROOT, config.StudentRoot, dest)

    shutil.copytree(real_source, real_dest, dirs_exist_ok=True)

    return {"status": "success", "message": "folder was copied successfully"}
