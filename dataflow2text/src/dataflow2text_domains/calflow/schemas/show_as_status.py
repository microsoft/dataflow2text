from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class ShowAsStatus(PrimitiveSchema):
    inner: str

    def __post_init__(self):
        if self.inner not in {
            "Free",
            "Tentative",
            "Busy",
            "OutOfOffice",
            "WorkingElsewhere",
            "Unknown",
            "UnexpectedValue",
        }:
            raise ValueError(f"Unknown ShowAsStatus: {self.inner}")

    @classmethod
    def Free(cls):
        return cls("Free")

    @classmethod
    def Tentative(cls):
        return cls("Tentative")

    @classmethod
    def Busy(cls):
        return cls("Busy")

    @classmethod
    def OutOfOffice(cls):
        return cls("OutOfOffice")

    @classmethod
    def WorkingElsewhere(cls):
        return cls("WorkingElsewhere")

    @classmethod
    def Unknown(cls):
        return cls("Unknown")

    @classmethod
    def UnexpectedValue(cls):
        return cls("UnexpectedValue")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "ShowAsStatus":
        schema_ = json_obj.get("schema")
        assert schema_ == "ShowAsStatus"
        underlying = json_obj.get("underlying")

        return ShowAsStatus(underlying)
