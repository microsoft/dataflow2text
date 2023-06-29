from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.time import Time


class TimeRangeConstraint(Constraint[Time]):
    def __init__(self, start_time: Time, end_time: Time):
        self.start_time = start_time
        self.end_time = end_time

        def predicate(dt: Time) -> bool:
            return start_time <= dt <= end_time

        super().__init__(type_arg=Time.dtype_ctor(), underlying=predicate)

    @classmethod
    def dtype_ctor(cls, *type_args: TypeName) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(Time.dtype_ctor())

    @property
    def dtype(self) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(Time.dtype_ctor())
