from dataclasses import dataclass

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class Holiday(PrimitiveSchema):
    inner: str

    def __post_init__(self):
        assert self.inner in {
            name for name, obj in vars(Holiday).items() if isinstance(obj, classmethod)
        }

    @classmethod
    def AprilFoolsDay(cls):
        return cls("AprilFoolsDay")

    @classmethod
    def AshWednesday(cls):
        return cls("AshWednesday")

    @classmethod
    def BlackFriday(cls):
        return cls("BlackFriday")

    @classmethod
    def Christmas(cls):
        return cls("Christmas")

    @classmethod
    def ColumbusDay(cls):
        return cls("ColumbusDay")

    @classmethod
    def EarthDay(cls):
        return cls("EarthDay")

    @classmethod
    def Easter(cls):
        return cls("Easter")

    @classmethod
    def EasterMonday(cls):
        return cls("EasterMonday")

    @classmethod
    def ElectionDay(cls):
        return cls("ElectionDay")

    @classmethod
    def FathersDay(cls):
        return cls("FathersDay")

    @classmethod
    def FlagDay(cls):
        return cls("FlagDay")

    @classmethod
    def GoodFriday(cls):
        return cls("GoodFriday")

    @classmethod
    def GroundhogDay(cls):
        return cls("GroundhogDay")

    @classmethod
    def Halloween(cls):
        return cls("Halloween")

    @classmethod
    def IndependenceDay(cls):
        return cls("IndependenceDay")

    @classmethod
    def Kwanzaa(cls):
        return cls("Kwanzaa")

    @classmethod
    def LaborDay(cls):
        return cls("LaborDay")

    @classmethod
    def MardiGras(cls):
        return cls("MardiGras")

    @classmethod
    def MemorialDay(cls):
        return cls("MemorialDay")

    @classmethod
    def MLKDay(cls):
        return cls("MLKDay")

    @classmethod
    def MothersDay(cls):
        return cls("MothersDay")

    @classmethod
    def NewYearsDay(cls):
        return cls("NewYearsDay")

    @classmethod
    def NewYearsEve(cls):
        return cls("NewYearsEve")

    @classmethod
    def PalmSunday(cls):
        return cls("PalmSunday")

    @classmethod
    def PatriotDay(cls):
        return cls("PatriotDay")

    @classmethod
    def PresidentsDay(cls):
        return cls("PresidentsDay")

    @classmethod
    def StPatricksDay(cls):
        return cls("StPatricksDay")

    @classmethod
    def TaxDay(cls):
        return cls("TaxDay")

    @classmethod
    def Thanksgiving(cls):
        return cls("Thanksgiving")

    @classmethod
    def ValentinesDay(cls):
        return cls("ValentinesDay")

    @classmethod
    def VeteransDay(cls):
        return cls("VeteransDay")
