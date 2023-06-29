from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.attendees_utils import (
    AttendeeListHasRecipientConstraint,
)
from dataflow2text_domains.calflow.functions.constraint_utils import andConstraint
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_LIST_ATTENDEE,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_LIST_ATTENDEE,
    template=(
        f"{{ {GenerationAct.NP.value} [c1] }} "
        "{{ , | _ }} "
        "{{ and | _ }} "
        f"{{ {GenerationAct.NP.value} [c2] }}"
    ),
)
def np_handle_and_constraint(c: BaseFunction):
    match c:
        case andConstraint(c1, c2):
            return {"c1": c1, "c2": c2}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_LIST_ATTENDEE,
    template=f"{{ {GenerationAct.NP.value} [constraint] }}",
)
def np_handle_attendee_list_has_recipient_constraint(c: BaseFunction):
    match c:
        case AttendeeListHasRecipientConstraint(constraint):
            return {"constraint": constraint}
