from dataflow2text_domains.calflow.functions.arithmetic import Minus, Plus
from dataflow2text_domains.calflow.functions.boolean_utils import And, Not, Or
from dataflow2text_domains.calflow.functions.comparison import (
    IsEqual,
    IsGreaterEqual,
    IsGreaterThan,
    IsLessEqual,
    IsLessThan,
)
from dataflow2text_domains.calflow.functions.constraint_utils import andConstraint
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    EqualConstraint,
    FuzzyEqualConstraint,
    GreaterEqualConstraint,
    GreaterThanConstraint,
    LessEqualConstraint,
    LessThanConstraint,
)
from dataflow2text_domains.calflow.schemas.length_unit import _UNIT_REGISTRY

MONTH_SCHEMAS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

DAY_OF_WEEK_SCHEMAS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

PLACE_FEATURE_SCHEMAS = [
    "HappyHour",
    "OutdoorDining",
    "Casual",
    "FullBar",
    "GoodforGroups",
    "WaiterService",
    "FamilyFriendly",
    "Takeout",
]

WEATHER_QUANTIFIER_SCHEMAS = ["Average", "Max", "Summarize", "Min", "Sum"]

LENGTH_UNIT_SCHEMAS = {
    _UNIT_REGISTRY.inch: "Inches",
    _UNIT_REGISTRY.meter: "Meters",
    _UNIT_REGISTRY.centimeter: "Centimeters",
    _UNIT_REGISTRY.foot: "Feet",
    _UNIT_REGISTRY.mile: "Miles",
    _UNIT_REGISTRY.kilometer: "Kilometers",
}

SPECIAL_CALL_LIKE_OP_NAMES = {
    "?=": EqualConstraint,
    "?~=": FuzzyEqualConstraint,
    "?>": GreaterThanConstraint,
    "?>=": GreaterEqualConstraint,
    "?<": LessThanConstraint,
    "?<=": LessEqualConstraint,
    "&": andConstraint,
    "==": IsEqual,
    ">": IsGreaterThan,
    ">=": IsGreaterEqual,
    "<": IsLessThan,
    "<=": IsLessEqual,
    "+": Plus,
    "-": Minus,
    "or": Or,
    "and": And,
    "not": Not,
}
