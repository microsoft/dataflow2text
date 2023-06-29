from dataclasses import dataclass
from functools import total_ordering

from dataflow2text.dataflow.schema import NullaryStructSchema, Number
from dataflow2text_domains.calflow.schemas.length_unit import LengthUnit


@dataclass(frozen=True)
class WeatherProperty(NullaryStructSchema):
    # TODO: In Express, WeatherProperty is a typeclass and Number and DateTime are also instances of it.
    #  We may consider using Protocol similar to achieve this (see ComparableSchema).
    pass


@dataclass(frozen=True)
class Temperature(WeatherProperty):
    pass


@dataclass(frozen=True)
class Dimensionless(WeatherProperty):
    pass


@total_ordering
@dataclass(frozen=True)
class Length(WeatherProperty):
    value: Number
    unit: LengthUnit

    def total(self) -> float:
        return self.value.inner * self.unit.inner

    def __lt__(self, other: "Length"):
        return self.total() < other.total()


@dataclass(frozen=True)
class Pressure(WeatherProperty):
    pass


@dataclass(frozen=True)
class Velocity(WeatherProperty):
    pass


@dataclass(frozen=True)
class Angle(WeatherProperty):
    pass


@dataclass(frozen=True)
class Point(WeatherProperty, NullaryStructSchema):
    lat: Number
    lon: Number
