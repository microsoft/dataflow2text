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

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from clamp.search.model import ModelResult


@dataclass(frozen=True, eq=True)
class DatumResult:
    """CLAMP predictions and results for a single datum"""

    # Test datum utterance
    test_datum_natural: str

    # Text and cost of each sequence in the final beam
    results: List[ModelResult]

    # Text of each sequence in the final beam
    # (Duplicated from `results`; maintained here only
    # for backwards compatibility. May be removed later.)
    outputs: List[str]

    # The metrics dictionary containing the main results
    metrics: Dict[str, Optional[str]]

    # Other (optional) test datum fields
    test_datum_id: Optional[str] = None
    test_datum_turn_part_index: Optional[int] = None
    test_datum_agent_context: Optional[str] = None
    test_datum_canonical: Optional[str] = None

    # Token-level log probabilities for each sequence in the final beam
    # (Not yet implemented)
    token_logprobs: Optional[List[List[Tuple[str, float]]]] = None
