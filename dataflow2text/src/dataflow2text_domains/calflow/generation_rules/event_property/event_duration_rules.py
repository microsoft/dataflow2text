from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_DURATION,
    get_start_from_event,
)
from dataflow2text_domains.calflow.schemas.event import Event


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_DURATION,
    template=(
        "{{ The | the }} {{ event | _ }} "
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"for {{ {GenerationAct.NP.value} [duration] }}."
    ),
)
def say_event_duration_1(c: BaseFunction[Event]):
    match c:
        case GetAttr(
            StructAttribute("duration", _),
            event,
        ) as duration:
            return {
                "event": event,
                "start": get_start_from_event(event),
                "duration": duration,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_DURATION,
    template=(
        "It "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"for {{ {GenerationAct.NP.value} [duration] }}."
    ),
)
def say_event_duration_2(c: BaseFunction[Event]):
    match c:
        case GetAttr(
            StructAttribute("duration", _),
            event,
        ) as duration:
            return {
                "event": event,
                "start": get_start_from_event(event),
                "duration": duration,
            }
