"""Grammar rules for describing `Constraint[Time]`s"""
from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.dataflow.schema import Interval
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.time_constraints import (
    Afternoon,
    Evening,
    LateAfternoon,
    Morning,
    Night,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_TIME,
)
from dataflow2text_domains.calflow.schemas.time_range_constraint import (
    TimeRangeConstraint,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="in the morning",
)
def pp_handle_morning(c: BaseFunction):
    match c:
        case Morning():
            return {}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="morning",
)
def np_handle_morning(c: BaseFunction):
    match c:
        case Morning():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="in the afternoon",
)
def pp_handle_afternoon(c: BaseFunction):
    match c:
        case Afternoon():
            return {}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="afternoon",
)
def np_handle_afternoon(c: BaseFunction):
    match c:
        case Afternoon():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="in the evening",
)
def pp_handle_evening(c: BaseFunction):
    match c:
        case Evening():
            return {}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="evening",
)
def np_handle_evening(c: BaseFunction):
    match c:
        case Evening():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="{{ late in the afternoon | in the late afternoon }}",
)
def pp_handle_late_afternoon(c: BaseFunction):
    match c:
        case LateAfternoon():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="{{ at night | in the night }}",
)
def pp_handle_night(c: BaseFunction):
    match c:
        case Night():
            return {}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template="night",
)
def np_handle_night(c: BaseFunction):
    match c:
        case Night():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_TIME,
    template=f"{{ {GenerationAct.PP.value} [timeInterval] }}",
)
def pp_handle_time_range_constraint(c: BaseFunction[TimeRangeConstraint]):
    if isinstance(c.__value__, TimeRangeConstraint):
        time_interval = Interval(
            lower=c.__value__.start_time, upper=c.__value__.end_time
        )
        return {"timeInterval": ValueCtor(time_interval)}
    return None
