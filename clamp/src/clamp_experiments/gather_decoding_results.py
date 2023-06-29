"""Gathers results from clamp_experiments.run_{unconstrained,constrained}_decoding."""
import argparse
import json
import os
from pathlib import Path

from clamp_experiments.ranked_predictions import RankedPredictions, load_clamp_outputs


def main(experiments_base_dir: str, output_dir: str):
    clamp_predictions_lookup = load_clamp_outputs(Path(experiments_base_dir))

    results = {}
    empty_prediction_datum_ids = []
    clamp_predictions: RankedPredictions
    for datum_id, clamp_predictions in clamp_predictions_lookup.items():
        if not clamp_predictions.inner:
            predictions = [""]
            empty_prediction_datum_ids.append(datum_id)
        else:
            predictions = [item.text for item in clamp_predictions.inner]

        assert datum_id not in results
        results[datum_id] = predictions

    print(f"Number of empty predictions: {len(empty_prediction_datum_ids)}")

    with open(os.path.join(output_dir, "predictions.json"), "w") as fp:
        fp.write(json.dumps(results, indent=2, sort_keys=True))
        fp.write("\n")

    with open(os.path.join(output_dir, "empty_prediction_datum_ids.txt"), "w") as fp:
        for datum_id in empty_prediction_datum_ids:
            fp.write(f"{datum_id}\n")


def add_arguments(argument_parser: argparse.ArgumentParser) -> None:
    argument_parser.add_argument(
        "--experiments_base_dir", help="The path to the experiments base directory."
    )
    argument_parser.add_argument("--output_dir", help="The output directory.")


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(cmdline_parser)
    args = cmdline_parser.parse_args()

    main(experiments_base_dir=args.experiments_base_dir, output_dir=args.output_dir)
