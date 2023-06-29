"""Helpers to convert CalFlow Lispress V2 programs into dataflow computations."""
import dataclasses
import json
import typing
from inspect import isclass
from typing import Dict, Optional

from more_itertools import first_true

from dataflow2text.dataflow.function import (
    BaseFunction,
    BooleanCtor,
    EmptyListCtor,
    GetAttr,
    LongCtor,
    NumberCtor,
    StringCtor,
    ValueCtor,
)
from dataflow2text.dataflow.function_library import FunctionLibrary
from dataflow2text.dataflow.schema import (
    BaseSchema,
    List,
    NullarySchema,
    StructAttribute,
    StructSchema,
)
from dataflow2text.dataflow.schema_library import SchemaLibrary
from dataflow2text.dataflow.type_inference_helpers import TypeAnnotation
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.experiments.calflow_constants import (
    DAY_OF_WEEK_SCHEMAS,
    MONTH_SCHEMAS,
    SPECIAL_CALL_LIKE_OP_NAMES,
)
from dataflow2text_domains.calflow.experiments.lispress.lispress import (
    Lispress,
    lispress_to_program,
    parse_lispress,
)
from dataflow2text_domains.calflow.experiments.lispress.program import (
    BuildStructOp,
    CallLikeOp,
    Expression,
    Program,
)
from dataflow2text_domains.calflow.experiments.lispress.program import (
    TypeName as LispressTypeName,
)
from dataflow2text_domains.calflow.experiments.lispress.program import ValueOp
from dataflow2text_domains.calflow.functions import value_factory
from dataflow2text_domains.calflow.functions.calflow_intension_utils import (
    ActionIntensionConstraint,
    QueryEventIntensionConstraint,
    roleConstraint,
)
from dataflow2text_domains.calflow.functions.confirm import (
    ConfirmAndReturnAction,
    ConfirmUpdateAndReturnActionIntension,
)
from dataflow2text_domains.calflow.functions.create_commit_event_ext import (
    CreateCommitEventExt,
)
from dataflow2text_domains.calflow.functions.date_ext import DateExt
from dataflow2text_domains.calflow.functions.date_range_constraints import (
    FullMonthofMonth,
)
from dataflow2text_domains.calflow.functions.date_time_ext import DateTimeExt
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.functions.event_spec_ext import EventSpecExt
from dataflow2text_domains.calflow.functions.event_utils import EventAttendance
from dataflow2text_domains.calflow.functions.list_utils import get
from dataflow2text_domains.calflow.functions.missing.calflow_intension_utils import (
    ConstraintTypeIntension,
)
from dataflow2text_domains.calflow.functions.missing.event_utils import item
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    AlwaysFalseConstraint,
    AlwaysTrueConstraint,
    EmptyStructConstraint,
)
from dataflow2text_domains.calflow.functions.value_factory import Option_apply
from dataflow2text_domains.calflow.schemas.create_commit_event import CreateCommitEvent
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_spec import EventSpec
from dataflow2text_domains.calflow.schemas.month import Month


def value_op_to_computation(op: ValueOp) -> BaseFunction:
    value = json.loads(op.value)
    schema = value.get("schema")
    underlying = value.get("underlying")

    if schema == "Long":
        return LongCtor(int(underlying))

    if schema == "Boolean":
        if underlying is True:
            return BooleanCtor(True)
        elif underlying is False:
            return BooleanCtor(False)
        else:
            raise ValueError(f"Unexpected Boolean value: {op.value}")

    if schema == "Number":
        return NumberCtor(float(underlying))

    if schema == "String":
        return StringCtor(str(underlying))

    raise ValueError(f"Unexpected schema: {schema}")


def call_like_op_to_computation(
    op: CallLikeOp,
    type_args: Optional[typing.List[TypeName]],
    arg_ids: typing.List[str],
    program: Program,
    schema_library: SchemaLibrary,
    function_library: FunctionLibrary,
    computation_for_expression_id: typing.Dict[str, BaseFunction],
) -> BaseFunction:
    args = [
        program_to_computation(
            program,
            program.expressions_by_id[arg_id],
            schema_library,
            function_library,
            computation_for_expression_id,
        )
        for arg_id in arg_ids
    ]

    maybe_special_func = SPECIAL_CALL_LIKE_OP_NAMES.get(op.name)
    if maybe_special_func is not None:
        func = maybe_special_func
    else:
        func = function_library.get(op.name)
        assert func is not None, op.name

    if type_args is None:
        return func(*args)

    # ==========================
    # Handles special functions
    # ==========================

    # roleConstraint has an output type arg that were not used in type annotations of arguments.
    if func is roleConstraint:
        assert len(type_args) == 1
        assert len(args) == 1
        return roleConstraint(type_arg=type_args[0], path=args[0])

    # item does not need type arg, but it appears in the Lispress.
    if func is item:
        assert len(type_args) == 1
        assert len(args) == 1
        return item(args[0])  # type: ignore

    raise ValueError(f"Unexpected type args for {op.name}: {type_args}")


def build_struct_op_to_computation(
    op: BuildStructOp,
    type_args: Optional[typing.List[TypeName]],
    arg_ids: typing.List[str],
    program: Program,
    schema_library: SchemaLibrary,
    function_library: FunctionLibrary,
    computation_for_expression_id: typing.Dict[str, BaseFunction],
) -> BaseFunction:
    args = [
        program_to_computation(
            program,
            program.expressions_by_id[arg_id],
            schema_library,
            function_library,
            computation_for_expression_id,
        )
        for arg_id in arg_ids
    ]

    if op.op_schema in MONTH_SCHEMAS:
        assert len(args) == 0
        return _make_month(op)

    if op.op_schema in DAY_OF_WEEK_SCHEMAS:
        assert len(args) == 0
        return _make_day_of_week(op)

    if op.op_schema == "List.Nil":
        assert len(args) == 0
        assert len(type_args) == 1
        return _make_empty_list(type_args[0])

    if op.op_schema.endswith(".apply"):
        return _make_value_factory(op, args, schema_library)

    if op.op_schema.endswith("_?"):
        assert type_args is None
        return _make_constraint_factory(op, args, schema_library)

    if "." in op.op_schema and len(arg_ids) == 0:
        return _make_enum_like(op, schema_library)

    if "." in op.op_schema and len(arg_ids) == 1 and not op.op_schema.endswith("apply"):
        return _make_get_attr(op, args, schema_library)

    schema = schema_library.get(TypeName(op.op_schema))
    if schema is not None:
        args_, kwargs = _build_args_and_kwargs(op, args)
        if type_args is None:
            return ValueCtor(schema(*args_, **kwargs))

        raise ValueError(f"Unexpected op {op} with type args {type_args}")

    return _make_regular_function(op, type_args, args, function_library)


def _make_month(op: BuildStructOp) -> ValueCtor:
    return ValueCtor(Month(MONTH_SCHEMAS.index(op.op_schema) + 1))


def _make_day_of_week(op: BuildStructOp) -> ValueCtor:
    return ValueCtor(DayOfWeek(DAY_OF_WEEK_SCHEMAS.index(op.op_schema)))


def _make_empty_list(type_arg: TypeName) -> EmptyListCtor:
    return EmptyListCtor(type_arg=type_arg)


def _make_enum_like(op: BuildStructOp, schema_library: SchemaLibrary) -> ValueCtor:
    units = op.op_schema.split(".")
    assert len(units) == 2, op.op_schema

    schema = schema_library.get(TypeName(base=units[0]))
    assert schema is not None, op.op_schema
    # TODO: support parameterized schema
    assert issubclass(schema, NullarySchema)

    if units[1] == "None":
        # `None` is a reserved keyword in Python.
        cls_method = getattr(schema, "Null")
    else:
        cls_method = getattr(schema, units[1])
    return ValueCtor(cls_method())


def _make_value_factory(
    op: BuildStructOp,
    args: typing.List[BaseFunction],
    schema_library: SchemaLibrary,
) -> BaseFunction:
    # e.g., PersonName.apply(...) is converted to PersonName_apply(...)
    units = op.op_schema.split(".")
    assert len(units) == 2, op.op_schema

    type_name = TypeName(base=units[0])
    schema = schema_library.get(type_name)
    assert schema is not None, op.op_schema

    args_, kwargs = _build_args_and_kwargs(op, args)
    if issubclass(schema, NullarySchema):
        func = getattr(value_factory, f"{schema.__name__}_apply")
        return func(*args_, **kwargs)

    if issubclass(schema, List):
        # `List.apply` is `get` instead of a constructor.
        assert len(args_) == 2
        return get(args_[0], args_[1])  # type: ignore

    # TODO: support parameterized schema
    raise ValueError(f"Unexpected op: {op}")


def _make_constraint_factory(
    op: BuildStructOp, args: typing.List[BaseFunction], schema_library: SchemaLibrary
) -> BaseFunction:
    # Process constraint macros in CalFlow 2.0, which uses the `_?` suffix, e.g., `Event.subject_?`.
    # We simply change `_?` to `_constraint` to make it valid in Python.
    # These methods are Computation instead of Schema, so we do not need to use ValueCtor.
    # Using Schema would make it harder to do pattern matching.
    # Also, Event.subject_? may take another computation like DateTime.date_?
    units = op.op_schema.split(".")
    assert len(units) == 2, op.op_schema

    type_name = TypeName(base=units[0])
    schema = schema_library.get(type_name)
    assert schema is not None, op.op_schema
    # TODO: support parameterized schema
    assert issubclass(schema, NullarySchema)

    func_name = f"{units[1][:-2]}_constraint"
    # Currently hard-coded for calflow2.
    if schema is Event:
        func = getattr(EventExt, func_name)
    elif schema is EventSpec:
        func = getattr(EventSpecExt, func_name)
    elif schema is CreateCommitEvent:
        func = getattr(CreateCommitEventExt, func_name)
    elif schema is Date:
        func = getattr(DateExt, func_name)
    elif schema is DateTime:
        func = getattr(DateTimeExt, func_name)
    else:
        raise NotImplementedError(f"Unsupported constraint factory computation: {op}.")

    return func(*args)


def _make_get_attr(
    op: BuildStructOp, args: typing.List[BaseFunction], schema_library: SchemaLibrary
) -> GetAttr:
    # e.g., Event.attendees(someEvent) would be converted to
    # GetAttr(someEvent, StructAttribute("attendees", List[Attendee]))
    # This only applies to single-arg ops excluding all `.apply` ops.
    # This check is brittle, and it would only work for CalFlow 2.0 data.
    units = op.op_schema.split(".")
    assert len(units) == 2, op.op_schema

    assert len(args) == 1

    schema = schema_library.get(TypeName(base=units[0]))
    assert schema is not None, op.op_schema
    assert issubclass(schema, StructSchema)

    target_field = first_true(
        dataclasses.fields(schema), pred=lambda x: x.name == units[1]
    )
    assert target_field is not None, op
    type_name = _type_annotation_to_type_name(target_field.type)

    return GetAttr(StructAttribute(units[1], type_name), args[0])


def _make_regular_function(
    op: BuildStructOp,
    type_args: Optional[typing.List[TypeName]],
    args: typing.List[BaseFunction],
    function_library: FunctionLibrary,
) -> BaseFunction:

    func = function_library.get(op.op_schema)
    assert func is not None, op.op_schema

    if func is FullMonthofMonth:
        num_args = len(args)
        if num_args == 1:
            return func(args[0])  # type: ignore
        if num_args == 2:
            # The `FullMonthofMonth` has an optional argument, but Lispress did not wrap it with `Option`.
            return func(args[0], Option_apply(args[1]))  # type: ignore
        raise ValueError(f"Unexpected FullMonthofMonth computation: {op} {args}")

    if func is EventAttendance:
        args_, kwargs = _build_args_and_kwargs(op, args)
        num_positional_args = len(args_)
        if num_positional_args == 0:
            return EventAttendance(**kwargs)
        if num_positional_args == 1:
            # In Lispress, the `comment` is a positional argument.
            assert "comment" not in kwargs
            kwargs["comment"] = args_[0]
            return EventAttendance(**kwargs)
        raise ValueError(f"Unexpected EventAttendance computation: {op} {args}")

    if type_args is None:
        if None in op.op_fields:
            # Some BuildStructOp does not have keyword arguments, so we trust the positional arguments.
            return func(*args)

        args_, kwargs = _build_args_and_kwargs(op, args)
        return func(*args_, **kwargs)

    if func is ConfirmAndReturnAction:
        assert len(type_args) == 1
        assert type_args[0] == TypeName("Dynamic")
        return ConfirmAndReturnAction()

    if func is ConfirmUpdateAndReturnActionIntension:
        assert len(type_args) == 1
        assert type_args[0] == TypeName("Dynamic")
        assert len(args) == 1
        return ConfirmUpdateAndReturnActionIntension(constraint=args[0])  # type: ignore

    if func is QueryEventIntensionConstraint:
        assert len(type_args) == 1
        assert type_args[0] == TypeName(
            "CalflowIntension",
            (TypeName("Constraint", (TypeName("Event"),)),),
        )
        return QueryEventIntensionConstraint()

    if func in {
        EmptyStructConstraint,
        AlwaysFalseConstraint,
        AlwaysTrueConstraint,
        ActionIntensionConstraint,
        ConstraintTypeIntension,
    }:
        assert len(type_args) == 1
        return func(type_arg=type_args[0])  # type: ignore

    raise ValueError(f"Unexpected op {op} with type args {type_args}")


def _build_args_and_kwargs(
    op: BuildStructOp,
    all_args: typing.List[BaseFunction],
) -> typing.Tuple[typing.List[BaseFunction], typing.Dict[str, BaseFunction]]:
    kwargs: typing.Dict[str, BaseFunction] = {}
    args: typing.List[BaseFunction] = []
    for field, arg in zip(op.op_fields, all_args):
        if field is None:
            if kwargs:
                raise ValueError(
                    f"Cannot have positional arguments after keyword arguments: {op}"
                )
            args.append(arg)
        else:
            kwargs[field] = arg
    return args, kwargs


def _type_annotation_to_type_name(
    type_annotation: TypeAnnotation,
) -> TypeName:
    if isclass(type_annotation) and issubclass(type_annotation, NullarySchema):
        return type_annotation.dtype_ctor()

    # pylint: disable=protected-access
    if isinstance(type_annotation, typing._GenericAlias):  # type: ignore
        origin = typing.get_origin(type_annotation)
        assert issubclass(origin, BaseSchema)
        type_args = [
            _type_annotation_to_type_name(type_arg)
            for type_arg in typing.get_args(type_annotation)
        ]
        return origin.dtype_ctor(*type_args)

    if isinstance(type_annotation, typing.TypeVar):
        # TODO: handle TypeVar
        raise NotImplementedError()

    raise ValueError(
        f"Unexpected type annotation: {type_annotation} {type(type_annotation)}"
    )


def program_to_computation(
    program: Program,
    expression: Expression,
    schema_library: SchemaLibrary,
    function_library: FunctionLibrary,
    computation_for_expression_id: typing.Dict[str, BaseFunction],
) -> BaseFunction:
    maybe_computation = computation_for_expression_id.get(expression.id)
    if maybe_computation is not None:
        return maybe_computation

    op = expression.op
    if isinstance(op, ValueOp):
        computation = value_op_to_computation(op)
        computation_for_expression_id[expression.id] = computation
        return computation

    if expression.type_args is not None:
        type_args = list(map(_convert_type_name, expression.type_args))
    else:
        type_args = None

    if isinstance(op, CallLikeOp):
        computation = call_like_op_to_computation(
            op,
            type_args,
            expression.arg_ids,
            program,
            schema_library,
            function_library,
            computation_for_expression_id,
        )
        computation_for_expression_id[expression.id] = computation
        return computation

    if isinstance(op, BuildStructOp):
        computation = build_struct_op_to_computation(
            op,
            type_args,
            expression.arg_ids,
            program,
            schema_library,
            function_library,
            computation_for_expression_id,
        )
        computation_for_expression_id[expression.id] = computation
        return computation

    raise ValueError(f"unknown op: ${op.__str__()}")


def _convert_type_name(
    type_name: LispressTypeName,
) -> TypeName:
    """Converts a lispress.program.TypeName to a dataflow2text TypeName."""
    return TypeName(
        base=type_name.base,
        type_args=tuple(
            _convert_type_name(type_arg) for type_arg in type_name.type_args
        ),
    )


def lispress_to_computation(
    lispress: Lispress,
    schema_library: SchemaLibrary,
    function_library: FunctionLibrary,
) -> BaseFunction:
    program, _ = lispress_to_program(lispress, 0)
    expression_id_for_computation: Dict[str, BaseFunction] = {}
    return program_to_computation(
        program,
        # TODO: why drop the last expression?
        program.expressions[-1],
        schema_library,
        function_library,
        expression_id_for_computation,
    )


def lispress_str_to_computation(
    lispress_str: str,
    schema_library: SchemaLibrary,
    function_library: FunctionLibrary,
) -> BaseFunction:
    lispress = parse_lispress(lispress_str)
    return lispress_to_computation(lispress, schema_library, function_library)
