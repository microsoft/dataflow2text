from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.dataflow.schema import Interval
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.date_time_ext import DateTimeExt
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    EqualConstraint,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_DATE_TIME,
)
from dataflow2text_domains.calflow.schemas.date_time_range_constraint import (
    DateTimeRangeConstraint,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_DATE_TIME,
    template=f"{{ {GenerationAct.PP.value} [dateTimeInterval] }}",
)
def pp_handle_date_time_range_constraint(c: BaseFunction[DateTimeRangeConstraint]):
    if isinstance(c.__value__, DateTimeRangeConstraint):
        date_time_interval = Interval(
            lower=c.__value__.start_datetime, upper=c.__value__.end_datetime
        )
        return {"dateTimeInterval": ValueCtor(date_time_interval)}
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_DATE_TIME,
    template=f"{{ {GenerationAct.NP.value} [time] }}",
)
def np_handle_time_constraint(c: BaseFunction):
    match c:
        case DateTimeExt.time_constraint(EqualConstraint(time)):
            return {"time": time}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_DATE_TIME,
    template=f"{{ {GenerationAct.NP.value} [dateTime] }}",
)
def np_handle_equal_constraint(c: BaseFunction):
    match c:
        case EqualConstraint(date_time):
            return {"dateTime": date_time}
