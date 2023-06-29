from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_TIME,
    stringify_time,
)
from dataflow2text_domains.calflow.schemas.time import Time


@generation(act=DEFAULT_ACT, typ=DTYPE_TIME, template=f"{{ {DEFAULT_ACT} [dateTime] }}")
def say_it_start_at_time(c: BaseFunction[Time]):
    match c:
        case GetAttr(StructAttribute("time", _), date_time):
            return {"dateTime": date_time}


@generation(act=GenerationAct.NP.value, typ=DTYPE_TIME, template="[timeStr]")
def say_stringify_time_with_ampm(c: BaseFunction[Time]):
    return {"timeStr": stringify_time(c, True)}


@generation(act=GenerationAct.NP.value, typ=DTYPE_TIME, template="[timeStr]")
def say_stringify_time_without_ampm(c: BaseFunction[Time]):
    return {"timeStr": stringify_time(c, False)}
