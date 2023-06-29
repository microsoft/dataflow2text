from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import Boolean, StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.comparison import (
    IsEqual,
    IsGreaterThan,
    IsLessThan,
)
from dataflow2text_domains.calflow.functions.constraint_utils import allows
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_BOOLEAN,
    get_start_from_event,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_BOOLEAN,
    template="It doesn't look like it.",
)
def say_it_does_not_look_like_it(c: BaseFunction):
    if c.__value__ == Boolean(False):
        return {}
    return None


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_BOOLEAN,
    template="{{ Looks like it. | Looks like it.. }}",
)
def say_looks_like_it(c: BaseFunction):
    if c.__value__ == Boolean(True):
        return {}
    return None


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_BOOLEAN,
    template=f"{{ {GenerationAct.UH.value} [result] }} {{{{ , | . }}}} {{ {DEFAULT_ACT} [query] }}",
)
def say_comparison_result_and_query(c: BaseFunction):
    match c:
        case IsGreaterThan(query, _) as result:
            return {"query": query, "result": result}
        case IsLessThan(query, _) as result:
            return {"query": query, "result": result}
        case IsEqual(query, _) as result:
            return {"query": query, "result": result}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_BOOLEAN,
    template=(
        f"{{ {GenerationAct.UH.value} [result] }} {{{{ , | . }}}} "
        f"{{ {GenerationAct.NP.value} [value] }} is {{ {GenerationAct.NP.value} [query] }}."
    ),
)
def say_yes_and_value_is_query(c: BaseFunction):
    # pylint: disable=used-before-assignment
    match c:
        case IsEqual(value, query) as result if result.__value__ == Boolean(True):
            return {"result": result, "query": query, "value": value}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_BOOLEAN,
    template=(
        f"{{ {GenerationAct.UH.value} [result] }}, "
        f"{{ {GenerationAct.NP.value} [person] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        "invited to {{ the | _ }} "
        f"{{ {GenerationAct.NP.value} [event] }}."
    ),
)
def say_result_and_person_invited_to_event(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case allows(
            person,
            GetAttr(StructAttribute("attendees", _), event),
        ) as result if result.__value__ == Boolean(True):
            return {
                "result": result,
                "person": person,
                "event": event,
                "start": get_start_from_event(event),
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_BOOLEAN,
    template=(
        f"{{ {GenerationAct.UH.value} [result] }}, "
        f"{{ {GenerationAct.NP.value} [person] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        "not invited to {{ the | _ }} "
        f"{{ {GenerationAct.NP.value} [event] }}."
    ),
)
def say_result_and_person_not_invited_to_event(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case allows(
            person,
            GetAttr(StructAttribute("attendees", _), event),
        ) as result if result.__value__ == Boolean(False):
            return {
                "result": result,
                "person": person,
                "event": event,
                "start": get_start_from_event(event),
            }


@generation(act=GenerationAct.UH.value, typ=DTYPE_BOOLEAN, template="Yes")
def say_yes(c: BaseFunction):
    if c.__value__ == Boolean(True):
        return {}
    return None


@generation(GenerationAct.UH.value, typ=DTYPE_BOOLEAN, template="No")
def say_no(c: BaseFunction):
    if c.__value__ == Boolean(False):
        return {}
    return None
