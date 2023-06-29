from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import Long, StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT, TOSTRING_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.find import FindEventWrapperWithDefaults
from dataflow2text_domains.calflow.functions.list_utils import size
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_LIST_ATTENDEE,
    DTYPE_LONG,
)


@generation(act=DEFAULT_ACT, typ=DTYPE_LONG, template="{S [search]}")
def say_search_results(c: BaseFunction):
    match c:
        case size(
            GetAttr(
                StructAttribute("results", _), FindEventWrapperWithDefaults(_) as search
            )
        ):
            return {"search": search}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_LONG,
    template=f"I found [n] {{{{ attendee | attendees }}}} {{ {GenerationAct.SBAR.value} [x] }} {{{{ ! | . }}}}",
)
def say_i_found_n_attendees(c: BaseFunction[Long]):
    match c:
        # pylint: disable=used-before-assignment
        case size(x) as n if x.return_type == DTYPE_LIST_ATTENDEE:
            return {"n": n, "x": x}


@generation(act=GenerationAct.Ordinal.value, typ=DTYPE_LONG, template="[num]st")
def say_ordinal_st(num: BaseFunction[Long]):
    if num.__value__.inner % 10 == 1 and num.__value__.inner != 11:
        return {"num": num}
    return None


@generation(act=GenerationAct.Ordinal.value, typ=DTYPE_LONG, template="[num]nd")
def say_ordinal_nd(num: BaseFunction[Long]):
    if num.__value__.inner % 10 == 2 and num.__value__.inner != 12:
        return {"num": num}
    return None


@generation(act=GenerationAct.Ordinal.value, typ=DTYPE_LONG, template="[num]rd")
def say_ordinal_rd(num: BaseFunction[Long]):
    if num.__value__.inner % 10 == 3 and num.__value__.inner != 13:
        return {"num": num}
    return None


@generation(act=GenerationAct.Ordinal.value, typ=DTYPE_LONG, template="[num]th")
def say_ordinal_th(num: BaseFunction[Long]):
    return {"num": num}


@generation(act=TOSTRING_ACT, typ=DTYPE_LONG, template="one")
def say_one(num: BaseFunction[Long]):
    if num.__value__.inner == 1:
        return {}
    return None


@generation(act=TOSTRING_ACT, typ=DTYPE_LONG, template="two")
def say_two(num: BaseFunction[Long]):
    if num.__value__.inner == 2:
        return {}
    return None


@generation(act=TOSTRING_ACT, typ=DTYPE_LONG, template="three")
def say_three(num: BaseFunction[Long]):
    if num.__value__.inner == 3:
        return {}
    return None
