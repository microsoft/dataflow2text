"""Processes a data tsv file in SMCalFlow-ResponseGeneration into a jsonl file
that can be used by clamp_experiments.run_constrained_decoding.

Unlike process_data.py, this script does not execute the plan to obtain the top-level execution result.
"""
import argparse
import csv
import json

import pandas as pd
from tqdm import tqdm


def main(data_tsv: str, outbase: str):
    data_df = pd.read_csv(
        data_tsv,
        sep="\t",
        encoding="utf-8",
        quoting=csv.QUOTE_ALL,
        na_values=None,
        keep_default_na=False,
    )

    output_jsonl = f"{outbase}.jsonl"
    fp = open(output_jsonl, "w")
    for _, row in tqdm(data_df.iterrows()):
        dialogue_id = row.get("dialogueId")
        turn_index = int(row.get("turnIndex"))
        lispress_str = row.get("lispress")
        agent_utterance = row.get("agentUtterance")

        processed_datum = {
            "dialogueId": dialogue_id,
            "turnIndex": turn_index,
            "input": lispress_str,
            "agentUtterance": agent_utterance,
        }
        fp.write(json.dumps(processed_datum))
        fp.write("\n")
    fp.close()


def add_arguments(argument_parser: argparse.ArgumentParser) -> None:
    argument_parser.add_argument("--data_tsv", help="The path to data tsv file.")
    argument_parser.add_argument("--outbase", help="The base name of output files.")


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(cmdline_parser)
    args = cmdline_parser.parse_args()

    main(
        data_tsv=args.data_tsv,
        outbase=args.outbase,
    )
