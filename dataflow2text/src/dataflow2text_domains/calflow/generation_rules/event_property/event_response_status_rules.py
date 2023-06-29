from dataflow2text.dataflow.function import GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_RESPONSE_STATUS,
    get_response_from_response_status,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_RESPONSE_STATUS,
    template=f"{{ {DEFAULT_ACT} [response] }}",
)
def say_response_status(c):
    match c:
        case GetAttr(
            StructAttribute("responseStatus", _),
            _event,
        ) as status:
            return {
                "response": get_response_from_response_status(status),
            }
