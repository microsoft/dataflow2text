import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict

import evaluate
import gem_metrics
import numpy as np
import pandas as pd

from clamp.search.datum import FullDatum
from clamp_experiments.eval_metrics import TopKExactMatch


def _process_string(
    inp: str,
    ignore_case: bool = False,
    strip_spaces: bool = False,
):
    s = inp
    if ignore_case:
        s = s.lower()
    if strip_spaces:
        s = s.strip()
        tmp = ""
        for ch in s:
            if ch.isspace() or ch in (".", "?", ",", ":", "'"):
                # If there is consecutive whitespace at the boundaries of terminals/nonterminals,
                # or whitespace followed by punctuation, discard extra whitespace.
                tmp = tmp.rstrip()
            tmp += ch
    return s


def _load_references(data_tsv: str) -> pd.DataFrame:
    data_df = pd.read_csv(
        data_tsv,
        sep="\t",
        encoding="utf-8",
        quoting=csv.QUOTE_ALL,
        na_values=None,
        keep_default_na=False,
    )
    datum_ids = [
        f"{row.get('dialogueId')}_{row.get('turnIndex')}"
        for _, row in data_df.iterrows()
    ]
    normalized_references = [
        _process_string(
            row.get("agentUtterance"),
            ignore_case=True,
            strip_spaces=True,
        )
        for _, row in data_df.iterrows()
    ]
    data_df.loc[:, "datumId"] = datum_ids
    data_df.loc[:, "normalizedReference"] = normalized_references

    data_df.set_index("datumId", inplace=True)
    return data_df


def _load_predictions(predictions_json: str) -> Dict[str, Any]:
    with open(predictions_json) as fp:
        predictions_lookup = json.load(fp)

    normalized_predictions_lookup = {}
    for datum_id, predictions in predictions_lookup.items():
        normalized_predictions_lookup[datum_id] = [
            _process_string(
                prediction,
                ignore_case=True,
                strip_spaces=True,
            )
            for prediction in predictions
        ]

    return normalized_predictions_lookup


def main(
    data_tsv: str,
    predictions_json: str,
    output_dir: Path,
):
    references_df = _load_references(data_tsv)
    print(f"len(references_df) = {len(references_df)}")

    predictions_lookup = _load_predictions(predictions_json)

    gem_preds = gem_metrics.texts.Predictions(
        {
            "values": [
                predictions_lookup.get(datum_id, [""])[0]  # type: ignore
                for datum_id, row in references_df.iterrows()
            ]
        }
    )
    gem_refs = gem_metrics.texts.References(
        {
            "values": [
                {"target": [row.get("normalizedReference")]}
                for _, row in references_df.iterrows()
            ]
        }
    )
    gem_scores = gem_metrics.compute(
        outs=gem_preds,
        refs=gem_refs,
        metrics_dict=gem_metrics.metric_list_to_metric_dict(["bleu", "rouge"]),
    )
    print("======= gem_scores = ", json.dumps(gem_scores, indent=2))

    hf_predictions = [
        predictions_lookup.get(datum_id, [""])[0] for datum_id, row in references_df.iterrows()  # type: ignore
    ]
    hf_refs = [row.get("normalizedReference") for _, row in references_df.iterrows()]
    bertscore = evaluate.load("bertscore")
    raw_bert_scores = bertscore.compute(
        predictions=hf_predictions,
        references=hf_refs,
        lang="en",
        rescale_with_baseline=True,
    )
    bert_scores = {
        "precision": np.mean(raw_bert_scores["precision"]),
        "recall": np.mean(raw_bert_scores["recall"]),
        "f1": np.mean(raw_bert_scores["f1"]),
        "hashcode": raw_bert_scores["hashcode"],
    }
    print("======= bert_scores = ", json.dumps(bert_scores, indent=2))

    exact_match: TopKExactMatch = TopKExactMatch(10)
    datum_id: str
    for datum_id, row in references_df.iterrows():
        predictions = predictions_lookup.get(datum_id, [""])
        reference = FullDatum(
            dialogue_id=None,
            turn_index=None,
            agent_context=None,
            natural="",
            canonical=row.get("normalizedReference"),
        )
        exact_match.update(predictions, reference)
    recall_scores = exact_match.compute()
    print("======= recall_scores = ", json.dumps(recall_scores, indent=2))

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "gem_scores.json", "w") as fw:
        fw.write(json.dumps(gem_scores, indent=2))
    with open(output_dir / "raw_bert_scores.json", "w") as fw:
        fw.write(json.dumps(raw_bert_scores, indent=2))
    with open(output_dir / "bert_scores.json", "w") as fw:
        fw.write(json.dumps(bert_scores, indent=2))
    with open(output_dir / "recall_scores.json", "w") as fw:
        fw.write(json.dumps(recall_scores, indent=2))


def add_arguments(argument_parser: argparse.ArgumentParser) -> None:
    argument_parser.add_argument("--data_tsv", help="The data tsv file.")
    argument_parser.add_argument(
        "--predictions_json", help="The predictions json file."
    )
    argument_parser.add_argument("--output_dir", help="The output directory.")


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(cmdline_parser)
    args = cmdline_parser.parse_args()

    main(
        data_tsv=args.data_tsv,
        predictions_json=args.predictions_json,
        output_dir=Path(args.output_dir),
    )
