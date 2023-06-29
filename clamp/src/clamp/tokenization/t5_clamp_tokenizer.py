import tempfile
from typing import Dict, Iterable, List, Optional

from sentencepiece import sentencepiece_model_pb2 as sentencepiece_model
from transformers import T5Tokenizer

from clamp.tokenization.clamp_tokenizer import ClampTokenizer


class T5ClampTokenizer(ClampTokenizer):
    # pylint: disable=super-init-not-called
    def __init__(
        self, tokenizer: T5Tokenizer, output_sequences: Optional[Iterable[str]] = None
    ):
        """
        `output_sequences` if provided, will be used to detect unk symbols and adding them to vocab.
        T5 has 28 extra token ids, if we need to add more than 28 new tokens to the vocab, we need to resize the
        token embeddings.
        """
        # Saving input tokenizer to a temp location so that it can be modified.
        tmp_tokenizer_loc = tempfile.mkdtemp()
        tokenizer.save_pretrained(tmp_tokenizer_loc)  # type: ignore

        # Modify the sentencepiece model normalizer settings to not ignore whitespaces.
        spiece_model_file = f"{tmp_tokenizer_loc}/spiece.model"
        m = sentencepiece_model.ModelProto()
        m.ParseFromString(open(spiece_model_file, "rb").read())
        m.normalizer_spec.add_dummy_prefix = False  # pylint: disable=no-member
        m.normalizer_spec.remove_extra_whitespaces = False  # pylint: disable=no-member
        m.normalizer_spec.precompiled_charsmap = b""  # pylint: disable=no-member
        m.denormalizer_spec.add_dummy_prefix = False  # pylint: disable=no-member
        m.denormalizer_spec.remove_extra_whitespaces = (  # pylint: disable=no-member
            False
        )
        m.denormalizer_spec.precompiled_charsmap = b""  # pylint: disable=no-member

        with open(spiece_model_file, "wb") as f:
            f.write(m.SerializeToString())
        self.tokenizer = T5Tokenizer.from_pretrained(tmp_tokenizer_loc)
        self.token_to_id_map = {
            k.replace("▁", " ").encode("utf-8"): v
            for k, v in self.tokenizer.get_vocab().items()
        }
        if output_sequences is not None:
            self.update_tokenizer_with_output_sequences(output_sequences)

    def update_tokenizer_with_output_sequences(
        self, output_sequences: Iterable[str]
    ) -> None:
        tmp_tokenizer_loc = tempfile.mkdtemp()
        self.tokenizer.save_pretrained(tmp_tokenizer_loc)
        spiece_model_file = f"{tmp_tokenizer_loc}/spiece.model"
        m = sentencepiece_model.ModelProto()
        m.ParseFromString(open(spiece_model_file, "rb").read())
        t5_vocab = self.tokenizer.get_vocab()
        # Look for unk tokens and add them to the vocab
        unk_tokens = {
            token
            for output_sequence in output_sequences
            for token in self.tokenizer.tokenize(output_sequence)
            if token not in t5_vocab
        }
        if len(unk_tokens) > 0:
            print(f"Adding unk tokens to the vocab: {unk_tokens}")
        for token in unk_tokens:
            new_token = sentencepiece_model.ModelProto().SentencePiece()
            new_token.piece = token
            new_token.score = 0
            m.pieces.append(new_token)  # pylint: disable=no-member

        with open(spiece_model_file, "wb") as f:
            f.write(m.SerializeToString())

        self.tokenizer = T5Tokenizer.from_pretrained(tmp_tokenizer_loc)
        self.token_to_id_map = {
            k.replace("▁", " ").encode("utf-8"): v
            for k, v in self.tokenizer.get_vocab().items()
        }

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size

    @property
    def pad_token_id(self) -> int:
        return 0

    @property
    def unk_token_id(self) -> int:
        return self.tokenizer.unk_token_id

    @property
    def eos_token_id(self) -> int:
        return self.tokenizer.eos_token_id

    def tokenize(self, text: str) -> List[bytes]:
        tokens = self.tokenizer.tokenize(text)
        return [token.replace("▁", " ").encode("utf-8") for token in tokens]

    @property
    def utf8_token_to_id_map(self) -> Dict[bytes, int]:
        return self.token_to_id_map

    def encode(self, text: str) -> List[int]:
        tokens = self.tokenize(text)
        unk_token_id = 2
        return [self.utf8_token_to_id_map.get(token, unk_token_id) for token in tokens]

    def save_pretrained(self, tokenizer_loc: str) -> None:
        self.tokenizer.save_pretrained(tokenizer_loc)

    # pylint: disable=arguments-differ
    @classmethod
    def from_pretrained(
        cls, tokenizer_loc: str, output_sequences: Optional[Iterable[str]] = None
    ) -> "T5ClampTokenizer":
        return T5ClampTokenizer(
            tokenizer=T5Tokenizer.from_pretrained(tokenizer_loc),
            output_sequences=output_sequences,
        )
