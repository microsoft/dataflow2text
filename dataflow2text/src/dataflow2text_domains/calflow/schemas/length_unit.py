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
