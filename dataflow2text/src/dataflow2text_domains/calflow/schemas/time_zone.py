import datetime
from dataclasses import dataclass
from typing import Any, Dict

import pytz

from dataflow2text.dataflow.schema import NullaryStructSchema, String


@dataclass(frozen=True)
class TimeZone(NullaryStructSchema):
    id: String

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "TimeZone":
        schema = json_obj.get("schema")
        assert schema == "TimeZone"
        underlying = json_obj.get("underlying")

        return TimeZone(id=String.from_typed_json(underlying.get("id")))

    def to_python_timezone(self) -> datetime.tzinfo:
        return pytz.timezone(self.id.inner)
