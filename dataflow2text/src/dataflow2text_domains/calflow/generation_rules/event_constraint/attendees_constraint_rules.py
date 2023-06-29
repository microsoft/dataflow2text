from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.constraint_utils import listSize
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    AlwaysTrueConstraint,
    EqualConstraint,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{{{ with | _ }}}} {{{{ attendees | {{ {GenerationAct.NP.value} [constraint] }} }}}}",
)
def pp_handle_event_attendees_constraint(c):
    match c:
        case EventExt.attendees_constraint(constraint):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template="with no attendees",
)
def pp_handle_event_attendees_constraint_no_attendees(c):
    match c:
        # pylint: disable=used-before-assignment
        case EventExt.attendees_constraint(
            listSize(EqualConstraint(numAttendees), AlwaysTrueConstraint(_))
        ) if numAttendees.__value__.inner == 0:
            return {}
