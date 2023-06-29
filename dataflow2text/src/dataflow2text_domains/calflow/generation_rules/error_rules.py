from typing import Callable, Dict, Optional

from dataflow2text.dataflow.function import BaseFunction, ExecutionError, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.errors.calflow_runtime_error import (
    EmptyListError,
    UpdateEventOrganizedByOtherUserError,
)
from dataflow2text_domains.calflow.functions.find import (
    FindEventWrapperWithDefaults,
    FindLastEvent,
)
from dataflow2text_domains.calflow.functions.list_utils import singleton
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct


def thrown_by(
    error: ExecutionError,
    error_matcher_body: Callable[[BaseFunction], Optional[Dict[str, BaseFunction]]],
) -> Optional[Dict[str, BaseFunction]]:
    for computation in error.provenance:
        result = error_matcher_body(computation)
        if result is not None:
            return result
    return None


@generation(
    act=DEFAULT_ACT,
    # TODO: We should describe the constraint at the end instead of hard-code the "after right now" etc.
    template=(
        "I {{ didn't find any | found no }} {{ matching events | events | _ }} "
        f"{{ {GenerationAct.PP.value} [constraint] }} "
        "{{ on your calendar | _ }} "
        f"{{ {GenerationAct.PP.value} [constraint] }} "
        "{{ after right now | from now until the end of the day | _ }}."
    ),
)
def say_no_event_thrown_by_singleton(c: BaseFunction):
    def error_matcher_body(computation: BaseFunction):
        match computation:
            case singleton(
                GetAttr(
                    StructAttribute("results", _),
                    FindEventWrapperWithDefaults(constraint),
                )
            ):
                return {"constraint": constraint}

    match c.__value__:
        # pylint: disable=used-before-assignment
        case ExecutionError(inner, _) as error if isinstance(inner, EmptyListError):
            return thrown_by(error, error_matcher_body)


@generation(
    act=DEFAULT_ACT,
    template=(
        "I {{ didn't find any | found no }} {{ matching events | events | _ }} "
        f"{{ {GenerationAct.PP.value} [constraint] }} "
        "from now until the end of the day."
    ),
)
def say_no_event_thrown_by_find_last_event(c: BaseFunction):
    def error_matcher_body(computation: BaseFunction):
        match computation:
            case FindLastEvent(constraint):
                return {"constraint": constraint}

    match c.__value__:
        # pylint: disable=used-before-assignment
        case ExecutionError(inner, _) as error if isinstance(inner, EmptyListError):
            return thrown_by(error, error_matcher_body)


@generation(
    act=DEFAULT_ACT, template="I'm unable to update events you didn't organize."
)
def handle_update_event_organized_by_other_user_error(c: BaseFunction):

    match c.__value__:
        # pylint: disable=used-before-assignment
        case ExecutionError(inner, _) if isinstance(
            inner, UpdateEventOrganizedByOtherUserError
        ):
            return {}
