from dataflow2text.dataflow.function import GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_DATE_TIME


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_DATE_TIME,
    template=(
        "{{ The | the | Your }} {{ event | _ }} "
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"{{ {GenerationAct.PP.value} [start] }}."
    ),
)
def say_event_start_1(c):
    match c:
        case GetAttr(
            StructAttribute("start", _),
            event,
        ) as start:
            return {
                "event": event,
                "start": start,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_DATE_TIME,
    template=(
        "It "
        f"{{ {GenerationAct.VB.value} [start] }} "
        f"{{ {GenerationAct.PP.value} [start] }}."
    ),
)
def say_event_start_2(c):
    match c:
        case GetAttr(
            StructAttribute("start", _),
            _,
        ) as start:
            return {"start": start}
