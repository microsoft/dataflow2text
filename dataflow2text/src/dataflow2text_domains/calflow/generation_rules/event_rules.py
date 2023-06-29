from dataflow2text.dataflow.function import BaseFunction, GetAttr, ValueCtor
from dataflow2text.dataflow.schema import Interval, StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.find import FindEventWrapperWithDefaults
from dataflow2text_domains.calflow.functions.list_utils import singleton
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_EVENT,
    get_attendees_from_event,
    get_subject_from_event,
    strip_string,
)
from dataflow2text_domains.calflow.schemas.event import Event


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_EVENT,
    template=(
        f"The {{ {GenerationAct.NP.value} [event] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"{{ {GenerationAct.PP.value} [dateTimeInterval] }}."
    ),
)
def say_event_and_date_time_interval(c: BaseFunction[Event]):
    date_time_interval = Interval(lower=c.__value__.start, upper=c.__value__.end)
    return {
        "event": c,
        "start": ValueCtor(c.__value__.start),
        "dateTimeInterval": ValueCtor(date_time_interval),
    }


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_EVENT,
    template=f'{{{{ "[subject]" | _ }}}} {{ {GenerationAct.PP.value} [dateTimeInterval] }}',
)
def np_say_event_subject_and_date_time_interval(c: BaseFunction[Event]):
    date_time_interval = Interval(lower=c.__value__.start, upper=c.__value__.end)
    return {
        "subject": strip_string(get_subject_from_event(c)),
        "dateTimeInterval": ValueCtor(date_time_interval),
    }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_EVENT,
    template=f"with {{ {GenerationAct.NP.value} [attendees] }}",
)
def pp_say_with_attendees(c: BaseFunction):
    return {
        "attendees": get_attendees_from_event(c),
    }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_EVENT,
    template=f"{{ {GenerationAct.PP.value} [constraint] }}",
)
def pp_handle_singleton(c: BaseFunction):
    match c:
        case singleton(
            GetAttr(
                StructAttribute("results", _), FindEventWrapperWithDefaults(constraint)
            )
        ):
            return {"constraint": constraint}
