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
from typing import TYPE_CHECKING, Dict, List

from cached_property import cached_property
from transformers import GPT2Tokenizer

from clamp.tokenization.clamp_tokenizer import ClampTokenizer

if TYPE_CHECKING:
    # pylint: disable=reimported
    from transformers.models.gpt2.tokenization_gpt2 import GPT2Tokenizer


@dataclass
class GPT2ClampTokenizer(ClampTokenizer):

    tokenizer: GPT2Tokenizer

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size

    @property
    def pad_token_id(self) -> int:
        result = self.tokenizer.pad_token_id
        assert result is not None
        return result

    @property
    def unk_token_id(self) -> int:
        result = self.tokenizer.unk_token_id
        assert result is not None
        return result

    @property
    def eos_token_id(self) -> int:
        result = self.tokenizer.eos_token_id
        assert result is not None
        return result

    def tokenize(self, text: str) -> List[bytes]:
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) == 0:
            # Handles text with only whitespaces
            for token in list(text):
                token = "".join(
                    self.tokenizer.byte_encoder[b] for b in token.encode("utf-8")
                )
                tokens.append(token)
        token_bytes = [
            bytes([self.tokenizer.byte_decoder[c] for c in token]) for token in tokens
        ]
        return token_bytes

    @cached_property
    def utf8_token_to_id_map(  # pylint:disable=invalid-overridden-method
        self,
    ) -> Dict[bytes, int]:
        utf8_token_to_id: Dict[bytes, int] = {}
        # encoded_token: UTF-8 encoded strings where bytes corresponding to
        # control characters in ASCII have been mapped to other characters
        for encoded_token, token_id in self.tokenizer.encoder.items():
            # token_bytes: UTF-8 encoded string
            token_bytes = bytes(self.tokenizer.byte_decoder[c] for c in encoded_token)
            utf8_token_to_id[token_bytes] = token_id

        return utf8_token_to_id

    def save_pretrained(self, tokenizer_loc: str) -> None:
        self.tokenizer.save_pretrained(tokenizer_loc)

    @classmethod
    def from_pretrained(cls, tokenizer_loc: str) -> "GPT2ClampTokenizer":
        return GPT2ClampTokenizer(
            tokenizer=GPT2Tokenizer.from_pretrained(tokenizer_loc)
        )
