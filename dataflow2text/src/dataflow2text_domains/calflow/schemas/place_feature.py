from dataclasses import dataclass

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class PlaceFeature(PrimitiveSchema):
    inner: int

    def __post_init__(self):
        assert 1 <= self.inner <= 8

    @classmethod
    def HappyHour(cls):
        return cls(1)

    @classmethod
    def OutdoorDining(cls):
        return cls(2)

    @classmethod
    def Casual(cls):
        return cls(3)

    @classmethod
    def FullBar(cls):
        return cls(4)

    @classmethod
    def GoodforGroups(cls):
        return cls(5)

    @classmethod
    def WaiterService(cls):
        return cls(6)

    @classmethod
    def FamilyFriendly(cls):
        return cls(7)

    @classmethod
    def Takeout(cls):
        return cls(8)
