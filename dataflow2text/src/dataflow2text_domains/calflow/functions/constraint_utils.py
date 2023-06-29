from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, List, Number, TSchema
from dataflow2text_domains.calflow.schemas.constraint import Constraint


@function
def andConstraint(
    c1: Constraint[TSchema], c2: Constraint[TSchema]
) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return c1.allows(x) and c2.allows(x)

    return Constraint(type_arg=c1.type_arg, underlying=predicate)


@function
def orConstraint(
    constraint1: Constraint[TSchema], constraint2: Constraint[TSchema]
) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return constraint1.allows(x) or constraint2.allows(x)

    return Constraint(type_arg=constraint1.type_arg, underlying=predicate)


@function
def allows(constraint: Constraint[TSchema], value: TSchema) -> Boolean:
    return Boolean(inner=constraint.allows(value))


@function
def negate(constraint: Constraint[TSchema]) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return not constraint.allows(x)

    return Constraint(type_arg=constraint.type_arg, underlying=predicate)


@function
def exists(constraint: Constraint[TSchema]) -> Constraint[List[TSchema]]:
    def predicate(x: List[TSchema]) -> bool:
        for item in x.inner:
            if constraint.allows(item):
                return True
        return False

    return Constraint(
        type_arg=List.dtype_ctor(constraint.type_arg), underlying=predicate
    )


@function
def listSize(
    constraint: Constraint[Number], typeConstraint: Constraint[List[TSchema]]
) -> Constraint[List[TSchema]]:
    def predicate(x: List[TSchema]) -> bool:
        return constraint.allows(Number(inner=len(x.inner)))

    return Constraint(type_arg=typeConstraint.type_arg, underlying=predicate)
