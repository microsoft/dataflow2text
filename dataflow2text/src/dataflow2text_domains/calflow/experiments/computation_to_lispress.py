"""Helpers to convert CalFlow dataflow computations to Lispress V2."""
import dataclasses
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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
from dataflow2text.dataflow.reentrancy import (
    collect_maximum_spanning_reentrant_computations,
)
from dataflow2text.dataflow.schema import Dynamic, EnumSchema, Option
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.experiments.calflow_constants import (
    DAY_OF_WEEK_SCHEMAS,
    LENGTH_UNIT_SCHEMAS,
    MONTH_SCHEMAS,
    PLACE_FEATURE_SCHEMAS,
    SPECIAL_CALL_LIKE_OP_NAMES,
    WEATHER_QUANTIFIER_SCHEMAS,
)
from dataflow2text_domains.calflow.experiments.lispress.lispress import (
    program_to_lispress,
    render_compact,
)
from dataflow2text_domains.calflow.experiments.lispress.program import (
    Expression,
    Program,
)
from dataflow2text_domains.calflow.experiments.lispress.program import (
    TypeName as LispressTypeName,
)
from dataflow2text_domains.calflow.experiments.lispress.program_utils import (
    Idx,
    is_struct_op_schema,
    mk_call_op,
    mk_struct_op,
    mk_value_op,
)
from dataflow2text_domains.calflow.functions import value_factory
from dataflow2text_domains.calflow.functions.arithmetic import Minus, Plus
from dataflow2text_domains.calflow.functions.calflow_intension_utils import (
    ActionIntensionConstraint,
    Execute,
    QueryEventIntensionConstraint,
    extensionConstraint,
    intension,
)
from dataflow2text_domains.calflow.functions.calflow_yield import Yield
from dataflow2text_domains.calflow.functions.comparison import (
    IsGreaterEqual,
    IsGreaterThan,
    IsLessEqual,
    IsLessThan,
)
from dataflow2text_domains.calflow.functions.confirm import (
    ConfirmAndReturnAction,
    ConfirmUpdateAndReturnActionIntension,
)
from dataflow2text_domains.calflow.functions.constraint_utils import (
    andConstraint,
    negate,
    orConstraint,
)
from dataflow2text_domains.calflow.functions.create_commit_event_ext import (
    CreateCommitEventExt,
)
from dataflow2text_domains.calflow.functions.date_ext import DateExt
from dataflow2text_domains.calflow.functions.date_range_constraints import (
    FullMonthofMonth,
)
from dataflow2text_domains.calflow.functions.date_time_ext import DateTimeExt
from dataflow2text_domains.calflow.functions.do import do
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.functions.event_spec_ext import EventSpecExt
from dataflow2text_domains.calflow.functions.event_utils import EventAttendance
from dataflow2text_domains.calflow.functions.list_utils import singleton, size
from dataflow2text_domains.calflow.functions.missing.calflow_intension_utils import (
    ConstraintTypeIntension,
    ReviseConstraint,
)
from dataflow2text_domains.calflow.functions.missing.choose import (
    ChooseCreateEvent,
    ChooseCreateEventFromConstraint,
)
from dataflow2text_domains.calflow.functions.missing.event_utils import item
from dataflow2text_domains.calflow.functions.missing.salience import NewClobber, refer
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    AlwaysFalseConstraint,
    AlwaysTrueConstraint,
    EmptyStructConstraint,
    EqualConstraint,
    GreaterEqualConstraint,
    GreaterThanConstraint,
    LessEqualConstraint,
    LessThanConstraint,
    alwaysTrueConstraintConstraint,
)
from dataflow2text_domains.calflow.functions.value_factory import (
    Option_apply,
    PeriodDuration_apply,
)
from dataflow2text_domains.calflow.schemas.attendee_type import AttendeeType
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.holiday import Holiday
from dataflow2text_domains.calflow.schemas.length_unit import LengthUnit
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.place_feature import PlaceFeature
from dataflow2text_domains.calflow.schemas.respond_comment import RespondComment
from dataflow2text_domains.calflow.schemas.response_should_send import RespondShouldSend
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)
from dataflow2text_domains.calflow.schemas.sensitivity import Sensitivity
from dataflow2text_domains.calflow.schemas.show_as_status import ShowAsStatus
from dataflow2text_domains.calflow.schemas.weather_quantifier import WeatherQuantifier
from dataflow2text_domains.calflow.schemas.year import Year


@dataclass
class ProgramConstructorState:
    """The mutable state to record the program construction variables."""

    idx_offset: Idx
    # The mapping from `id(computation)` to the corresponding expression `idx` for all reentrant computations.
    reentrant_indices: Dict[int, int]


def _handle_builtin_primitive_ctor(
    computation: BaseFunction, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], Idx]:
    assert isinstance(computation, (BooleanCtor, LongCtor, NumberCtor, StringCtor))
    dtype = computation.reveal_type()
    assert not dtype.type_args
    value = computation.inner
    if isinstance(computation, NumberCtor) and (int_value := int(value)) == value:
        value = int_value
    expression, idx = mk_value_op(
        value,
        dtype.base,
        state.idx_offset,
        type=_convert_type_name(dtype) if fully_typed else None,
    )
    state.idx_offset = idx
    return [expression], idx


def _convert_type_name(
    type_name: TypeName,
) -> LispressTypeName:
    """Converts a dataflow2text TypeName to the corresponding lispress.program.TypeName."""
    return LispressTypeName(
        base=type_name.base,
        type_args=tuple(
            _convert_type_name(type_arg) for type_arg in type_name.type_args
        ),
    )


def _build_arg_expressions(
    computation: BaseFunction, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], List[Idx], List[Optional[str]]]:
    expressions = []
    arg_indices = []
    arg_names = []
    for arg_name, arg_computation in computation.args():
        arg_expressions, arg_idx = _computation_to_expressions(
            arg_computation, state, fully_typed
        )
        expressions.extend(arg_expressions)
        arg_indices.append(arg_idx)
        if fully_typed:
            arg_names.append(arg_name)
        else:
            arg_names.append(None)
    return expressions, arg_indices, arg_names


def _handle_call_like_op(
    computation: BaseFunction,
    state: ProgramConstructorState,
    fully_typed: bool,
) -> Tuple[List[Expression], Idx]:
    expressions, arg_indices, arg_names = _build_arg_expressions(
        computation, state, fully_typed
    )

    maybe_type_arg: Optional[TypeName] = getattr(computation, "type_arg", None)
    if maybe_type_arg is not None:
        assert not isinstance(maybe_type_arg, BaseFunction)
        type_args = [_convert_type_name(maybe_type_arg)]
    elif isinstance(computation, (item,)):
        type_args = [_convert_type_name(computation.t.reveal_type())]  # type: ignore
    else:
        type_args = None

    if fully_typed:
        if isinstance(
            computation, (IsGreaterThan, IsLessThan, IsGreaterEqual, IsLessEqual)
        ):
            type_args = [_convert_type_name(computation.x.reveal_type())]  # type: ignore
        elif isinstance(computation, (Plus, Minus)):
            type_args = [_convert_type_name(computation.x.reveal_type())]  # type: ignore
        elif isinstance(computation, (size, singleton)):
            type_args = [
                _convert_type_name(computation.list.reveal_type().type_args[0])  # type: ignore
            ]
        elif isinstance(computation, (andConstraint,)):
            type_args = [_convert_type_name(computation.c1.reveal_type().type_args[0])]  # type: ignore
        elif isinstance(computation, (orConstraint,)):
            type_args = [
                _convert_type_name(computation.constraint1.reveal_type().type_args[0])  # type: ignore
            ]
        elif isinstance(computation, (refer,)):
            type_args = [
                _convert_type_name(
                    computation.constraint.reveal_type().type_args[0].type_args[0]  # type: ignore
                )
            ]
        elif isinstance(computation, (extensionConstraint, negate)):
            type_args = [
                _convert_type_name(computation.constraint.reveal_type().type_args[0])  # type: ignore
            ]
        elif isinstance(
            computation,
            (
                EqualConstraint,
                GreaterThanConstraint,
                GreaterEqualConstraint,
                LessThanConstraint,
                LessEqualConstraint,
            ),
        ):
            type_args = [_convert_type_name(computation.reference.reveal_type())]  # type: ignore
        elif isinstance(computation, (alwaysTrueConstraintConstraint,)):
            type_args = [
                _convert_type_name(
                    computation.typeConstraint.reveal_type().type_args[0]  # type: ignore
                )
            ]
        elif isinstance(computation, (item,)):
            type_args = [_convert_type_name(computation.t.reveal_type())]  # type: ignore
        elif isinstance(computation, (do,)):
            type_args = [
                _convert_type_name(computation.arg1.reveal_type()),
                _convert_type_name(computation.arg2.reveal_type()),
            ]
        elif isinstance(computation, (intension,)):
            type_args = [
                _convert_type_name(computation.extension.reveal_type()),  # type: ignore
            ]

    op_name = type(computation).__name__
    for key, func in SPECIAL_CALL_LIKE_OP_NAMES.items():
        if isinstance(computation, func):
            op_name = key
            break

    expression, idx = mk_call_op(
        name=op_name,
        args=arg_indices,
        # This is not very elegant, but we do not want to change too much of `mk_call_op` for now.
        arg_names=arg_names
        if any(arg_name is not None for arg_name in arg_names)
        else None,
        type_args=type_args,
        type=_convert_type_name(computation.reveal_type()) if fully_typed else None,
        idx=state.idx_offset,
    )
    state.idx_offset = idx
    return expressions + [expression], idx


def _handle_value_ctor(
    computation: ValueCtor, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], Idx]:
    value = computation.inner

    if isinstance(value, Month):
        op_schema = MONTH_SCHEMAS[value.inner - 1]
    elif isinstance(value, DayOfWeek):
        op_schema = DAY_OF_WEEK_SCHEMAS[value.inner]
    elif isinstance(
        value, (Holiday, Sensitivity, AttendeeType, ShowAsStatus, ResponseStatusType)
    ):
        # enum-like schemas whose `inner` is a `str`.
        assert isinstance(value.inner, str)
        cls = type(value)
        if value.inner == "Null":
            op_schema = f"{cls.__name__}.None"
        else:
            op_schema = f"{cls.__name__}.{value.inner}"
    elif isinstance(value, EnumSchema) and isinstance(value.inner, str):
        enum_cls = type(value)
        op_schema = f"{enum_cls.__name__}.{value.inner}"
    elif isinstance(value, PlaceFeature):
        op_schema = f"PlaceFeature.{PLACE_FEATURE_SCHEMAS[value.inner - 1]}"
    elif isinstance(value, WeatherQuantifier):
        op_schema = f"WeatherQuantifier.{WEATHER_QUANTIFIER_SCHEMAS[value.inner - 1]}"
    elif isinstance(value, LengthUnit):
        op_schema = f"LengthUnit.{LENGTH_UNIT_SCHEMAS[value.inner]}"
    else:
        op_schema = type(value).__name__

    expression, idx = mk_struct_op(
        op_schema,
        args=[],
        idx=state.idx_offset,
        type=_convert_type_name(computation.reveal_type()) if fully_typed else None,
    )
    state.idx_offset = idx
    return [expression], idx


def _handle_event_attendance(
    computation: BaseFunction, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], Idx]:
    assert isinstance(computation, EventAttendance)

    all_expressions: List[Expression] = []
    args: List[Tuple[Optional[str], int]] = []
    comment_computation = computation.comment  # type: ignore
    # In Lispress, `comment` is a positional argument. So it is processed first here.
    if comment_computation != ValueCtor(RespondComment("")):
        arg_expressions, arg_idx = _computation_to_expressions(
            comment_computation, state, fully_typed
        )
        all_expressions.extend(arg_expressions)
        if fully_typed:
            args.append(("comment", arg_idx))
        else:
            args.append((None, arg_idx))

    arg_expressions, arg_idx = _computation_to_expressions(computation.event, state, fully_typed)  # type: ignore
    all_expressions.extend(arg_expressions)
    args.append(("event", arg_idx))

    response_computation = computation.response  # type: ignore
    if response_computation != ValueCtor(ResponseStatusType.Null()):
        arg_expressions, arg_idx = _computation_to_expressions(
            response_computation, state, fully_typed
        )
        all_expressions.extend(arg_expressions)
        args.append(("response", arg_idx))

    send_response_computation = computation.sendResponse  # type: ignore
    if send_response_computation != ValueCtor(RespondShouldSend(True)):
        arg_expressions, arg_idx = _computation_to_expressions(
            send_response_computation, state, fully_typed
        )
        all_expressions.extend(arg_expressions)
        args.append(("sendResponse", arg_idx))

    expression, idx = mk_struct_op(
        "EventAttendance",
        args,
        state.idx_offset,
        type=_convert_type_name(computation.reveal_type()) if fully_typed else None,
    )
    state.idx_offset = idx
    return all_expressions + [expression], idx


def _handle_full_month_of_month(
    computation: BaseFunction, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], Idx]:
    assert isinstance(computation, FullMonthofMonth)

    all_expressions: List[Expression] = []
    args: List[Tuple[Optional[str], int]] = []

    arg_expressions, arg_idx = _computation_to_expressions(computation.month, state, fully_typed)  # type: ignore
    all_expressions.extend(arg_expressions)
    if fully_typed:
        args.append(("month", arg_idx))
    else:
        args.append((None, arg_idx))

    year_computation = computation.year  # type: ignore
    if isinstance(year_computation, Option_apply):
        arg_expressions, arg_idx = _computation_to_expressions(
            # Unwraps the `Option` and use the constructor of `Year`.
            year_computation.value,  # type: ignore
            state,
            fully_typed,
        )
        all_expressions.extend(arg_expressions)
        if fully_typed:
            args.append(("year", arg_idx))
        else:
            args.append((None, arg_idx))
    else:
        assert year_computation == ValueCtor(Option(Year.dtype_ctor(), None))

    expression, idx = mk_struct_op(
        "FullMonthofMonth",
        args,
        state.idx_offset,
        type=_convert_type_name(computation.reveal_type()) if fully_typed else None,
    )
    state.idx_offset = idx
    return all_expressions + [expression], idx


def _handle_period_duration_apply(
    computation: BaseFunction, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], Idx]:
    assert isinstance(computation, PeriodDuration_apply)

    all_expressions: List[Expression] = []
    args: List[Tuple[Optional[str], int]] = []

    period_computation = computation.period  # type: ignore
    if period_computation != ValueCtor(Period()):
        arg_expressions, arg_idx = _computation_to_expressions(
            period_computation, state, fully_typed
        )
        all_expressions.extend(arg_expressions)
        # `period` is a positional argument in Lispress.
        if fully_typed:
            args.append(("period", arg_idx))
        else:
            args.append((None, arg_idx))

    duration_computation = computation.duration  # type: ignore
    if duration_computation != ValueCtor(Duration()):
        arg_expressions, arg_idx = _computation_to_expressions(
            duration_computation, state, fully_typed
        )
        all_expressions.extend(arg_expressions)
        args.append(("duration", arg_idx))

    expression, idx = mk_struct_op(
        "PeriodDuration.apply",
        args,
        state.idx_offset,
        type=_convert_type_name(computation.reveal_type()) if fully_typed else None,
    )
    state.idx_offset = idx
    return all_expressions + [expression], idx


def _handle_build_struct_op(
    computation: BaseFunction, state: ProgramConstructorState, fully_typed: bool
) -> Tuple[List[Expression], Idx]:

    if isinstance(computation, EventAttendance):
        return _handle_event_attendance(computation, state, fully_typed)

    if isinstance(computation, FullMonthofMonth):
        return _handle_full_month_of_month(computation, state, fully_typed)

    if isinstance(computation, PeriodDuration_apply):
        return _handle_period_duration_apply(computation, state, fully_typed)

    all_expressions: List[Expression] = []
    expressions, arg_indices, arg_names = _build_arg_expressions(
        computation, state, fully_typed
    )
    all_expressions.extend(expressions)
    args: List[Tuple[Optional[str], int]] = list(zip(arg_names, arg_indices))

    maybe_type_arg: Optional[TypeName] = getattr(computation, "type_arg", None)
    if maybe_type_arg is not None:
        assert not isinstance(maybe_type_arg, BaseFunction)
        type_args = [_convert_type_name(maybe_type_arg)]
    else:
        type_args = None

    if fully_typed:
        if isinstance(computation, Yield):
            # In SMCalFlow v2.0 fully_typed_lispress, `Yield` has a type arg.
            # But for the normal lispress, the type arg is dropped somehow.
            type_args = [_convert_type_name(computation.output.reveal_type())]
        elif isinstance(
            computation, (Execute, (ChooseCreateEvent, ChooseCreateEventFromConstraint))
        ):
            type_args = [
                _convert_type_name(computation.intension.reveal_type().type_args[0])  # type: ignore
            ]
        elif isinstance(computation, ReviseConstraint):
            type_args = [
                _convert_type_name(computation.rootLocation.reveal_type().type_args[0]),  # type: ignore
                _convert_type_name(computation.new.reveal_type().type_args[0]),  # type: ignore
            ]
        elif isinstance(computation, NewClobber):
            type_args = [
                _convert_type_name(computation.intension.reveal_type().type_args[0]),  # type: ignore
                _convert_type_name(computation.value.reveal_type().type_args[0]),  # type: ignore
            ]

    cls = type(computation)
    op_schema = cls.__name__
    if isinstance(computation, EmptyListCtor):
        op_schema = "List.Nil"
    elif hasattr(value_factory, op_schema) and op_schema.endswith("_apply"):
        units = op_schema.split("_")
        op_schema = f"{units[0]}.apply"
    elif op_schema.endswith("_constraint"):
        op_schema = _handle_constraint_factory(computation)
    elif isinstance(computation, ValueCtor):
        raise NotImplementedError("TBD")
    elif isinstance(computation, GetAttr):
        dtype = computation.obj.reveal_type()
        if dtype.type_args:
            # CalFlow does not have such data
            raise NotImplementedError()
        op_schema = f"{dtype.base}.{computation.attr.name}"

        if (
            fully_typed
            and dtype.base == "Date"
            and computation.attr.name == "dayOfWeek"
        ):
            assert len(args) == 1
            # need to rewrite the argument name for fully_typed_lispress
            args[0] = ("date", args[0][1])
    elif isinstance(
        computation, (ConfirmAndReturnAction, ConfirmUpdateAndReturnActionIntension)
    ):
        type_args = [_convert_type_name(Dynamic.dtype_ctor())]
    elif isinstance(computation, QueryEventIntensionConstraint):
        op_schema = "QueryEventIntensionConstraint"
        dtype = computation.reveal_type()
        assert dtype.base == "Constraint"
        assert len(dtype.type_args) == 1
        type_args = [_convert_type_name(dtype.type_args[0])]
    elif isinstance(
        computation,
        (
            EmptyStructConstraint,
            AlwaysFalseConstraint,
            AlwaysTrueConstraint,
            ActionIntensionConstraint,
            ConstraintTypeIntension,
        ),
    ):
        assert len(type_args) == 1

    expression, idx = mk_struct_op(
        op_schema,
        args,
        state.idx_offset,
        type=_convert_type_name(computation.reveal_type()) if fully_typed else None,
    )
    if type_args is not None:
        expression = dataclasses.replace(expression, type_args=type_args)

    state.idx_offset = idx
    return all_expressions + [expression], idx


def _handle_constraint_factory(c: BaseFunction) -> str:
    cls = type(c)
    units = cls.__name__.split("_")
    assert len(units) == 2
    if cls.__module__ == EventExt.__module__:
        return f"Event.{units[0]}_?"

    if cls.__module__ == EventSpecExt.__module__:
        return f"EventSpec.{units[0]}_?"

    if cls.__module__ == CreateCommitEventExt.__module__:
        return f"CreateCommitEvent.{units[0]}_?"

    if cls.__module__ == DateExt.__module__:
        return f"Date.{units[0]}_?"

    if cls.__module__ == DateTimeExt.__module__:
        return f"DateTime.{units[0]}_?"

    qualname_units = cls.__qualname__.split(".")
    assert len(qualname_units) == 2
    assert qualname_units[0].endswith("Ext"), cls.__qualname__
    return f"{qualname_units[0][:-3]}.{units[0]}_?"


def _is_call_like_op(computation: BaseFunction) -> bool:
    """Returns true if the computation should be converted to a `CallLikeOp`.

    The check is pretty hacky but should work for CalFlow data.
    """
    cls = type(computation)
    if cls in SPECIAL_CALL_LIKE_OP_NAMES.values():
        return True

    name = cls.__name__
    if name.endswith("_constraint"):
        return False
    if name.endswith("_apply"):
        return False
    if is_struct_op_schema(name):
        return False

    return True


def _computation_to_expressions(
    computation: BaseFunction,
    state: ProgramConstructorState,
    fully_typed: bool,
) -> Tuple[List[Expression], Idx]:
    maybe_arg_idx = state.reentrant_indices.get(id(computation))
    if maybe_arg_idx is not None:
        return [], maybe_arg_idx

    if isinstance(computation, (BooleanCtor, LongCtor, NumberCtor, StringCtor)):
        return _handle_builtin_primitive_ctor(computation, state, fully_typed)

    if isinstance(computation, ValueCtor):
        return _handle_value_ctor(computation, state, fully_typed)

    if _is_call_like_op(computation):
        return _handle_call_like_op(computation, state, fully_typed)

    return _handle_build_struct_op(computation, state, fully_typed)


def computation_to_program(
    computation: BaseFunction, fully_typed: bool
) -> Tuple[Program, Idx]:
    reentrant_computations = collect_maximum_spanning_reentrant_computations(
        computation
    )
    state = ProgramConstructorState(idx_offset=0, reentrant_indices={})

    all_expressions = []
    for _, reentrant_computation in enumerate(reentrant_computations):
        expressions, idx = _computation_to_expressions(
            reentrant_computation, state, fully_typed
        )
        all_expressions.extend(expressions)
        state.reentrant_indices[id(reentrant_computation)] = idx

    expressions, root_idx = _computation_to_expressions(computation, state, fully_typed)
    all_expressions.extend(expressions)
    return Program(expressions=all_expressions), root_idx


def computation_to_lispress_str(
    computation: BaseFunction, fully_typed: bool = False
) -> str:
    program, _ = computation_to_program(computation, fully_typed)
    lispress = program_to_lispress(program)
    return render_compact(lispress)
