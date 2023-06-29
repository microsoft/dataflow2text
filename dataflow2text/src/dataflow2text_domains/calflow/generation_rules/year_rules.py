from dataflow2text.dataflow.function import BaseFunction, GetAttr, LongCtor
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_YEAR
from dataflow2text_domains.calflow.schemas.year import Year


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_YEAR,
    template=f"The {{ {GenerationAct.NP.value} [event] }} {{ {GenerationAct.VB.value} [end] }} in [year].",
)
def say_event_end_in_year(c: BaseFunction[Year]):
    match c:
        case GetAttr(
            StructAttribute("year", _),
            GetAttr(
                StructAttribute("date", _),
                GetAttr(StructAttribute("end", _), event) as end,
            ),
        ) as year:
            return {"year": LongCtor(year.__value__.inner), "end": end, "event": event}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_YEAR,
    template=f"The {{ {GenerationAct.NP.value} [event] }} {{ {GenerationAct.VB.value} [start] }} in [year].",
)
def say_event_start_in_year(c: BaseFunction[Year]):
    match c:
        case GetAttr(
            StructAttribute("year", _),
            GetAttr(
                StructAttribute("date", _),
                GetAttr(StructAttribute("start", _), event) as start,
            ),
        ) as year:
            return {
                "year": LongCtor(year.__value__.inner),
                "start": start,
                "event": event,
            }
