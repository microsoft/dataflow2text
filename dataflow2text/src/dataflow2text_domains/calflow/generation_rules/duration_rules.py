from dataflow2text.dataflow.function import BaseFunction, LongCtor
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_DURATION
from dataflow2text_domains.calflow.schemas.duration import Duration


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DURATION,
    template="{{ an | one | 1 }} hour",
)
def np_say_one_hour(c: BaseFunction[Duration]):
    if c.__value__.nanoseconds.inner != 0:
        return None

    if c.__value__.seconds.inner != 3600:
        return None

    return {}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DURATION,
    template="[num] hours",
)
def np_say_hours(c: BaseFunction[Duration]):
    if c.__value__.nanoseconds.inner != 0:
        return None

    num_hours = int(c.__value__.seconds.inner / 3600)
    if num_hours * 3600 != c.__value__.seconds.inner:
        return None

    if num_hours <= 1:
        return None

    return {"num": LongCtor(num_hours)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DURATION,
    template="a half hour",
)
def np_say_a_half_hour(c: BaseFunction[Duration]):
    if c.__value__.nanoseconds.inner != 0:
        return None

    if c.__value__.seconds.inner != 1800:
        return None

    return {}
