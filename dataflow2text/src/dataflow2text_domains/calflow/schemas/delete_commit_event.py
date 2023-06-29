from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema


@dataclass(frozen=True)
class DeleteCommitEvent(NullaryStructSchema):
    pass
