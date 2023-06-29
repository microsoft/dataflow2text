from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.dataflow.schema import Interval
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_INTERVAL_TIME
from dataflow2text_domains.calflow.schemas.time import Time


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_TIME,
    template=(
        "between "
        f"{{ {GenerationAct.NP.value} [start] }} "
        f"and {{ {GenerationAct.NP.value} [end] }}"
    ),
)
def pp_say_between_time_and_time(c: BaseFunction[Interval[Time]]):
    return {
        "start": ValueCtor(c.__value__.lower),
        "end": ValueCtor(c.__value__.upper),
    }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_TIME,
    template=(
        "from "
        f"{{ {GenerationAct.NP.value} [start] }} "
        f"to {{ {GenerationAct.NP.value} [end] }}"
    ),
)
def pp_say_from_time_to_time(c: BaseFunction[Interval[Time]]):
    return {
        "start": ValueCtor(c.__value__.lower),
        "end": ValueCtor(c.__value__.upper),
    }
