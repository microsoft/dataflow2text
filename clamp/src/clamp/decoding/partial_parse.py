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
