from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class ResponseStatusType(PrimitiveSchema):
    """

    Note `Null` and `NotResponded` are equivalent.
    TODO: There is only one use of `NotResponded` in CalFlow, and we should change that to `Null` and then
    change this schema.
    """

    inner: str

    def __post_init__(self):
        if self.inner not in {
            "Null",
            "Organizer",
            "TentativelyAccepted",
            "Accepted",
            "Declined",
            "NotResponded",
        }:
            raise ValueError(f"Unknown ResponseStatusType: {self.inner}")

    @classmethod
    def Null(cls):
        return cls("Null")

    @classmethod
    def Organizer(cls):
        return cls("Organizer")

    @classmethod
    def TentativelyAccepted(cls):
        return cls("TentativelyAccepted")

    @classmethod
    def Accepted(cls):
        return cls("Accepted")

    @classmethod
    def Declined(cls):
        return cls("Declined")

    @classmethod
    def NotResponded(cls):
        return cls("NotResponded")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "ResponseStatusType":
        schema = json_obj.get("schema")
        assert schema == "ResponseStatusType"
        underlying = json_obj.get("underlying")
        assert underlying is not None

        if underlying == "None":
            return ResponseStatusType.Null()

        return ResponseStatusType(underlying)
