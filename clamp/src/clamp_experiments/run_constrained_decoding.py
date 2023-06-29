import argparse
import asyncio
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import torch
from tqdm import tqdm

from clamp.decoding.partial_parse import PartialParse
from clamp.decoding.uint8_earley_partial_parse import (
    UInt8EarleyPartialParse,
    UInt8GrammarTokenizerInfo,
)
from clamp.earley.cfg import load_grammar_from_directory
from clamp.search.beam_search_semantic_parser import BeamSearchSemanticParser
from clamp.search.datum import DatumSub, FullDatum
from clamp.search.problem_factory import ConstrainedDecodingProblemFactory
from clamp.search.seq2seq_decoding_step import PartialParseBuilder, Seq2SeqDecodingSetup
from clamp.seq2seq.seq2seq_bart import Seq2SeqBart
from clamp.seq2seq.seq2seq_model import HS, AutoregressiveModel
from clamp.tokenization.clamp_tokenizer import ClampTokenizer
from clamp_experiments.codet5_model_config import CodeT5ModelConfig
from clamp_experiments.eval_metrics import Metric, TopKExactMatch
from clamp_experiments.experiment import Experiment, run_experiment
from clamp_experiments.fit_max_steps import compute_and_print_fit
from clamp_experiments.io_utils import load_data_from_json_file


def create_partial_parse_builder(
    tokenizer: ClampTokenizer, grammar_dir: str
) -> PartialParseBuilder[FullDatum]:

    specialized_grammar = load_grammar_from_directory(grammar_dir)
    grammar_tokenizer_info = UInt8GrammarTokenizerInfo.from_clamp_tokenizer(
        specialized_grammar, tokenizer
    )
    partial_parse = UInt8EarleyPartialParse.initial(grammar_tokenizer_info)
    partial_parse_builder = lambda _: partial_parse
    return partial_parse_builder


def make_semantic_parser(
    lm: AutoregressiveModel[HS],
    beam_size: int,
    partial_parse_builder: Callable[[DatumSub], PartialParse],
    max_steps_fn: Optional[Callable[[DatumSub], Optional[int]]],
    keep_finished_nodes: bool = False,
) -> BeamSearchSemanticParser:
    decoding_setup: Seq2SeqDecodingSetup = Seq2SeqDecodingSetup(
        partial_parse_builder=partial_parse_builder, seq2seq_model=lm  # type: ignore
    )

    problem_factory = ConstrainedDecodingProblemFactory(
        autoregressive_model=lm,
        decoding_setup=decoding_setup,
        length_normalization=0.7,
        top_k=beam_size,
    )

    return BeamSearchSemanticParser(
        problem_factory=problem_factory,
        tokenizer=lm.tokenizer,
        beam_size=beam_size,
        max_steps_fn=max_steps_fn,
        keep_finished_nodes=keep_finished_nodes,
    )


def build_lm_and_tokenizer(model_config: CodeT5ModelConfig, train_data_jsonl: str):
    model, tokenizer, _ = model_config.setup_model()

    # CodeT5Model can be loaded as a Seq2SeqBart since they both use the encoder-decoder architecture.
    lm = Seq2SeqBart(
        pretrained_model_dir=str(model_config.model_loc),
        model=model,
        clamp_tokenizer=tokenizer,
    )

    print(f"Reading {train_data_jsonl}")
    train_data = load_data_from_json_file(train_data_jsonl)
    print(f"len(train_data) = {len(train_data)}")

    # Everything other than Overnight in BenchClamp
    train_length_pairs = []
    for datum in train_data:
        num_input_tokens = len(tokenizer.tokenize(datum.natural))
        num_output_tokens = len(tokenizer.tokenize(datum.canonical)) + 1
        train_length_pairs.append((num_input_tokens, num_output_tokens))

    max_steps_intercept, max_steps_slope = compute_and_print_fit(
        train_length_pairs, 10, 1
    )
    max_steps_fn = lambda _datum: min(
        int(
            len(tokenizer.tokenize(_datum.natural)) * max_steps_slope
            + max_steps_intercept
        ),
        1000,
    )

    return lm, tokenizer, max_steps_fn


def create_experiments(
    model_config: CodeT5ModelConfig,
    train_data_jsonl: str,
    eval_data_jsonl: str,
    max_num_experiments: int,
    grammar_base_dir: str,
) -> List[Tuple[str, Experiment]]:
    print(f"Reading {eval_data_jsonl}")
    eval_data = load_data_from_json_file(eval_data_jsonl)
    print(f"len(eval_data) = {len(eval_data)}")
    if max_num_experiments > 0:
        eval_data = eval_data[:max_num_experiments]
        print(f"len(eval_data) = {len(eval_data)}")

    lm, tokenizer, max_steps_fn = build_lm_and_tokenizer(model_config, train_data_jsonl)
    beam_size = 5
    metrics: Dict[str, Metric[Sequence[str], FullDatum]] = {
        "exact_match": TopKExactMatch(beam_size)
    }

    experiments = []
    for datum in tqdm(eval_data):
        datum_id = f"{datum.dialogue_id}_{datum.turn_index}"
        print(f"Creating experiment for {datum_id}")

        partial_parse_builder = create_partial_parse_builder(
            tokenizer, os.path.join(grammar_base_dir, datum_id)
        )
        parser = make_semantic_parser(
            lm=lm,
            beam_size=beam_size,
            partial_parse_builder=partial_parse_builder,
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
    grammar_base_dir: str,
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
            grammar_base_dir=grammar_base_dir,
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
        "--grammar_base_dir", required=True, help="The base directory of the grammar."
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
        grammar_base_dir=args.grammar_base_dir,
        output_dir=args.output_dir,
    )
