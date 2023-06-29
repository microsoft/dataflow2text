"""Processes a data tsv file in SMCalFlow-ResponseGeneration into a jsonl file
that can be used by clamp_experiments.run_constrained_decoding.

During the processing, we obtain the top-level execution results and serialize it as a json string.
In most cases, the top-level execution result is the value of the argument of the outermost `Yield` in the plan or
an error when the execution throws an exception.
"""
import argparse
import csv
import json
import os

import jsons
import pandas as pd
from tqdm import tqdm

import dataflow2text_domains.calflow.config
from dataflow2text.dataflow.function import BaseFunction, ExecutionError
from dataflow2text.dataflow.schema import List, Option, PrimitiveSchema
from dataflow2text_domains.calflow.dataflow_library import (
    CALFLOW_FUNCTION_LIBRARY,
    CALFLOW_SCHEMA_LIBRARY,
)
from dataflow2text_domains.calflow.experiments.lispress_to_computation import (
    lispress_str_to_computation,
)
from dataflow2text_domains.calflow.functions.calflow_yield import Yield
from dataflow2text_domains.calflow.functions.do import do


def unwrap_do(c: BaseFunction) -> BaseFunction:
    if isinstance(c, do):
        return unwrap_do(c.arg2)
    return c


def primitive_serializer(obj: PrimitiveSchema, **kwargs):
    kwargs["cls"] = type(obj.inner)
    return jsons.dump(obj.inner, **kwargs)


def option_serializer(obj: Option, **kwargs):
    kwargs["cls"] = type(obj.inner)
    return jsons.dump(obj.inner, **kwargs)


def list_serializer(obj: List, **kwargs):
    kwargs["cls"] = type(obj.inner)
    return jsons.dump(obj.inner, **kwargs)


def get_top_level_execution_result(
    dialogue_id: str, turn_index: int, lispress_str: str
) -> str:
    dataflow2text_domains.calflow.config.current_dialogue_id = dialogue_id
    dataflow2text_domains.calflow.config.current_turn_index = turn_index

    computation = lispress_str_to_computation(
        lispress_str,
        CALFLOW_SCHEMA_LIBRARY,
        CALFLOW_FUNCTION_LIBRARY,
    )

    # do(Yield(...), Yield(...))
    computation = unwrap_do(computation)
    if isinstance(computation, Yield):
        value = computation.output.__value__
    else:
        value = computation.__value__

    if isinstance(value, ExecutionError):
        return value.inner.__repr__()

    else:
        value_dict = jsons.dump(
            value,
            strip_properties=True,
        )
        result_dict = {
            "type": value.dtype.render(),
            "value": value_dict,
        }
        return json.dumps(result_dict)


def main(
    data_tsv: str, preambles_and_metas_dir: str, use_user_utterance: bool, outbase: str
):
    data_df = pd.read_csv(
        data_tsv,
        sep="\t",
        encoding="utf-8",
        quoting=csv.QUOTE_ALL,
        na_values=None,
        keep_default_na=False,
    )

    dataflow2text_domains.calflow.config.preambles_dir = os.path.join(
        preambles_and_metas_dir, "preambles"
    )
    dataflow2text_domains.calflow.config.metas_dir = os.path.join(
        preambles_and_metas_dir, "metas"
    )

    jsons.set_serializer(primitive_serializer, PrimitiveSchema)
    jsons.set_serializer(list_serializer, List)
    jsons.set_serializer(option_serializer, Option)

    output_jsonl = f"{outbase}.jsonl"
    fp = open(output_jsonl, "w")
    for _, row in tqdm(data_df.iterrows()):
        dialogue_id = row.get("dialogueId")
        turn_index = int(row.get("turnIndex"))
        lispress_str = row.get("lispress")
        agent_utterance = row.get("agentUtterance")

        result_str = get_top_level_execution_result(
            dialogue_id, turn_index, lispress_str
        )

        if use_user_utterance:
            user_utterance = row.get("userUtterance")
            input_text = (
                f"User: {user_utterance} Plan: {lispress_str} Result: {result_str}"
            )
        else:
            input_text = f"Plan: {lispress_str} Result: {result_str}"
        processed_datum = {
            "dialogueId": dialogue_id,
            "turnIndex": turn_index,
            "input": input_text,
            "agentUtterance": agent_utterance,
        }
        fp.write(json.dumps(processed_datum))
        fp.write("\n")
    fp.close()


def add_arguments(argument_parser: argparse.ArgumentParser) -> None:
    argument_parser.add_argument("--data_tsv", help="The path to data tsv file.")
    argument_parser.add_argument(
        "--preambles_and_metas_dir",
        help="The path to the folder contains preambles and metas.",
    )
    argument_parser.add_argument(
        "--use_user_utterance",
        default=False,
        action="store_true",
        help="If set, prefix with the user utterance in the input.",
    )
    argument_parser.add_argument("--outbase", help="The base name of output files.")


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(cmdline_parser)
    args = cmdline_parser.parse_args()

    main(
        data_tsv=args.data_tsv,
        preambles_and_metas_dir=args.preambles_and_metas_dir,
        use_user_utterance=args.use_user_utterance,
        outbase=args.outbase,
    )
