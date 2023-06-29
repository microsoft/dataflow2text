from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek


@function
def Weekdays() -> Constraint[DayOfWeek]:
    def predicate(dow: DayOfWeek) -> bool:
        return dow not in (DayOfWeek.Saturday(), DayOfWeek.Sunday())

    return Constraint(type_arg=DayOfWeek.dtype_ctor(), underlying=predicate)


@function
def Weekend() -> Constraint[DayOfWeek]:
    def predicate(dow: DayOfWeek) -> bool:
        return dow in (DayOfWeek.Saturday(), DayOfWeek.Sunday())

    return Constraint(type_arg=DayOfWeek.dtype_ctor(), underlying=predicate)
