import pathlib
import os


def _convert_to_bool(s):
    return s.lower().strip() in ["true", "yes", "1"]


class Config:
    model = os.getenv("OPENAI_MODEL")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.0))
    source_root = pathlib.Path(os.getenv("PYTETA_SOURCE_ROOT"))
    student_root = pathlib.Path(os.getenv("PYTETA_STUDENT_ROOT"))
    show_tool_responses = _convert_to_bool(os.getenv("PYTETA_SHOW_TOOL_RESPONSE"))


class ConfigKeys:
    model = "model"
    temperature = "temperature"
    source_root = "source_root"
    student_root = "student_root"
    show_tool_responses = "show_tool_responses"
