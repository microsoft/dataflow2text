"""This file contains helper methods for retrieving execution context.

These methods are needed for implementations of dataflow2text_domains.calflow.functions.
"""
import json
import os
from typing import Any, Dict

import dataflow2text_domains.calflow.config
from dataflow2text_domains.calflow.errors.preamble_errors import (
    MissingPreambleError,
    MissingTimestampError,
)
from dataflow2text_domains.calflow.schemas.date_time import DateTime


def get_preamble(dialogue_id: str) -> Dict[str, Any]:
    path_to_preamble_json = os.path.join(
        dataflow2text_domains.calflow.config.preambles_dir,
        f"{dialogue_id}.json",
    )
    if not os.path.exists(path_to_preamble_json):
        raise MissingPreambleError(dialogue_id)
    with open(path_to_preamble_json) as fp:
        preamble = json.load(fp)
    return preamble


def get_datetime(dialogue_id: str, turn_index: int) -> DateTime:
    path_to_meta_json = os.path.join(
        dataflow2text_domains.calflow.config.metas_dir, f"{dialogue_id}.json"
    )
    if not os.path.exists(path_to_meta_json):
        raise MissingTimestampError(dialogue_id, turn_index)

    with open(path_to_meta_json) as fp:
        meta = json.load(fp)

    assert meta["id"] == dialogue_id

    # the first item in meta["turns"] is always the session start event
    assert meta["turns"][0]["parts"][0]["event"]["eventType"] == "Session Start"
    # turn_index is 0-based, so we need to offset by 1.
    turn = meta["turns"][turn_index + 1]
    event = turn["parts"][0]["event"]
    timestamp = event["value"]["underlyingJson"]["underlying"]["timeStamp"]

    return DateTime.from_typed_json(timestamp)


def get_current_datetime() -> DateTime:
    return get_datetime(
        dataflow2text_domains.calflow.config.current_dialogue_id,
        dataflow2text_domains.calflow.config.current_turn_index,
    )
