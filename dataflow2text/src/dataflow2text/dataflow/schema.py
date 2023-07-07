# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import dataclasses
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from dataflow2text.dataflow.type_name import TypeName


class BaseSchema(ABC):
    """The base class of dataflow schemas.

    An instance of its subclass is called a dataflow value, and the subclass itself is called a dataflow schema.
    A dataflow value has a dataflow type (i.e., `dtype`).
    A dataflow schema has a dtype constructor (i.e., `dtype_ctor`).

    >>> string_dvalue = String("foo")
    >>> dschema = type(string_dvalue)
    >>> assert dschema == String
    >>> assert string_dvalue.dtype == String.dtype_ctor()

    When a dataflow schema is a Generic class, the type arg of the Generic class should always be `TSchema`.
    Otherwise, there is no way to derive the dataflow type correctly. We can add this check in the `__post_init__`
    method in future (assuming all dataflow schemas are dataclasses).

    For enum types, we use `classmethod` to implement the schema, e.g.,

    >>> @dataclass(frozen=True)
    >>> class Color(EnumSchema):
    >>>   inner: str
    >>>
    >>>   def __post_init__(self):
    >>>     assert self.inner in ["Red", "Blue"]
    >>>
    >>>   @classmethod
    >>>   def Red(cls):
    >>>     return cls("Red")
    >>>
    >>>   @classmethod
    >>>   def Blue(cls):
    >>>     return cls("Blue")

    This is a little verbose, but has much better support in IDE, pylint, and mypy, compared with
    the approach that uses a decorator to convert a `Enum` class into a `NullarySchema`.
    """

    @classmethod
    def dtype_base(cls) -> str:
        """Returns the base of the dataflow type."""
        return cls.__name__

    @classmethod
    def dtype_ctor(cls, *type_args: TypeName) -> TypeName:
        """Constructs the dataflow type of the schema using the provided type args."""
        actual_num_type_args = len(type_args)
        if issubclass(cls, typing.Generic):  # type: ignore
            expected_num_type_args = len(cls.__parameters__)  # type: ignore
        else:
            expected_num_type_args = 0
        if actual_num_type_args != expected_num_type_args:
            raise ValueError(
                f"Expected {expected_num_type_args} type arg(s) for {cls}, but got {type_args}."
            )
        return TypeName(cls.dtype_base(), type_args)

    @property
    @abstractmethod
    def dtype(self) -> TypeName:
        """Returns the dataflow type of the dataflow value."""
        raise NotImplementedError()


TSchema = TypeVar("TSchema", bound=BaseSchema)


class NullarySchema(BaseSchema, ABC):
    """The base class for dataflow schemas without any type arg."""

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor()


@dataclass(frozen=True)
class Unit(NullarySchema):
    pass


class PrimitiveSchema(NullarySchema, ABC):
    """The base class of primitive dataflow schemas.

    For primitive schemas, we cannot use the `GetAttr` computation to obtain the encapsulated value.
    """

    def __init__(self, inner):
        self.inner = inner

    @classmethod
    def from_typed_json(cls, json_obj: typing.Dict[str, typing.Any]):
        schema_ = json_obj.get("schema")
        if schema_ != cls.__name__:
            raise ValueError(
                f"Unable to construct a {cls} value due to mismatched schema: {json_obj}."
            )

        underlying = json_obj.get("underlying")
        if underlying is None:
            raise ValueError(
                f"Unable to create a {cls} value due to null underlying: {json_obj}."
            )
        return cls(inner=underlying)


class EnumSchema(PrimitiveSchema, ABC):
    """The base class of enum schemas.

    The implementation is empty now, but we need to distinguish EnumSchema from other PrimitiveSchema so
    we can render them differently.
    For example, we would like to render `Color.Red()` as `Color.Red` instead of `Color("Red")`.
    """


@dataclass(frozen=True)
class String(PrimitiveSchema):
    inner: str

    def __post_init__(self):
        assert isinstance(self.inner, str), self.inner


@dataclass(frozen=True)
class Boolean(PrimitiveSchema):
    inner: bool

    def __post_init__(self):
        assert isinstance(self.inner, bool)


@dataclass(frozen=True, order=True)
class Long(PrimitiveSchema):
    inner: int

    def __post_init__(self):
        assert isinstance(self.inner, int)


@dataclass(order=True)
class Number(PrimitiveSchema):
    """The Number schema which encapsulates a float value.

    Cannot use `@dataclass(frozen=True)` since the `__post_init__` modifies the `inner`.
    """

    inner: float

    def __post_init__(self):
        if isinstance(self.inner, int):
            self.inner = float(self.inner)
        assert isinstance(self.inner, float)

    def to_long(self) -> Long:
        return Long(inner=int(self.inner))


@dataclass(frozen=True)
class Option(Generic[TSchema], BaseSchema):
    # TODO: See if we can define `__init__` so we don't need to provide type_arg every time.
    #  Then we can get rid of the `from_value` method.
    type_arg: TypeName
    inner: typing.Optional[TSchema]

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor(self.type_arg)

    @classmethod
    def from_value(cls, value: TSchema) -> "Option[TSchema]":
        assert value is not None
        return Option(type_arg=value.dtype, inner=value)

    def get(self) -> TSchema:
        if self.inner is None:
            raise ValueError(f"Cannot call `get` on {self}")
        return self.inner


@dataclass(frozen=True)
class List(Generic[TSchema], BaseSchema):
    # TODO: See if we can define __init__ so we don't need to provide type_arg every time.
    type_arg: TypeName
    inner: typing.List[TSchema]

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor(self.type_arg)

    @classmethod
    def from_value(cls, value: typing.List[TSchema]) -> "List[TSchema]":
        assert len(value) > 0
        return List(type_arg=value[0].dtype, inner=value)

    def __len__(self) -> int:
        return len(self.inner)

    def __getitem__(self, item):
        return self.inner[item]

    def __setitem__(self, key, value):
        self.inner[key] = value


@dataclass(frozen=True)
class Dynamic(NullarySchema):
    type_arg: TypeName
    inner: BaseSchema


@dataclass(frozen=True)
class StructAttribute(Generic[TSchema]):
    """An attribute of a struct schema.

    Note this is not a schema.
    """

    # The name of the attribute.
    name: str
    # The type of the attribute.
    typ: TypeName


class StructSchema(BaseSchema, ABC):
    def __post_init__(self):
        # We can only validate the schema at run time, and cannot rely on mypy typecheck.
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, BaseSchema):
                raise ValueError(f"Unexpected value in {self}: {value}")

    def get_attr(self, attr: StructAttribute[TSchema]) -> TSchema:
        return getattr(self, attr.name)


class NullaryStructSchema(StructSchema, NullarySchema, ABC):
    pass


class Comparable(Protocol):
    """A protocol for classes that implement comparisons."""

    @abstractmethod
    def __lt__(self, other) -> bool:
        pass

    @abstractmethod
    def __le__(self, other) -> bool:
        pass

    @abstractmethod
    def __gt__(self, other) -> bool:
        pass

    @abstractmethod
    def __ge__(self, other) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass


class ComparableSchema(BaseSchema, Comparable, ABC):
    pass


TComparableSchema = TypeVar("TComparableSchema", bound=ComparableSchema)


@dataclass(frozen=True)
class Interval(Generic[TComparableSchema], StructSchema):
    lower: TComparableSchema
    upper: TComparableSchema

    def __post_init__(self):
        super().__post_init__()
        assert self.lower.dtype == self.upper.dtype
        assert self.lower <= self.upper

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor(self.lower.dtype)
