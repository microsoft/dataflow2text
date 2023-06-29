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
        "{{ The | the }} event "
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.VB.value} [end] }} "
        f"{{ {GenerationAct.PP.value} [end] }}."
    ),
)
def say_event_end(c):
    match c:
        case GetAttr(
            StructAttribute("end", _),
            event,
        ) as end:
            return {
                "event": event,
                "end": end,
            }
