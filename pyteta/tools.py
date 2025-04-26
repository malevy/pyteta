import pathlib
import shutil

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from config import ConfigKeys

_SOURCE_PLACEHOLDER_ROOT = pathlib.Path("SOURCE/")
_STUDENT_PLACEHOLDER_ROOT = pathlib.Path("STUDENT/")


def _make_real_path(placeHolderRoot, newRoot, fakePath):
    relativePortion = fakePath.relative_to(placeHolderRoot)
    return newRoot.joinpath(relativePortion)


def _path_start_with(path, start):
    return path.is_relative_to(start)


@tool
def list_files(folder_spec: str, config: RunnableConfig):
    """
    list the contents of a given folder

    Args:
        folder_spec (str): path to the folder of interest
        config (RunnableConfig): the configuration

    Returns:
        a dictionary with the following keys:
            status (str): "success" or "error"
            message (str): an error or success message
            folder_spec (str): the path to the folder of interest
            files (list): a list of files in the folder
            folders (list): a list of folders in the folder
    """
    folder = pathlib.Path(folder_spec)

    real_folder = None
    if _path_start_with(folder, _SOURCE_PLACEHOLDER_ROOT):
        real_folder = _make_real_path(
            _SOURCE_PLACEHOLDER_ROOT, config["configurable"][ConfigKeys.source_root], folder
        )
    elif _path_start_with(folder, _STUDENT_PLACEHOLDER_ROOT):
        real_folder = _make_real_path(
            _STUDENT_PLACEHOLDER_ROOT, config["configurable"][ConfigKeys.student_root], folder
        )
    else:
        return {
            "status": "error",
            "message": f"folder_spec does not start with {_SOURCE_PLACEHOLDER_ROOT} or {_STUDENT_PLACEHOLDER_ROOT}",
        }

    if not real_folder.exists():
        return {"status": "error", "message": f"{folder} does not exist"}

    response = {
        "status": "success",
        "folder_spec": f"{folder}",
        "files": [],
        "folders": [],
    }

    try:
        for item in real_folder.iterdir():
            if item.is_file():
                response["files"].append(item.name)
            elif item.is_dir():
                response["folders"].append(item.name)
        return response
    except OSError as e:
        return {"status": "error", "message": f"{e.strerror}"}


@tool
def create_folder(folder_spec: str, config: RunnableConfig):
    """
    Creates a folder by creating all nonexistent parent folders first.

    Args:
        folder_spec (str): the path and name of the new folder
        config (RunnableConfig): the configuration

    Returns:
        a dictionary with the following keys:
            status (str): "success" or "error"
            message (str): an error or success message
            folder_spec (str): the path to the folder of interest
    """

    folder = pathlib.Path(folder_spec)

    if not _path_start_with(folder, _STUDENT_PLACEHOLDER_ROOT):
        return {
            "status": "error",
            "message": f"the new folder should be a within {_STUDENT_PLACEHOLDER_ROOT}",
        }

    folder_to_create = _make_real_path(
        _STUDENT_PLACEHOLDER_ROOT, config["configurable"][ConfigKeys.student_root], folder
    )

    try:
        folder_to_create.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return {"status": "error", "message": f"{e.strerror}"}

    return {
        "status": "success",
        "folder_spec": f"{folder}",
        "message": "folder was created successfully",
    }


@tool
def copy_folder(source_spec: str, dest_spec: str, config: RunnableConfig):
    """
    Recursively copies an entire folder to a new folder.

    Args:
        source_spec (str): path to the folder containing the items to copy
        dest_spec (str): path to the destination folder
        config (RunnableConfig): the configuration

    Returns:
        a dictionary with the following keys:
            status (str): "success" or "error"
            message (str): an error or success message
    """
    source = pathlib.Path(source_spec)
    dest = pathlib.Path(dest_spec)

    real_source = None
    if _path_start_with(source, _SOURCE_PLACEHOLDER_ROOT):
        real_source = _make_real_path(
            _SOURCE_PLACEHOLDER_ROOT, config["configurable"][ConfigKeys.source_root], source
        )
    elif _path_start_with(source, _STUDENT_PLACEHOLDER_ROOT):
        real_source = _make_real_path(
            _STUDENT_PLACEHOLDER_ROOT, config["configurable"][ConfigKeys.student_root], source
        )
    else:
        return {
            "status": "error",
            "message": f"source_spec does not start with {_SOURCE_PLACEHOLDER_ROOT} or {_STUDENT_PLACEHOLDER_ROOT}",
        }

    if not _path_start_with(dest, _STUDENT_PLACEHOLDER_ROOT):
        return {
            "status": "error",
            "message": f"dest_spec must be within {_STUDENT_PLACEHOLDER_ROOT}",
        }
    real_dest = _make_real_path(_STUDENT_PLACEHOLDER_ROOT, config["configurable"][ConfigKeys.student_root], dest)

    try:
        shutil.copytree(real_source, real_dest, dirs_exist_ok=True)

        return {"status": "success", "message": "folder was copied successfully"}
    except shutil.Error as e:
        return {"status": "error", "message": f"{e.exception}"}
    except FileNotFoundError as nf:
        return {"status": "error", "message": f"{nf.strerror}"}
    except FileExistsError as fe:
        return {"status": "error", "message": f"{fe.strerror}"}
