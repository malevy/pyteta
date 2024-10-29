import pathlib
import os


def _convert_to_bool(s):
    return s.lower().strip() in ["true", "yes", "1"]


class Config:
    ApiKey = str(os.getenv("OPENAI_API_KEY"))
    Model = os.getenv("OPENAI_MODEL")
    SourceRoot = pathlib.Path(os.getenv("PYTETA_SOURCE_ROOT"))
    StudentRoot = pathlib.Path(os.getenv("PYTETA_STUDENT_ROOT"))
    ShowToolResponses = _convert_to_bool(os.getenv("PYTETA_SHOW_TOOL_RESPONSE"))
    ShowToolUsage = _convert_to_bool(os.getenv("PYTETA_SHOW_TOOL_USAGE"))
