from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.person_utils import (
    CurrentUser,
    FindManager,
    toRecipient,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_RECIPIENT,
    get_person_name_from_recipient,
)
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_RECIPIENT,
    template="{{ you | You }}",
)
def np_say_you(c: BaseFunction[Recipient]):
    if c.__value__.emailAddress.inner == CurrentUser().__value__.emailAddress:
        return {}
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_RECIPIENT,
    template=f"{{ {GenerationAct.NP.value} [name] }}",
)
def np_say_recipient_name(c: BaseFunction[Recipient]):
    return {"name": get_person_name_from_recipient(c)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_RECIPIENT,
    template="your manager",
)
def say_your_manager(c: BaseFunction[Recipient]):
    match c:
        case FindManager(toRecipient(CurrentUser())):
            return {}
