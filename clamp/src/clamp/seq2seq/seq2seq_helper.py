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
from typing import List, Optional, Sequence

import jsons

from clamp.tokenization.clamp_tokenizer import ClampTokenizer


@dataclass
class Surround:
    bos: List[int]
    eos: List[int]
    starts_with_space: bool


@dataclass
class Seq2SeqSettings:
    input_surround: Surround
    output_surround: Surround
    decoder_start_token_id: Optional[int]


@dataclass
class Seq2SeqHelper:
    settings: Seq2SeqSettings
    tokenizer: ClampTokenizer
    decoder_start_token_ids: List[int]
    decoder_eos_token_id: int
    decoder_output_begins_with_space: bool

    @classmethod
    def from_settings_json(
        cls, json_str: str, tokenizer: ClampTokenizer
    ) -> "Seq2SeqHelper":
        settings = jsons.loads(json_str, cls=Seq2SeqSettings)
        decoder_start_token_ids = settings.output_surround.bos
        if settings.decoder_start_token_id is not None:
            decoder_start_token_ids = [
                settings.decoder_start_token_id
            ] + decoder_start_token_ids

        # Output surround eos should be one token id, since that needs to be used to detect end of output sequence.
        assert len(settings.output_surround.eos) == 1
        decoder_eos_token_id = settings.output_surround.eos[0]
        decoder_output_begins_with_space = settings.output_surround.starts_with_space
        return cls(
            settings,
            tokenizer,
            decoder_start_token_ids,
            decoder_eos_token_id,
            decoder_output_begins_with_space,
        )

    def encode_for_encoder(self, s: str) -> List[int]:
        string_to_tokenize = s
        if self.settings.input_surround.starts_with_space:
            string_to_tokenize = " " + s
        token_ids = (
            self.settings.input_surround.bos
            + list(self.tokenizer.encode(string_to_tokenize))
            + self.settings.input_surround.eos
        )
        return token_ids

    def encode_prefix_for_decoder(
        self, s: str, include_bos_ids: bool = True
    ) -> List[int]:
        string_to_tokenize = s
        if self.settings.output_surround.starts_with_space:
            string_to_tokenize = " " + s
        token_ids = self.tokenizer.encode(string_to_tokenize)
        if include_bos_ids:
            return self.decoder_start_token_ids + token_ids
        else:
            return token_ids

    def decode_output(self, ids: Sequence[int]) -> str:
        output = self.tokenizer.decode(list(ids))
        if self.decoder_output_begins_with_space and output[0] == " ":
            output = output[1:]
        return output
