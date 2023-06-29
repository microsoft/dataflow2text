import dataclasses
import hashlib
import inspect
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Generic, Tuple, Type, TypeVar, Union

from dataflow2text.dataflow.error import EmptyOptionError
from dataflow2text.dataflow.schema import (
    BaseSchema,
    Boolean,
    List,
    Long,
    NullarySchema,
    Number,
    Option,
    String,
    StructAttribute,
    StructSchema,
    TSchema,
)
from dataflow2text.dataflow.type_inference_helpers import (
    TypeAnnotation,
    TypeNameGetterLookup,
    build_type_name_getters_lookup,
    type_annotation_contains_forward_ref,
)
from dataflow2text.dataflow.type_name import TypeName


class BaseFunction(Generic[TSchema], ABC):
    """The base class of dataflow functions.

    An instance of its subclass is called a dataflow computation, and the subclass itself is called a dataflow function.

    We assume that the function implementation (`__call__`) is immutable, i.e., it is guaranteed to return the same
    result given the arguments of the computation. The behavior would be undefined if this assumption is violated.

    We cannot use `@dataclass` here. See https://github.com/python/mypy/issues/5374.
    """

    @typing.final
    def __call__(self) -> TSchema:
        try:
            return self._call_impl()
        except ExecutionError as e:
            raise dataclasses.replace(e, provenance=e.provenance + [self])
        except Exception as e:
            raise ExecutionError(inner=e, provenance=[self]) from e

    @abstractmethod
    def _call_impl(self) -> TSchema:
        raise NotImplementedError()

    @abstractmethod
    def reveal_type(self) -> TypeName:
        """Reveals the type of the return value.

        Unlike `return_type`, this method runs type inference without executing the computation.
        """
        raise NotImplementedError()

    @typing.final
    @property
    def return_type(self) -> TypeName:
        """The runtime return type of the computation."""
        return self.__value__.dtype

    @typing.final
    @cached_property
    def __value__(self) -> TSchema:
        """Stores the value of the computation.

        If errored during execution, the execution error is stored.
        """
        try:
            return self.__call__()
        except ExecutionError as error:
            # mypy cannot recognize `error` is compatible with `TSchema`
            return error  # type: ignore

    def args(self) -> typing.List[Tuple[str, "BaseFunction"]]:
        return [
            (field.name, arg)
            for field in dataclasses.fields(self)
            if isinstance((arg := getattr(self, field.name)), BaseFunction)
        ]


def hash_computation(c: BaseFunction) -> str:
    return hashlib.sha256(c.__str__().encode("utf-8")).hexdigest()


@dataclasses.dataclass(frozen=True)
class ExecutionError(Exception, NullarySchema):
    """The error raised when a computation execution failed.

    It encapsulates the error and tracks its provenance.
    """

    inner: Exception
    provenance: typing.List[BaseFunction] = dataclasses.field(default_factory=list)


@dataclass(frozen=True)
class ValueCtor(BaseFunction[TSchema]):
    inner: TSchema

    def __post_init__(self):
        assert isinstance(self.inner, BaseSchema)

    def _call_impl(self):
        return self.inner

    def reveal_type(self) -> TypeName:
        return self.inner.dtype


TStructSchema = TypeVar("TStructSchema", bound=StructSchema)


@dataclass(frozen=True)
class GetAttr(Generic[TStructSchema, TSchema], BaseFunction[TSchema]):
    attr: StructAttribute[TSchema]
    obj: BaseFunction[TStructSchema]

    def _call_impl(self) -> TSchema:
        if isinstance(self.obj.__value__, ExecutionError):
            raise self.obj.__value__
        return self.obj.__value__.get_attr(self.attr)

    def reveal_type(self) -> TypeName:
        return self.attr.typ


@dataclass(frozen=True)
class Get(BaseFunction[TSchema]):
    obj: BaseFunction[Option[TSchema]]

    def _call_impl(self) -> TSchema:
        value = self.obj.__value__
        if isinstance(value, ExecutionError):
            raise value

        if isinstance(value, Option):
            if value.inner is None:
                raise EmptyOptionError()
            return value.inner

        raise RuntimeError(f"Unexpected value: {self.obj.__value__}\n{self.obj}")

    def reveal_type(self) -> TypeName:
        type_args = self.obj.reveal_type().type_args
        assert len(type_args) == 1
        return type_args[0]


@dataclass(frozen=True)
class StringCtor(BaseFunction[String]):
    inner: str

    def _call_impl(self) -> String:
        return String(self.inner)

    def reveal_type(self) -> TypeName:
        return String.dtype_ctor()


@dataclass(frozen=True)
class BooleanCtor(BaseFunction[Boolean]):
    inner: bool

    def _call_impl(self) -> Boolean:
        return Boolean(self.inner)

    def reveal_type(self) -> TypeName:
        return Boolean.dtype_ctor()


@dataclass(frozen=True)
class LongCtor(BaseFunction[Long]):
    inner: int

    def _call_impl(self) -> Long:
        return Long(self.inner)

    def reveal_type(self) -> TypeName:
        return Long.dtype_ctor()


@dataclass(frozen=True)
class NumberCtor(BaseFunction[Number]):
    inner: float

    def _call_impl(self) -> Number:
        return Number(self.inner)

    def reveal_type(self) -> TypeName:
        return Number.dtype_ctor()


@dataclass(frozen=True)
class ListCtor(BaseFunction[List[TSchema]]):
    type_arg: TypeName
    inner: typing.List[TSchema]

    def _call_impl(self) -> List[TSchema]:
        return List(self.type_arg, self.inner)

    def reveal_type(self) -> TypeName:
        return List.dtype_ctor(self.type_arg)


@dataclass(frozen=True)
class EmptyListCtor(BaseFunction[List[TSchema]]):
    type_arg: TypeName

    def _call_impl(self) -> List[TSchema]:
        return List(self.type_arg, [])

    def reveal_type(self) -> TypeName:
        return List.dtype_ctor(self.type_arg)


@dataclass(frozen=True)
class OptionCtor(BaseFunction[Option[TSchema]]):
    type_arg: TypeName
    inner: typing.Optional[TSchema]

    def _call_impl(self) -> Option[TSchema]:
        return Option(self.type_arg, self.inner)

    def reveal_type(self) -> TypeName:
        return Option.dtype_ctor(self.type_arg)


@dataclass(frozen=True)
class EmptyOptionCtor(BaseFunction[Option[TSchema]]):
    type_arg: TypeName

    def _call_impl(self) -> Option[TSchema]:
        return Option(self.type_arg, None)

    def reveal_type(self) -> TypeName:
        return Option.dtype_ctor(self.type_arg)


def function(func) -> Type[BaseFunction]:
    """A decorator to convert a native python function to a dataflow function (i.e., a subclass of BaseFunction).

    For example,

    >>> from dataflow2text.dataflow.schema import String
    >>>
    >>> @function
    >>> def Identity(x: String) -> String:
    >>>   return x

    is converted to

    >>> @dataclass(frozen=True)
    >>> class Identity(BaseFunction[String]):
    >>>   x: BaseFunction[String]
    >>>
    >>>   def _call_impl(self) -> String:
    >>>     return self.x()
    >>>
    >>>   def reveal_type(self) -> TypeName:
    >>>     return String.dtype_ctor()

    The former is much less verbose, but the latter has better IDE support.

    We have implemented a Pylint plugin `pylint_dataflow2text.function` to avoid `no-member` errors.

    We may be able to implement a mypy plugin to support better typecheck in future.
    See https://mypy.readthedocs.io/en/stable/extending_mypy.html#extending-mypy-using-plugins

    Note the return annotation need to be either a concrete type or inferrable from the input arguments. Otherwise, we
    cannot use the `@function` decorator and we need to manually define the function class.
    """

    signature = inspect.signature(func)
    return_annotation = signature.return_annotation

    if type_annotation_contains_forward_ref(return_annotation):
        raise ValueError(f"return annotation contains ForwardRef: {signature}")

    param: inspect.Parameter
    for _, param in signature.parameters.items():
        if type_annotation_contains_forward_ref(param.annotation):
            raise ValueError(f"param annotation contains ForwardRef: {signature}")
        if param.name in {"__value__", "return_type"}:
            raise ValueError(f"cannot use reserved keyword {param.name}: {signature}")

    fields: typing.List[
        Union[Tuple[str, type], Tuple[str, type, dataclasses.Field]]
    ] = [
        (
            param.name,
            BaseFunction[param.annotation],  # type: ignore
        )
        if param.default is inspect.Parameter.empty
        else (
            param.name,
            BaseFunction[param.annotation],  # type: ignore
            dataclasses.field(default=ValueCtor(param.default)),  # type: ignore
        )
        for _, param in signature.parameters.items()
    ]
    type_name_getters_lookup: TypeNameGetterLookup = build_type_name_getters_lookup(
        signature
    )

    def call_impl(self):
        kwargs = {f"{field[0]}": getattr(self, field[0]).__value__ for field in fields}
        for _, value in kwargs.items():
            if isinstance(value, ExecutionError):
                raise value

        return func(**kwargs)

    def reveal_type(self) -> TypeName:
        return _reveal_type_helper(self, return_annotation, type_name_getters_lookup)

    cls = dataclasses.make_dataclass(
        cls_name=f"{func.__name__}",
        fields=fields,
        bases=(BaseFunction[return_annotation],),  # type: ignore
        namespace={
            "__module__": func.__module__,
            "__qualname__": func.__qualname__,
            "_call_impl": call_impl,
            "reveal_type": reveal_type,
        },
        frozen=True,
    )
    return cls


def _reveal_type_helper(
    self, annotation: TypeAnnotation, type_name_getters_lookup: TypeNameGetterLookup
) -> TypeName:
    if inspect.isclass(annotation) and issubclass(annotation, BaseSchema):
        return annotation.dtype_ctor()

    if isinstance(annotation, TypeVar):
        param_name, type_name_getter = type_name_getters_lookup[annotation][0]
        param_computation: BaseFunction = getattr(self, param_name)
        return type_name_getter(param_computation.reveal_type())

    # pylint: disable=protected-access
    if isinstance(annotation, typing._GenericAlias):  # type: ignore
        origin: BaseSchema = annotation.__origin__
        type_args = [
            _reveal_type_helper(self, arg, type_name_getters_lookup)
            for arg in annotation.__args__
        ]
        return origin.dtype_ctor(*type_args)

    # If we need to handle other cases, we can consider using `typing.get_origin` and `typing.get_args`.
    raise ValueError(f"Unexpected annotation during reveal_type: {annotation}.")
