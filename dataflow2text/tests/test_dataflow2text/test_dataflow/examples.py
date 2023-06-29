from dataclasses import dataclass
from typing import Generic, TypeVar

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.function_library import (
    BUILTIN_FUNCTION_LIBRARY,
    FunctionLibrary,
)
from dataflow2text.dataflow.library import Library
from dataflow2text.dataflow.schema import (
    BaseSchema,
    List,
    Long,
    Number,
    PrimitiveSchema,
    StructSchema,
    TSchema,
)
from dataflow2text.dataflow.schema_library import BUILTIN_SCHEMA_LIBRARY, SchemaLibrary
from dataflow2text.dataflow.type_name import TypeName

_T = TypeVar("_T", bound=BaseSchema)
_R = TypeVar("_R", bound=BaseSchema)


@function
def identity(x: TSchema) -> TSchema:
    return x


@function
def add(x: Number, y: Number) -> Number:
    return Number(x.inner + y.inner)


@function
def add_with_default(x: Number, y: Number = Number(1.0)) -> Number:
    return Number(x.inner + y.inner)


@function
def size(x: List[_T]) -> Long:
    return Long(len(x))


class EmptyListError(Exception):
    pass


class NonSingletonListError(Exception):
    pass


@function
def head(x: List[_T]) -> _T:
    if len(x) == 0:
        raise EmptyListError()
    return x[0]


@function
def singleton(x: List[TSchema]) -> TSchema:
    length = len(x)
    if length == 0:
        raise EmptyListError()

    if length > 1:
        raise NonSingletonListError()

    return x[0]


@dataclass(frozen=True)
class ExampleStruct(Generic[_T, _R], StructSchema):
    """A example struct schema with two type args."""

    x: _T
    y: _R

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor(self.x.dtype, self.y.dtype)


@function
def y0_getter(ex: ExampleStruct[_T, List[_R]]) -> _R:
    return ex.y[0]


@dataclass(frozen=True)
class ExampleColor(PrimitiveSchema):
    """An example schema for Enum."""

    inner: str

    def __post_init__(self):
        assert self.inner in ["Red", "Blue"]

    @classmethod
    def Red(cls):
        return cls(inner="Red")

    @classmethod
    def Blue(cls):
        return cls(inner="Blue")


EXAMPLE_SCHEMA_LIBRARY = BUILTIN_SCHEMA_LIBRARY + SchemaLibrary([ExampleStruct])
EXAMPLE_FUNCTION_LIBRARY = BUILTIN_FUNCTION_LIBRARY + FunctionLibrary([add])
EXAMPLE_LIBRARY = Library(EXAMPLE_SCHEMA_LIBRARY, EXAMPLE_FUNCTION_LIBRARY)
