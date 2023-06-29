from dataclasses import dataclass

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class DayOfWeek(PrimitiveSchema):
    # Use 0-based values to be consistent with python datetime.
    inner: int

    def __post_init__(self):
        assert isinstance(self.inner, int)
        assert 0 <= self.inner < 7

    @classmethod
    def Monday(cls):
        return cls(0)

    @classmethod
    def Tuesday(cls):
        return cls(1)

    @classmethod
    def Wednesday(cls):
        return cls(2)

    @classmethod
    def Thursday(cls):
        return cls(3)

    @classmethod
    def Friday(cls):
        return cls(4)

    @classmethod
    def Saturday(cls):
        return cls(5)

    @classmethod
    def Sunday(cls):
        return cls(6)
