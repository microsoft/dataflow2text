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
from dataclasses import dataclass
from typing import Dict, List

from cached_property import cached_property


@dataclass  # type: ignore
class ClampTokenizer(ABC):
    """
    Tokenizer interface to use for Clamp experiments. Any class implementing this interface should respect all
    whitespaces while tokenizing text. This interface only works for tokenizers using tokens aligned to
    UTF-8-encoded byte boundaries.
    """

    @abstractmethod
    def tokenize(self, text: str) -> List[bytes]:
        pass

    @property
    @abstractmethod
    def vocab_size(self) -> int:
        pass

    @property
    @abstractmethod
    def utf8_token_to_id_map(self) -> Dict[bytes, int]:
        pass

    # TODO: Make these token_ids Optional[int]
    @property
    @abstractmethod
    def pad_token_id(self) -> int:
        pass

    @property
    @abstractmethod
    def unk_token_id(self) -> int:
        pass

    @property
    @abstractmethod
    def eos_token_id(self) -> int:
        pass

    @abstractmethod
    def save_pretrained(self, tokenizer_loc: str) -> None:
        pass

    @classmethod
    @abstractmethod
    def from_pretrained(cls, tokenizer_loc: str) -> "ClampTokenizer":
        pass

    # pylint: disable=no-self-use
    def detokenize(self, tokens: List[bytes]) -> str:
        full_bytes = b"".join(tokens)
        try:
            return full_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return "<Undecodable_UTF-8_string>"

    @cached_property
    def id_to_utf8_token_map(self) -> Dict[int, bytes]:
        return {v: k for k, v in self.utf8_token_to_id_map.items()}

    def encode(self, text: str) -> List[int]:
        tokens = self.tokenize(text)
        return [self.utf8_token_to_id_map[token] for token in tokens]

    def decode(self, token_ids: List[int]) -> str:
        tokens = [
            self.id_to_utf8_token_map[token_id]
            for token_id in token_ids
            if token_id in self.id_to_utf8_token_map
        ]
        return self.detokenize(tokens)
