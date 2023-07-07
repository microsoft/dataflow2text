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

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, List, Optional, Sequence, TypeVar

from clamp.search.datum import FullDatumSub

Pred = TypeVar("Pred")
Target = TypeVar("Target")


class Metric(Generic[Pred, Target], ABC):
    """Used to measure goodness of model results compared to the ground truth.

    Stateful over the duration of an experiment run."""

    @abstractmethod
    def update(self, pred: Pred, target: Target) -> Dict[str, Optional[str]]:
        """Uses `target` and the model predictions `pred` to update the state."""

    @abstractmethod
    def compute(self) -> Dict[str, float]:
        """Uses the state to compute the final results."""

    @abstractmethod
    def reset(self) -> None:
        """Reinitializes the state."""


@dataclass
class TopKExactMatch(Metric[Sequence[str], FullDatumSub]):
    k: int
    correct: List[int] = dataclasses.field(init=False)
    total: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.reset()

    # pylint: disable=no-self-use
    def _is_correct(self, pred: str, target: FullDatumSub) -> bool:
        """Can be overridden by child classes."""
        return pred == target.canonical

    # pylint: disable=arguments-renamed
    def update(
        self, preds: Sequence[str], target: FullDatumSub
    ) -> Dict[str, Optional[str]]:
        self.total += 1
        found_correct = False
        result: Dict[str, Optional[str]] = {}
        for i, pred in enumerate(preds[: self.k]):
            correct = self._is_correct(pred, target)
            found_correct |= correct
            self.correct[i] += found_correct
            result[f"rank{i + 1}"] = "correct" if correct else "incorrect"
            result[f"top{i + 1}"] = "correct" if found_correct else "incorrect"

        # Handle when we have fewer predictions than self.k
        for i in range(len(preds), self.k):
            self.correct[i] += found_correct
            result[f"rank{i + 1}"] = "incorrect"
            result[f"top{i + 1}"] = "correct" if found_correct else "incorrect"

        return result

    def compute(self) -> Dict[str, float]:
        result = {}
        for i in range(self.k):
            result[f"top{i + 1}"] = self.correct[i] / self.total
        return result

    def reset(self) -> None:
        self.correct = [0] * self.k
        self.total = 0
