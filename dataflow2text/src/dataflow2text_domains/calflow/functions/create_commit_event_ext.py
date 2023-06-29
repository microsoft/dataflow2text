from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.create_commit_event import CreateCommitEvent
from dataflow2text_domains.calflow.schemas.event_spec import EventSpec


class CreateCommitEventExt:
    @staticmethod
    @function
    def data_constraint(obj: Constraint[EventSpec]) -> Constraint[CreateCommitEvent]:
        def predicate(ev: CreateCommitEvent) -> bool:
            return obj.allows(ev.data)

        return Constraint(type_arg=CreateCommitEvent.dtype_ctor(), underlying=predicate)
