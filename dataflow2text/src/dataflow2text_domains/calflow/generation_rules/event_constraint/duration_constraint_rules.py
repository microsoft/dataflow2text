from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.duration_utils import toHours
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    EqualConstraint,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template="for [num] hours",
)
def pp_handle_event_duration_constraint_plural(c):
    match c:
        # pylint: disable=used-before-assignment
        case EventExt.duration_constraint(
            EqualConstraint(toHours(num))
        ) if num.__value__.inner > 1:
            return {"num": num}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template="for [num] hour",
)
def pp_handle_event_duration_constraint_singular(c):
    match c:
        # pylint: disable=used-before-assignment
        case EventExt.duration_constraint(
            EqualConstraint(toHours(num))
        ) if num.__value__.inner == 1:
            return {"num": num}
