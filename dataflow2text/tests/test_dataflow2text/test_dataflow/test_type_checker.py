import pytest

from dataflow2text.dataflow.function import GetAttr, ValueCtor
from dataflow2text.dataflow.schema import List, Number, String, StructAttribute
from dataflow2text.dataflow.type_checker import TypeMismatchError, validate_type
from test_dataflow2text.test_dataflow.examples import (
    EXAMPLE_SCHEMA_LIBRARY,
    ExampleStruct,
    add,
    size,
)


def test_value_ctor():
    computation1 = ValueCtor(Number(1.0))
    validate_type(computation1, EXAMPLE_SCHEMA_LIBRARY)

    computation2 = ValueCtor(String("foo"))
    validate_type(computation2, EXAMPLE_SCHEMA_LIBRARY)

    computation3 = ValueCtor(List(Number.dtype_ctor(), [String("foo")]))
    validate_type(computation3, EXAMPLE_SCHEMA_LIBRARY)


def test_get_attr():
    computation1 = GetAttr(
        StructAttribute("x", String.dtype_ctor()),
        ValueCtor(ExampleStruct(String("foo"), Number(1.0))),
    )
    validate_type(computation1, EXAMPLE_SCHEMA_LIBRARY)

    computation2 = GetAttr(
        StructAttribute("x", Number.dtype_ctor()),
        ValueCtor(ExampleStruct(String("foo"), Number(1.0))),
    )
    with pytest.raises(TypeMismatchError):
        validate_type(computation2, EXAMPLE_SCHEMA_LIBRARY)

    computation3 = GetAttr(
        StructAttribute("x", List.dtype_ctor(String.dtype_ctor())),
        ValueCtor(
            ExampleStruct(List(String.dtype_ctor(), [String("foo")]), Number(1.0))
        ),
    )
    validate_type(computation3, EXAMPLE_SCHEMA_LIBRARY)


def test_simple_should_succeed():
    computation = add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0)))
    validate_type(computation, EXAMPLE_SCHEMA_LIBRARY)


def test_simple_should_fail():
    computation = add(ValueCtor(Number(1.0)), ValueCtor(String("foo")))

    with pytest.raises(TypeMismatchError):
        validate_type(computation, EXAMPLE_SCHEMA_LIBRARY)


def test_with_type_arg():
    number_dtype = Number.dtype_ctor()
    computation1 = size(ValueCtor(List(number_dtype, [Number(1.0)])))
    validate_type(computation1, EXAMPLE_SCHEMA_LIBRARY)

    lnumber_dtype = List.dtype_ctor(number_dtype)
    computation2 = size(
        ValueCtor(List(lnumber_dtype, [List(number_dtype, [Number(1.0)])]))
    )

    validate_type(computation2, EXAMPLE_SCHEMA_LIBRARY)
