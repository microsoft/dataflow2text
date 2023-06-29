from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.client_command_utils import (
    joinEventCommand,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_JOIN_EVENT_COMMAND,
)
from dataflow2text_domains.calflow.schemas.join_event_command import JoinEventCommand


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_JOIN_EVENT_COMMAND,
    template=f"Connecting to {{ {GenerationAct.NP.value} [event] }}.",
)
def say_connecting_to_event(c: BaseFunction[JoinEventCommand]):
    match c:
        case joinEventCommand(GetAttr(StructAttribute("id", _), event)):
            return {"event": event}
