from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class Sensitivity(PrimitiveSchema):
    inner: str

    def __post_init__(self):
        if self.inner not in {"Normal", "Private"}:
            raise ValueError(f"Unknown Sensitivity: {self.inner}")

    @classmethod
    def Normal(cls):
        return cls("Normal")

    @classmethod
    def Private(cls):
        return cls("Private")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Sensitivity":
        schema_ = json_obj.get("schema")
        assert schema_ == "Sensitivity"
        underlying = json_obj.get("underlying")

        return Sensitivity(inner=underlying)
