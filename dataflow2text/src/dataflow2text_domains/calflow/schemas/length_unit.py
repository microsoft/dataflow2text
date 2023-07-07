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

import pint
from pint import UnitRegistry

from dataflow2text.dataflow.schema import PrimitiveSchema

_UNIT_REGISTRY = UnitRegistry()


@dataclass(frozen=True)
class LengthUnit(PrimitiveSchema):
    inner: pint.Unit

    def __post_init__(self):
        assert self.inner in {
            _UNIT_REGISTRY.inch,
            _UNIT_REGISTRY.meter,
            _UNIT_REGISTRY.centimeter,
            _UNIT_REGISTRY.foot,
            _UNIT_REGISTRY.mile,
            _UNIT_REGISTRY.kilometer,
        }

    @classmethod
    def Inches(cls):
        return cls(_UNIT_REGISTRY.inch)

    @classmethod
    def Meters(cls):
        return cls(_UNIT_REGISTRY.meter)

    @classmethod
    def Centimeters(cls):
        return cls(_UNIT_REGISTRY.centimeter)

    @classmethod
    def Feet(cls):
        return cls(_UNIT_REGISTRY.foot)

    @classmethod
    def Miles(cls):
        return cls(_UNIT_REGISTRY.mile)

    @classmethod
    def Kilometers(cls):
        return cls(_UNIT_REGISTRY.kilometer)
