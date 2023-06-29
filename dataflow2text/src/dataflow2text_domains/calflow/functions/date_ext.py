from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.month import Month


class DateExt:
    @staticmethod
    @function
    def month_constraint(obj: Constraint[Month]) -> Constraint[Date]:
        raise NotImplementedError()

    @staticmethod
    @function
    def day_constraint(obj: Constraint[Day]) -> Constraint[Date]:
        raise NotImplementedError()

    @staticmethod
    @function
    def dayOfWeek_constraint(date: Constraint[DayOfWeek]) -> Constraint[Date]:
        def predicate(d: Date) -> bool:
            return date.allows(d.dayOfWeek)

        return Constraint(type_arg=Date.dtype_ctor(), underlying=predicate)
