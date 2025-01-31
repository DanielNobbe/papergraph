from typing import BinaryIO, Optional

from typing_extensions import TypedDict
from langchain.schema import Document


class Result(TypedDict):
    metadata: dict
    key_findings: list
    methodology: str
    summary: str
    keywords: list


class State(TypedDict):
    path: Optional[str]
    item: Optional[BinaryIO]
    doc: Document
    docs: list
    chunk_size: int
    chunk_overlap: int
    result: Result


def get_filepath_input_state(path: str) -> State:
    state = State()
    state["result"] = Result()  # may stay empty

    state["path"] = path

    state["chunk_size"] = 90000  # mistral large has 130k context window
    state["chunk_overlap"] = 1000

    return state


def get_iofile_input_state(item: BinaryIO) -> State:
    state = State()
    state["result"] = Result()  # may stay empty

    state["item"] = item
    return state
