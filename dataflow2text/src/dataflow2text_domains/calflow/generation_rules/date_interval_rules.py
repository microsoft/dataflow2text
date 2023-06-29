from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.dataflow.schema import Interval
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_INTERVAL_DATE
from dataflow2text_domains.calflow.schemas.date import Date


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE,
    template=(
        "between {{ on | _ }} "
        f"{{ {GenerationAct.NP.value} [start] }} "
        f"and {{ {GenerationAct.NP.value} [end] }}"
    ),
)
def pp_say_between_date_and_date(c: BaseFunction[Interval[Date]]):
    return {
        "start": ValueCtor(c.__value__.lower),
        "end": ValueCtor(c.__value__.upper),
    }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE,
    template=(
        "from "
        f"{{ {GenerationAct.NP.value} [start] }} "
        f"to {{ {GenerationAct.NP.value} [end] }}"
    ),
)
def pp_say_from_date_to_date(c: BaseFunction[Interval[Date]]):
    return {
        "start": ValueCtor(c.__value__.lower),
        "end": ValueCtor(c.__value__.upper),
    }
