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
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from transformers import PreTrainedModel, T5ForConditionalGeneration

from clamp.seq2seq.seq2seq_helper import Seq2SeqSettings, Surround
from clamp.tokenization.clamp_tokenizer import ClampTokenizer
from clamp.tokenization.gpt2_clamp_tokenizer import GPT2ClampTokenizer


@dataclass
class CodeT5ModelConfig:
    model_loc: Path
    device_map: Optional[Dict[int, List[int]]] = None

    def setup_model(self) -> Tuple[PreTrainedModel, ClampTokenizer, Seq2SeqSettings]:
        if not self.model_loc.exists():
            raise ValueError(f"Model files not found in {self.model_loc}")
        model = T5ForConditionalGeneration.from_pretrained(self.model_loc)
        assert isinstance(model, T5ForConditionalGeneration)
        tokenizer = GPT2ClampTokenizer.from_pretrained(str(self.model_loc))
        seq2seq_settings = Seq2SeqSettings(
            input_surround=Surround(bos=[1], eos=[2], starts_with_space=True),
            output_surround=Surround(bos=[1], eos=[2], starts_with_space=True),
            decoder_start_token_id=0,
        )
        self.maybe_parallelize(model)  # type: ignore
        model.eval()  # type: ignore
        return model, tokenizer, seq2seq_settings  # type: ignore

    def maybe_parallelize(self, model: PreTrainedModel) -> None:
        if torch.cuda.is_available():
            if self.device_map is not None and model.is_parallelizable:  # type: ignore
                print(f"Parallelizing model with {self.device_map}")
                model.parallelize(self.device_map)  # type: ignore
            else:
                print("Entire model to GPU 0")
                model.to(torch.device("cuda:0"))  # type: ignore[attr-defined]
        else:
            model.to(torch.device("cpu"))  # type: ignore[attr-defined]
