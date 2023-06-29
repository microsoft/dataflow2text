import dataclasses
import inspect
import typing
from typing import Any, TypeVar

from dataflow2text.dataflow.function import (
    BaseFunction,
    BooleanCtor,
    GetAttr,
    LongCtor,
    NumberCtor,
    StringCtor,
    ValueCtor,
)
from dataflow2text.dataflow.schema import (
    BaseSchema,
    ComparableSchema,
    NullarySchema,
    NullaryStructSchema,
    StructAttribute,
    StructSchema,
)
from dataflow2text.dataflow.schema_library import SchemaLibrary
from dataflow2text.dataflow.type_name import TypeName


class UnresolvedTypeError(Exception):
    """The error raised when the type cannot be found in the library."""


class TypeMismatchError(Exception):
    """The error raised when the inferred type does not match the type annotation."""


def validate_type(computation: BaseFunction, schema_library: SchemaLibrary) -> None:
    """Validates that the computation passes the type checking given the library."""

    # A sanity check that `reveal_type` does not throw. Failures may suggest bugs in the `reveal_type` implementation.
    _ = computation.reveal_type()

    if isinstance(computation, ValueCtor):
        _validate_value_ctor(computation, schema_library)
    elif isinstance(computation, GetAttr):
        _validate_get_attr(computation, schema_library)
    elif isinstance(computation, StringCtor):
        _validate_string_ctor(computation)
    elif isinstance(computation, BooleanCtor):
        _validate_boolean_ctor(computation)
    elif isinstance(computation, LongCtor):
        _validate_long_ctor(computation)
    elif isinstance(computation, NumberCtor):
        _validate_number_ctor(computation)
    else:
        _validate_computation(computation, schema_library)


def _validate_value_ctor(computation: ValueCtor, schema_library: SchemaLibrary):
    """Validates a ValueCtor computation.

    Here we only need to validate that the type is registered in the library.
    """

    if schema_library.get(computation.inner.dtype) is None:
        raise UnresolvedTypeError(
            f"Cannot find type in the library: {computation.inner.dtype}"
        )


def _validate_string_ctor(computation: StringCtor):
    """Validates a StringCtor computation."""

    if not isinstance(computation.inner, str):
        raise TypeMismatchError(f"Invalid StringCtor computation: ${computation}")


def _validate_boolean_ctor(computation: BooleanCtor):
    """Validates a BooleanCtor computation."""

    if not isinstance(computation.inner, bool):
        raise TypeMismatchError(f"Invalid BooleanCtor computation: ${computation}")


def _validate_long_ctor(computation: LongCtor):
    """Validates a LongCtor computation."""

    if not isinstance(computation.inner, int):
        raise TypeMismatchError(f"Invalid LongCtor computation: ${computation}")


def _validate_number_ctor(computation: NumberCtor):
    """Validates a NumberCtor computation."""

    if not isinstance(computation.inner, float):
        raise TypeMismatchError(f"Invalid NumberCtor computation: ${computation}")


def _validate_get_attr(computation: GetAttr, schema_library: SchemaLibrary):
    """Validates a GetAttr computation.

    Here, we validate the attribute against the object.
    """

    obj_dtype = computation.obj.reveal_type()
    # struct schema is always concrete, e.g., SimpleStruct, ExampleStruct[String, Number]
    struct_schema = schema_library.get(obj_dtype)
    if struct_schema is None:
        raise UnresolvedTypeError(f"Cannot find type in the library: {obj_dtype}")

    # pylint: disable=protected-access
    if isinstance(struct_schema, typing._GenericAlias):  # type: ignore
        # We could also check `hasattr(struct_schema. "__origin__")` instead of using `isinstance`.
        origin = struct_schema.__origin__
        assert len(origin.__parameters__) == len(struct_schema.__args__)
        bindings = dict(zip(origin.__parameters__, struct_schema.__args__))
        _check_struct(origin, computation.attr, schema_library, bindings)
        return

    if issubclass(struct_schema, NullaryStructSchema):
        # When the `struct_schema` is not a GenericAlias, it would be a `NullaryStructSchema`.
        struct_schema = typing.cast(typing.Type[NullaryStructSchema], struct_schema)
        _check_struct(struct_schema, computation.attr, schema_library)
        return

    raise ValueError(f"Unexpected schema: {struct_schema}")


def _validate_computation(computation: BaseFunction, schema_library: SchemaLibrary):
    """Validates the computation which is an instance of dataflow functions defined using the @function decorator."""
    field: dataclasses.Field
    for field in dataclasses.fields(computation):  # type: ignore
        field_value = getattr(computation, field.name)
        field_type = field.type

        if isinstance(field_value, TypeName):
            if field_type is not TypeName:
                raise ValueError(
                    f"Unexpected field ({field_type}) in {computation}: {field_value}"
                )
            continue

        if not isinstance(field_value, BaseFunction):
            raise ValueError(
                f"Unexpected field ({field_type}) in {computation}: {field_value}"
            )

        if field_type.__origin__ != BaseFunction or len(field_type.__args__) != 1:
            raise ValueError(f"Unexpected field type in {computation}: {field}")

        type_annotation = field_type.__args__[0]
        field_value_type = field_value.reveal_type()
        if not _check_type(field_value_type, type_annotation, schema_library):
            raise TypeMismatchError(
                f"Type validation for `{field.name}` failed in {computation}\n{field.type}\n{field_value_type}"
            )

        validate_type(field_value, schema_library)


def _check_struct(
    struct_schema: typing.Type[StructSchema],
    attr: StructAttribute,
    schema_library: SchemaLibrary,
    bindings=None,
):
    """Checks the attribute against the struct schema.

    Raise TypeMismatchError when the attribute type does not match the struct schema.
    """
    type_annotation = None
    for field in dataclasses.fields(struct_schema):  # type: ignore
        if field.name == attr.name:
            field_type = field.type
            if inspect.isclass(field_type) and issubclass(field_type, BaseSchema):
                # a concrete schema
                type_annotation = field_type

            elif isinstance(
                field_type,
                # pylint: disable=protected-access
                typing._GenericAlias,  # type: ignore
            ):
                # e.g., the `type_annotation` is `List[T]`
                type_annotation = field_type

            else:
                type_annotation = bindings[field_type]

            break
    if type_annotation is None:
        raise ValueError(f"{attr.name} is not in {struct_schema}")

    if not _check_type(attr.typ, type_annotation, schema_library):
        raise TypeMismatchError(
            f"{attr.typ} does not match {type_annotation} in {struct_schema}"
        )


def _check_type(
    actual_type: TypeName, type_annotation: Any, schema_library: SchemaLibrary
) -> bool:
    """Returns True if the actual type is allowed by the type annotation.

    In future, we could consider converting both `actual_type` and `type_annotation` to `mypy.types.UnboundType`, and
    then use `mypy.typeanal.TypeAnalyser` to convert them to bound types. Then we may be able to use mypy TypeChecker
    and other functionalities (e.g., `mypy.sametypes.is_same_type` `mypy.subtypes.is_subtype`).
    """

    actual_schema_base = schema_library.get_base(actual_type)
    if actual_schema_base is None:
        raise UnresolvedTypeError(
            f"Cannot find type in the library: {actual_type.base}"
        )

    if type_annotation is BaseSchema:
        return True

    if isinstance(type_annotation, TypeVar):
        type_bound = type_annotation.__bound__
        if type_bound is None:
            return True
        return _check_type(actual_type, type_bound, schema_library)

    if inspect.isclass(type_annotation):
        if issubclass(type_annotation, (NullarySchema, NullaryStructSchema)):
            return issubclass(actual_schema_base, type_annotation)
        if issubclass(type_annotation, ComparableSchema):
            return _is_comparable(actual_schema_base)
        if issubclass(type_annotation, BaseSchema):
            return type_annotation.dtype_ctor() == actual_type

        raise ValueError(
            f"Unexpected annotation: {type_annotation}. Actual type: {actual_type}."
        )

    # pylint: disable=protected-access
    if isinstance(type_annotation, typing._GenericAlias):  # type: ignore
        # e.g., the `type_annotation` is `List[T]`
        type_annotation_origin = type_annotation.__origin__
        assert issubclass(type_annotation_origin, BaseSchema), type_annotation_origin

        if not issubclass(actual_schema_base, type_annotation_origin):
            return False

        if len(type_annotation.__args__) == len(actual_type.type_args):
            for type_arg, annotation_arg in zip(
                actual_type.type_args, type_annotation.__args__
            ):
                if not _check_type(type_arg, annotation_arg, schema_library):
                    return False
            return True
        else:
            # TODO: If `type_annotation` is `ExampleStructBase[T, R]` and `actual_type` is `ExampleStructFoo[String]`
            #  which is a subclass of `ExampleStructBase[T, Number]`, then the assertion would fail, and we should
            #  handle them correctly. For now, we assume the type args are always aligned.
            raise NotImplementedError()

    # If we need to handle other cases, we can consider using `typing.get_origin` and `typing.get_args`.
    raise ValueError(
        f"Unexpected annotation: {type_annotation}. Actual type: {actual_type}."
    )


def _is_comparable(schema: typing.Type[BaseSchema]) -> bool:
    return (
        hasattr(schema, "__lt__")
        and hasattr(schema, "__le__")
        and hasattr(schema, "__gt__")
        and hasattr(schema, "__ge__")
        and hasattr(schema, "__eq__")
    )
