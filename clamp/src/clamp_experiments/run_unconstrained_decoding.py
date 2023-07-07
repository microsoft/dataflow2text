# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import torch
from tqdm import tqdm

from clamp.decoding.null_partial_parse import NullPartialParse
from clamp.search.datum import DatumSub, FullDatum
from clamp_experiments.codet5_model_config import CodeT5ModelConfig
from clamp_experiments.eval_metrics import Metric, TopKExactMatch
from clamp_experiments.experiment import Experiment, run_experiment
from clamp_experiments.io_utils import load_data_from_json_file
from clamp_experiments.run_constrained_decoding import (
    build_lm_and_tokenizer,
    make_semantic_parser,
)


def _partial_parse_builder(datum: DatumSub):
    return NullPartialParse()


def create_experiments(
    model_config: CodeT5ModelConfig,
    train_data_jsonl: str,
    eval_data_jsonl: str,
    max_num_experiments: int,
) -> List[Tuple[str, Experiment]]:
    print(f"Reading {eval_data_jsonl}")
    eval_data = load_data_from_json_file(eval_data_jsonl)
    print(f"len(eval_data) = {len(eval_data)}")
    if max_num_experiments > 0:
        eval_data = eval_data[:max_num_experiments]
        print(f"len(eval_data) = {len(eval_data)}")

    lm, _tokenizer, max_steps_fn = build_lm_and_tokenizer(
        model_config, train_data_jsonl
    )
    beam_size = 5
    metrics: Dict[str, Metric[Sequence[str], FullDatum]] = {
        "exact_match": TopKExactMatch(beam_size)
    }

    experiments = []
    for datum in tqdm(eval_data):
        datum_id = f"{datum.dialogue_id}_{datum.turn_index}"
        print(f"Creating experiment for {datum_id}")

        parser = make_semantic_parser(
            lm=lm,
            beam_size=beam_size,
            partial_parse_builder=_partial_parse_builder,
            max_steps_fn=max_steps_fn,
            keep_finished_nodes=True,
        )
        experiment = Experiment(
            model=parser, client=lm, test_data=[datum], metrics=metrics
        )
        experiments.append((datum_id, experiment))

    return experiments


def main(
    model_loc: str,
    train_data_jsonl: str,
    eval_data_jsonl: str,
    max_num_experiments: int,
    output_dir: str,
):
    async def inner():
        model_config = CodeT5ModelConfig(
            model_loc=Path(model_loc),
            device_map={0: list(range(4)), 1: list(range(4, 12))}
            if torch.cuda.device_count() >= 2
            else None,
        )
        experiments = create_experiments(
            model_config=model_config,
            train_data_jsonl=train_data_jsonl,
            eval_data_jsonl=eval_data_jsonl,
            max_num_experiments=max_num_experiments,
        )
        for datum_id, exp in experiments:
            await run_experiment(datum_id, exp, Path(output_dir))

    with torch.no_grad():
        asyncio.run(inner())


def add_arguments(argument_parser: argparse.ArgumentParser) -> None:
    argument_parser.add_argument(
        "--train_data_jsonl", required=True, help="The training data jsonl file."
    )
    argument_parser.add_argument(
        "--eval_data_jsonl", required=True, help="The evaluation data jsonl file."
    )
    argument_parser.add_argument(
        "--max_num_experiments",
        type=int,
        default=0,
        help="If positive, only run the first few experiments. 0 means running all experiments.",
    )
    argument_parser.add_argument(
        "--model_loc", required=True, help="The path to the model files."
    )
    argument_parser.add_argument(
        "--output_dir", required=True, help="The output directory."
    )


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(cmdline_parser)
    args = cmdline_parser.parse_args()

    main(
        model_loc=args.model_loc,
        train_data_jsonl=args.train_data_jsonl,
        eval_data_jsonl=args.eval_data_jsonl,
        max_num_experiments=args.max_num_experiments,
        output_dir=args.output_dir,
    )
