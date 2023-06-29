from dataclasses import dataclass

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class WeatherQuantifier(PrimitiveSchema):
    inner: int

    def __post_init__(self):
        assert 1 <= self.inner <= 5

    @classmethod
    def Average(cls):
        return cls(1)

    @classmethod
    def Max(cls):
        return cls(2)

    @classmethod
    def Summarize(cls):
        return cls(3)

    @classmethod
    def Min(cls):
        return cls(4)

    @classmethod
    def Sum(cls):
        return cls(5)
