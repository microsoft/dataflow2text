from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.find import FindEventWrapperWithDefaults
from dataflow2text_domains.calflow.functions.list_utils import head, size
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_QUERY_EVENT_RESPONSE,
    get_search_results,
    get_start_from_event,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_QUERY_EVENT_RESPONSE,
    template=(
        "I {{ didn't find any | found no }} {{ matching events | events }} "
        f"{{{{ on your calendar {{ {GenerationAct.PP.value} [constraint] }} | "
        f"{{ {GenerationAct.PP.value} [constraint] }} | "
        f"{{ {GenerationAct.PP.value} [constraint] }} on your calendar }}}}."
    ),
)
def say_find_no_event(c):
    match c:
        # pylint: disable=used-before-assignment
        case FindEventWrapperWithDefaults(constraint) as search if (
            len(search.__value__.results) == 0
        ):
            return {"constraint": constraint}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_QUERY_EVENT_RESPONSE,
    template=(
        "I found [numEvents] {{ matching event | event | _ }} "
        f"{{{{ on your calendar {{ {GenerationAct.PP.value} [constraint] }} | "
        f"{{ {GenerationAct.PP.value} [constraint] }} | "
        f"{{ {GenerationAct.PP.value} [constraint] }} on your calendar }}}}. "
        f"It {{ {GenerationAct.Copula.value} [start] }} "
        "{{ a | an | the | _ }} "
        f"{{ {GenerationAct.NP.value} [firstEvent] }}."
    ),
)
def say_found_one_event(c):
    # pylint: disable=used-before-assignment
    match c:
        case FindEventWrapperWithDefaults(constraint) as search if (
            len(search.__value__.results) == 1
        ):
            search_results = get_search_results(search)
            first_event = head(search_results)
            return {
                "numEvents": size(search_results),
                "constraint": constraint,
                "start": get_start_from_event(first_event),
                "firstEvent": first_event,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_QUERY_EVENT_RESPONSE,
    template=(
        "I found [numEvents] {{ matching events | events }} "
        f"{{{{ on your calendar {{ {GenerationAct.PP.value} [constraint] }} | "
        f"{{ {GenerationAct.PP.value} [constraint] }} | "
        f"{{ {GenerationAct.PP.value} [constraint] }} on your calendar }}}}. "
        f"The first {{ {GenerationAct.Copula.value} [start] }} "
        "{{ a | an | the | _ }} "
        f"{{ {GenerationAct.NP.value} [firstEvent] }}."
    ),
)
def say_found_n_events(c):
    # pylint: disable=used-before-assignment
    match c:
        case FindEventWrapperWithDefaults(constraint) as search if (
            len(search.__value__.results) > 1
        ):
            search_results = get_search_results(search)
            first_event = head(search_results)
            return {
                "numEvents": size(search_results),
                "constraint": constraint,
                "start": get_start_from_event(first_event),
                "firstEvent": first_event,
            }
