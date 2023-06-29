from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date


class DateRangeConstraint(Constraint[Date]):
    def __init__(self, start_date: Date, end_date: Date):
        self.start_date = start_date
        self.end_date = end_date

        def predicate(date: Date) -> bool:
            return start_date <= date <= end_date

        super().__init__(type_arg=Date.dtype_ctor(), underlying=predicate)

    @classmethod
    def dtype_ctor(cls, *type_args: TypeName) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(Date.dtype_ctor())

    @property
    def dtype(self) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(Date.dtype_ctor())
