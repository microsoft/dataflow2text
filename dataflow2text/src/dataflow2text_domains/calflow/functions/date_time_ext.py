from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.time import Time


class DateTimeExt:
    @staticmethod
    @function
    def date_constraint(obj: Constraint[Date]) -> Constraint[DateTime]:
        def predicate(dt: DateTime) -> bool:
            return obj.allows(dt.date)

        return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def time_constraint(obj: Constraint[Time]) -> Constraint[DateTime]:
        def predicate(dt: DateTime) -> bool:
            return obj.allows(dt.time)

        return Constraint(type_arg=DateTime.dtype_ctor(), underlying=predicate)
