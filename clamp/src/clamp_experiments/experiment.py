import bdb
import datetime
import json
import pathlib
import sys
import time
import traceback
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import (
    AsyncContextManager,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

import jsons

from clamp.async_tools import limits
from clamp.search.datum import FullDatum, FullDatumSub
from clamp.search.model import Model, ModelResult
from clamp.util import logger
from clamp_experiments.datum_result import DatumResult
from clamp_experiments.eval_metrics import Metric


@dataclass
class Experiment(Generic[FullDatumSub]):
    model: Model[FullDatumSub]
    client: AsyncContextManager
    test_data: List[FullDatumSub]
    metrics: Mapping[str, Metric[Sequence[str], FullDatumSub]]
    log_dir: Optional[Path] = None


async def run_experiment(
    exp_name: str,
    exp: Experiment,
    log_dir: Optional[pathlib.Path] = None,
    debug: bool = False,
    ids: Optional[List[str]] = None,
    rerun: bool = False,
    num_eval_examples: Optional[int] = None,
    rank: int = 0,
    world_size: int = 1,
) -> None:
    if log_dir is None:
        if exp.log_dir is None:
            print("At least one of log_dir and exp.log_dir needs to be provided")
            return
        log_dir = exp.log_dir

    if world_size == 1:
        exp_log_dir = log_dir / exp_name
    else:
        exp_log_dir = log_dir / f"{exp_name}_rank-{rank:02d}-of-{world_size:02d}"
    exp_log_dir.mkdir(exist_ok=True, parents=True)
    results_path = exp_log_dir / "results.json"
    if results_path.exists() and not rerun:
        print(f"Skipping {exp_name}, already finished")
        return
    print("********************")
    print(f"Running {exp_name} rank {rank} world size {world_size}")
    print("********************")
    now = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    all_metric_results: Dict[str, float] = {}

    test_data = (
        [datum for datum in exp.test_data if datum.dialogue_id in ids]
        if ids
        else exp.test_data
    )
    if not test_data:
        print(f"No test data! ids: {ids}")
        return

    print(f"Total test examples: {len(test_data)}")
    test_data = test_data[
        (rank * len(test_data))
        // world_size : ((rank + 1) * len(test_data))
        // world_size
    ]
    if num_eval_examples is not None:
        test_data = test_data[:num_eval_examples]

    print(f"Test examples this shard: {len(test_data)}")
    current_test_index = 0

    # Find past model outputs
    candidate_past_model_outputs: List[Tuple[pathlib.Path, List[Dict]]] = []
    for past_model_outputs_path in exp_log_dir.glob("model_outputs.*.jsonl"):
        candidate_past_model_outputs.append(
            (
                past_model_outputs_path,
                [json.loads(line) for line in open(past_model_outputs_path, "r")],
            )
        )
    if candidate_past_model_outputs:
        past_model_outputs_path, past_model_outputs_to_copy = max(
            candidate_past_model_outputs, key=lambda t: len(t[1])
        )
        if len(past_model_outputs_to_copy) > 0:
            print(
                f"*** Copying {len(past_model_outputs_to_copy)} past results from {past_model_outputs_path} ***"
            )
    else:
        past_model_outputs_to_copy = []

    with logger.intercept_output(
        exp_log_dir / f"stdout.{now}", exp_log_dir / f"stderr.{now}"
    ), open(
        exp_log_dir / f"model_outputs.{now}.jsonl", "w"
    ) as model_outputs_f, ExitStack() as _logger_cm:

        try:
            for metric in exp.metrics.values():
                metric.reset()
            for test_datum, past_model_output in zip(
                test_data, past_model_outputs_to_copy
            ):
                current_test_index += 1
                assert test_datum.dialogue_id == past_model_output["test_datum_id"]
                assert (
                    test_datum.turn_index
                    == past_model_output["test_datum_turn_part_index"]
                )
                for metric in exp.metrics.values():
                    metric.update(past_model_output["outputs"], test_datum)
                model_outputs_f.write(json.dumps(past_model_output) + "\n")
            model_outputs_f.flush()

            start_time = time.time()
            first_unprocessed_test_index = current_test_index

            async with exp.client:
                async for kbest, test_datum in limits.map_async_limited(
                    exp.model.predict,
                    test_data[len(past_model_outputs_to_copy) :],
                    max_concurrency=1,
                    wrap_exception=not debug,
                ):
                    beam_search_text = [beam.text for beam in kbest]
                    beam_token_costs = [beam.token_costs for beam in kbest]

                    all_metric_results_for_datum: Dict[str, Optional[str]] = {}
                    for metric_name, metric in exp.metrics.items():
                        metric_one_result = metric.update(beam_search_text, test_datum)
                        for key, value_str in metric_one_result.items():
                            all_metric_results_for_datum[
                                f"{metric_name}/{key}"
                            ] = value_str
                    print(
                        exp_log_dir, json.dumps(all_metric_results_for_datum, indent=4)
                    )
                    results = DatumResult(
                        test_datum.natural,
                        kbest,
                        beam_search_text,
                        all_metric_results_for_datum,
                        test_datum.dialogue_id,
                        test_datum.turn_index,
                        test_datum.agent_context,
                        test_datum.canonical,
                        beam_token_costs,
                    )
                    model_outputs_f.write(jsons.dumps(results) + "\n")
                    model_outputs_f.flush()

                    # TODO: Delete this call and replace it with more flexible logging?
                    _exact_match_with_logging(test_datum, kbest)
                    current_test_index += 1
                    print(f"Current test index: {current_test_index}")

            num_processed = current_test_index - first_unprocessed_test_index
            elapsed = time.time() - start_time
            per_item = elapsed / num_processed if num_processed else None
            print("Timing report:")
            print(f"- Items processed: {num_processed}")
            print(f"- Elapsed: {elapsed}")
            print(f"- Per item: {per_item}")
            with open(f"{exp_log_dir}/timings.json", "w") as f:
                json.dump(
                    {
                        "num_processed": num_processed,
                        "elapsed": elapsed,
                        "per_item": per_item,
                    },
                    f,
                )

            for metric_name, metric in exp.metrics.items():
                for key, value in metric.compute().items():
                    all_metric_results[f"{metric_name}/{key}"] = value

            print(results_path, json.dumps(all_metric_results, indent=4))

            if not ids:
                with open(results_path, "w") as results_f:
                    json.dump(all_metric_results, results_f)
        except (KeyboardInterrupt, bdb.BdbQuit):  # pylint: disable=try-except-raise
            # If we get Ctrl-C then we want to stop the entire program,
            # instead of just skipping this one experiment.
            raise
        except Exception as e:  # pylint: disable=broad-except
            if isinstance(e, limits.MapInnerException):
                if isinstance(e.__cause__, (KeyboardInterrupt, bdb.BdbQuit)):
                    # If we get Ctrl-C then we want to stop the entire program,
                    # instead of just skipping this one experiment.
                    raise e.__cause__

                print(
                    f"Last test_datum: {e.orig_item} in experiment {exp_name}",
                    file=sys.stderr,
                )

            if debug:
                # If we're running inside a debugger, re-raise the
                # exception so that we can debug it.
                raise
            # Log the exception, and move onto the next item in `exps`.
            traceback.print_exc()


def _exact_match_with_logging(
    test_datum: FullDatum, kbest: Sequence[ModelResult]
) -> bool:
    # TODO: Replace this with a more flexible function suited to each domain

    gold = (
        test_datum.canonical.strip(" ")
        if test_datum.canonical is not None
        else "UNREACHABLE"
    )
    pred = kbest[0].text.strip(" ") if kbest else ""
    print()
    print(f"context:   {test_datum.agent_context}")
    print(f"natural:   {test_datum.natural}")
    print(f"predicted: {pred}")
    print(f"gold:      {gold}")
    result = gold == pred
    print(f"is correct: {result}")
    beam_result = False
    for i, pred_i in enumerate(kbest):
        stripped = pred_i.text.strip(" ")
        beam_result = beam_result or gold == stripped
        print(f"Beam {i} [{pred_i.cost:.3f}]: {stripped}")
        print(f"is correct@{i}: {beam_result}")
    print()
    return result
