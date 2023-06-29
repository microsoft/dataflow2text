from dataclasses import dataclass

from dataflow2text.dataflow.function import BaseFunction, function
from dataflow2text.dataflow.schema import String, TComparableSchema, TSchema
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.constraint import Constraint


@function
def EqualConstraint(
    reference: TSchema,
) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        return x == reference

    return Constraint(type_arg=reference.dtype, underlying=predicate)


def _string_fuzzy_match(reference: str, value: str) -> bool:
    """Returns true if the `value` fuzzy matches the `reference`.

    To be conservative, we do not relax these condition to be "any token overlap".

    Note we cannot simply stem the reference due to other examples in the data, e.g.,
    - 8746c6d7-31ad-44cb-bb63-77e7207aca80 assumed `_string_fuzzy_match("therapy sessions", "therapy session") == False`.
    """

    if reference in value:
        # Returns true if the `reference` is a substring of `value`.
        return True

    reference_tokens = reference.split(" ")
    if reference_tokens[-1] in {
        "meeting",
        "meetings",
        "appointment",
        "appointments",
    }:
        reference_tokens = reference_tokens[:-1]
    if " ".join(reference_tokens) in value:
        # e.g., `reference` is "work meetings", and `value` is "February Work Meeting".
        return True

    # In some dialogue (e.g., 6db6983e-975f-4769-bc23-20948aae7d66), "doctors appointment" fuzzy matches is "doctor",
    # but this is not always the case (e.g., ffd04e75-f747-4f6f-8f2f-76972adf082d)
    # if reference_tokens == ["doctors"] and value == "doctor":
    #     return True

    return False


@function
def FuzzyEqualConstraint(
    reference: TSchema,
) -> Constraint[TSchema]:
    def predicate(x: TSchema) -> bool:
        if isinstance(x, String) and isinstance(reference, String):
            return _string_fuzzy_match(reference.inner.lower(), x.inner.lower())

        return x == reference

    return Constraint(type_arg=reference.dtype, underlying=predicate)


@function
def GreaterEqualConstraint(
    reference: TComparableSchema,
) -> Constraint[TComparableSchema]:
    def predicate(x: TComparableSchema) -> bool:
        return x >= reference

    return Constraint(type_arg=reference.dtype, underlying=predicate)


@function
def LessEqualConstraint(reference: TComparableSchema) -> Constraint[TComparableSchema]:
    def predicate(x: TComparableSchema) -> bool:
        return x <= reference

    return Constraint(type_arg=reference.dtype, underlying=predicate)


@function
def LessThanConstraint(reference: TComparableSchema) -> Constraint[TComparableSchema]:
    def predicate(x: TComparableSchema) -> bool:
        return x < reference

    return Constraint(type_arg=reference.dtype, underlying=predicate)


@function
def GreaterThanConstraint(
    reference: TComparableSchema,
) -> Constraint[TComparableSchema]:
    def predicate(x: TComparableSchema) -> bool:
        return x > reference

    return Constraint(type_arg=reference.dtype, underlying=predicate)


@function
def alwaysTrueConstraintConstraint(
    typeConstraint: Constraint[TSchema],
) -> Constraint[Constraint[TSchema]]:
    def predicate(x: Constraint[TSchema]) -> bool:
        return x.type_arg == typeConstraint.type_arg

    return Constraint(
        type_arg=Constraint.dtype_ctor(typeConstraint.type_arg),
        underlying=predicate,
    )


@dataclass(frozen=True)
class EmptyStructConstraint(BaseFunction[Constraint[TSchema]]):
    """Returns an always-true constraint for a given struct schema.

    In Lispress/Express, the signature is
        def EmptyStructConstraint[T](): Constraint[T]

    In Python, we have to pass the type arg as an argument to the computation.
    Therefore, we cannot use the `@function` decorator.
    """

    type_arg: TypeName

    def _call_impl(self) -> Constraint[TSchema]:
        def predicate(x: TSchema) -> bool:
            return True

        return Constraint(type_arg=self.type_arg, underlying=predicate)

    def reveal_type(self) -> TypeName:
        return Constraint.dtype_ctor(self.type_arg)


@dataclass(frozen=True)
class AlwaysFalseConstraint(BaseFunction[Constraint[TSchema]]):
    type_arg: TypeName

    def _call_impl(self) -> Constraint[TSchema]:
        def predicate(x: TSchema) -> bool:
            return False

        return Constraint(type_arg=self.type_arg, underlying=predicate)

    def reveal_type(self) -> TypeName:
        return Constraint.dtype_ctor(self.type_arg)


@dataclass(frozen=True)
class AlwaysTrueConstraint(BaseFunction[Constraint[TSchema]]):
    type_arg: TypeName

    def _call_impl(self) -> Constraint[TSchema]:
        def predicate(x: TSchema) -> bool:
            return True

        return Constraint(type_arg=self.type_arg, underlying=predicate)

    def reveal_type(self) -> TypeName:
        return Constraint.dtype_ctor(self.type_arg)
