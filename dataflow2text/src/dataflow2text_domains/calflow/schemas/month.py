from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class Month(PrimitiveSchema):
    # Use 1-based values to be consistent with python datetime.
    inner: int

    def __post_init__(self):
        assert 1 <= self.inner <= 12

    @classmethod
    def January(cls):
        return cls(1)

    @classmethod
    def February(cls):
        return cls(2)

    @classmethod
    def March(cls):
        return cls(3)

    @classmethod
    def April(cls):
        return cls(4)

    @classmethod
    def May(cls):
        return cls(5)

    @classmethod
    def June(cls):
        return cls(6)

    @classmethod
    def July(cls):
        return cls(7)

    @classmethod
    def August(cls):
        return cls(8)

    @classmethod
    def September(cls):
        return cls(9)

    @classmethod
    def October(cls):
        return cls(10)

    @classmethod
    def November(cls):
        return cls(11)

    @classmethod
    def December(cls):
        return cls(12)

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Month":
        schema = json_obj.get("schema")
        assert schema == "Month"
        underlying = json_obj.get("underlying")

        return Month(_ALL_MONTHS.index(underlying) + 1)


_ALL_MONTHS = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]
