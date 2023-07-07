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

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Prediction:
    text: str
    cost: float


@dataclass
class RankedPredictions:
    inner: List[Prediction]

    def __init__(self, predictions: List[Prediction]):
        # sort as per increasing cost
        self.inner = sorted(predictions, key=lambda x: x.cost)


def _strip_post_eos(s: str, eos_token: Optional[str] = None) -> str:
    if eos_token is None or eos_token not in s:
        return s
    return s[: s.index(eos_token)]


def load_clamp_outputs(
    experiments_base_dir: Path, eos_token: Optional[str] = None
) -> Dict[str, RankedPredictions]:
    """Returns a dictionary of datum_id -> RankedPredictions"""

    ret = {}
    error_cnt = 0
    for datum_id in os.listdir(experiments_base_dir):
        datum_id = str(datum_id)
        exp_dir = experiments_base_dir / datum_id
        model_outputs_paths = list(exp_dir.glob("model_outputs*.json*"))
        latest_file = max(
            model_outputs_paths, key=os.path.getctime
        )  # get the latest model_outputs* file
        model_outputs: List[Dict] = [
            json.loads(line) for line in open(latest_file, "r")
        ]
        if len(model_outputs) != 1:
            error_cnt += 1
            continue
        model_output = [
            Prediction(
                text=_strip_post_eos(t["text"], eos_token=eos_token),
                cost=float(t["cost"]),
            )
            for t in model_outputs[0]["results"]
        ]
        ranked_predictions = RankedPredictions(model_output)

        ret[datum_id] = ranked_predictions
    print(f"[load_clamp_outputs] error_cnt = {error_cnt}")
    print(f"[load_clamp_outputs] len(ret)  = {len(ret)}")

    return ret
