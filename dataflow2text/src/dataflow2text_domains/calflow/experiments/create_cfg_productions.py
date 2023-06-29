import argparse
import csv
import os
from pathlib import Path
from typing import Set

import pandas as pd
from more_itertools import peekable
from tqdm import tqdm

import dataflow2text_domains.calflow.config
from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.dataflow_transducer import DataflowTransducer
from dataflow2text.generation.generation_production import (
    GenerationProduction,
    render_generation_production,
)
from dataflow2text.generation.generation_symbol import (
    GenerationNonterminal,
    render_generation_symbol,
)
from dataflow2text.generation.simple_generation_parser import SimpleGenerationParser
from dataflow2text_domains.calflow.dataflow_library import (
    CALFLOW_FUNCTION_LIBRARY,
    CALFLOW_GENERATION_RULES,
    CALFLOW_LIBRARY,
    CALFLOW_SCHEMA_LIBRARY,
)
from dataflow2text_domains.calflow.experiments.computation_to_lispress import (
    computation_to_lispress_str,
)
from dataflow2text_domains.calflow.experiments.lispress_to_computation import (
    lispress_str_to_computation,
)

# Hard-coded start symbol used by CLAMP.
CLAMP_START_SYMBOL = "start"


def render_root_production(computation: BaseFunction) -> str:
    root_symbol = GenerationNonterminal(act=DEFAULT_ACT, computation=computation)
    return f"{CLAMP_START_SYMBOL} -> {render_generation_symbol(root_symbol)}"


def check_gold_reachability(
    allowed_rules: Set[str], gold: str, computation: BaseFunction
) -> bool:
    parser = SimpleGenerationParser(
        CALFLOW_LIBRARY,
        [r for r in CALFLOW_GENERATION_RULES if r.name in allowed_rules],
    )
    trees = peekable(parser.parse(computation, gold))
    return bool(trees)


def main(
    data_tsv: str,
    preambles_and_metas_dir: str,
    outdir: str,
):
    transducer = DataflowTransducer(CALFLOW_LIBRARY, CALFLOW_GENERATION_RULES)
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

    if not os.path.exists(outdir):
        Path(outdir).mkdir(parents=True, exist_ok=True)

    gold_unreachable = 0
    gold_unreachable_tsv_fp = open(
        os.path.join(outdir, "unreachable_gold_ids.tsv"), "w"
    )
    gold_unreachable_tsv_fp.write("dialogueId\tturnIndex\n")

    gold_reachable = 0
    gold_reachable_tsv_fp = open(os.path.join(outdir, "reachable_gold_ids.tsv"), "w")
    gold_reachable_tsv_fp.write("dialogueId\tturnIndex\n")

    all_tsv_fp = open(os.path.join(outdir, "all_ids.tsv"), "w")  # dialogueId_turnIndex

    pbar = tqdm(
        data_df.iterrows(),
        postfix={
            "Reachable gold": gold_reachable,
            "Unreachable gold": gold_unreachable,
        },
    )
    for _, row in pbar:
        dialogue_id = row.get("dialogueId")
        turn_index = row.get("turnIndex")
        lispress_str = row.get("lispress")

        dataflow2text_domains.calflow.config.current_dialogue_id = dialogue_id
        dataflow2text_domains.calflow.config.current_turn_index = turn_index

        computation = lispress_str_to_computation(
            lispress_str, CALFLOW_SCHEMA_LIBRARY, CALFLOW_FUNCTION_LIBRARY
        )

        # Validate that the computation can be converted back to the same lispress str.
        # This is redundant, but it is a good sanity check.
        recovered_lispress_str = computation_to_lispress_str(
            computation, fully_typed=False
        )
        assert recovered_lispress_str == lispress_str

        productions = transducer.generate(computation)
        seen_productions: Set[str] = set()
        seen_rules: Set[str] = set()
        production: GenerationProduction
        # We skip the root (which is S).
        # We do not skip the first-level child since it can be either unwrapping `Yield` or `do`.
        for production in productions:
            production_str = render_generation_production(production)
            if production_str in seen_productions:
                continue
            seen_productions.add(production_str)
            seen_rules.add(production.name)

        dir_scfg_file = os.path.join(outdir, f"{dialogue_id}_{turn_index}")
        Path(dir_scfg_file).mkdir(parents=True, exist_ok=True)
        ext = ".cfg"
        path_to_scfg_file = os.path.join(dir_scfg_file, "grammar" + ext)
        fp = open(path_to_scfg_file, "w")

        fp.write(render_root_production(computation))
        fp.write("\n")

        for production_str in sorted(seen_productions):
            fp.write(production_str)
            fp.write("\n")
        fp.close()

        if check_gold_reachability(seen_rules, row.get("agentUtterance"), computation):
            gold_reachable += 1
            gold_reachable_tsv_fp.write(f"{dialogue_id}\t{turn_index}\n")
        else:
            gold_unreachable += 1
            gold_unreachable_tsv_fp.write(f"{dialogue_id}\t{turn_index}\n")
        all_tsv_fp.write(f"{dialogue_id}_{turn_index}\n")

        pbar.set_postfix(
            {"Reachable gold": gold_reachable, "Unreachable gold": gold_unreachable}
        )

    gold_unreachable_tsv_fp.close()
    gold_reachable_tsv_fp.close()

    print("Gold unreachable:", gold_unreachable)
    print("Gold reachable:", gold_reachable)


def add_arguments(argument_parser: argparse.ArgumentParser) -> None:
    argument_parser.add_argument(
        "--data_tsv", help="The data (with computation) tsv file."
    )
    argument_parser.add_argument(
        "--preambles_and_metas_dir",
        help="The path to the folder contains preambles and metas.",
    )
    argument_parser.add_argument("--outdir", help="The output directory")


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(cmdline_parser)
    args = cmdline_parser.parse_args()

    main(
        data_tsv=args.data_tsv,
        preambles_and_metas_dir=args.preambles_and_metas_dir,
        outdir=args.outdir,
    )
