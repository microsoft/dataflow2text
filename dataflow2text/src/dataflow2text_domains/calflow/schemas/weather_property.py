# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
