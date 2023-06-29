from typing import Optional, Tuple

import torch

from clamp.decoding.partial_parse import PartialParse


class NullPartialParse(PartialParse):
    """PartialParse which admits any sequence."""

    def allowed_next(
        self, ordered_ids: Optional[torch.Tensor] = None, top_k: Optional[int] = None
    ) -> Tuple[Optional[torch.Tensor], bool]:
        return None, True

    def append(self, token: int) -> "PartialParse":
        return self
