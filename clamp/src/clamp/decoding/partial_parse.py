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

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import torch


class PartialParse(ABC):
    @abstractmethod
    def allowed_next(
        self, ordered_ids: Optional[torch.Tensor] = None, top_k: Optional[int] = None
    ) -> Tuple[Optional[torch.Tensor], bool]:
        """Returns possible ways to extend the current prefix.

        The Tensor is of type long and 1-dimensional, with no duplicate values,
        containing the IDs of the tokens that we could append.
        If it is None, then any token is allowed.
        The bool indicates whether we are allowed to terminate here.

        If ordered_ids and top_k are not None, this may optionally return only
        the first `top_k` token IDs from ordered_ids which comports with the
        grammar, instead of all such token IDs.
        """

    @abstractmethod
    def append(self, token: int) -> "PartialParse":
        """Return a new PartialParse created by appending this token."""
