import datetime
from dataclasses import dataclass
from functools import total_ordering

from dataflow2text.dataflow.schema import Long, NullaryStructSchema


@total_ordering
@dataclass(frozen=True)
class Duration(NullaryStructSchema):
    seconds: Long = Long(0)
    nanoseconds: Long = Long(0)

    def to_python_duration(self) -> datetime.timedelta:
        return datetime.timedelta(
            seconds=self.seconds.inner,
            # This loss of precision may introduce bugs, but we assume this does not matter in practice.
            microseconds=int(self.nanoseconds.inner / 1000),
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Duration):
            raise ValueError(f"cannot compare{self} with {other}.")

        return self.to_python_duration() < other.to_python_duration()
