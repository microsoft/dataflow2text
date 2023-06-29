from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.constraint_utils import andConstraint
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [c1] }} {{ {GenerationAct.PP.value} [c2] }}",
)
def pp_handle_and_constraint(c: BaseFunction):
    match c:
        case andConstraint(c1, c2):
            return {"c1": c1, "c2": c2}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [c1] }} {{ {GenerationAct.PP.value} [c2] }}",
)
def pp_handle_and_constraint_swapped(c: BaseFunction):
    """Like `pp_handle_and_constraint`, with `c1` and `c2` swapped."""
    match c:
        case andConstraint(c2, c1):
            return {"c1": c1, "c2": c2}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"between {{ {GenerationAct.PP.value} [start] }} and {{ {GenerationAct.PP.value} [end] }}",
)
def pp_say_between_start_and_end(c: BaseFunction):
    match c:
        case andConstraint(
            EventExt.start_constraint(start),
            EventExt.end_constraint(end),
        ):
            return {"start": start, "end": end}
