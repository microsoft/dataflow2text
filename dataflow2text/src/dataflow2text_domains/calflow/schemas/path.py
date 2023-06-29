from dataclasses import dataclass

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class Path(PrimitiveSchema):
    inner: str
