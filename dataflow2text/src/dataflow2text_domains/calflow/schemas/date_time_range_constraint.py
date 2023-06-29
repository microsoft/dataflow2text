from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date_time import DateTime


class DateTimeRangeConstraint(Constraint[DateTime]):
    def __init__(self, start_datetime: DateTime, end_datetime: DateTime):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        def predicate(dt: DateTime) -> bool:
            return start_datetime <= dt <= end_datetime

        super().__init__(type_arg=DateTime.dtype_ctor(), underlying=predicate)

    @classmethod
    def dtype_ctor(cls, *type_args: TypeName) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(DateTime.dtype_ctor())

    @property
    def dtype(self) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(DateTime.dtype_ctor())
