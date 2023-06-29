from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)


@dataclass(frozen=True)
class AttendanceResponse(NullaryStructSchema):
    status: ResponseStatusType
