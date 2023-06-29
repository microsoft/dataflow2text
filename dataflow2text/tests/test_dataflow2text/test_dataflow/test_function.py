import pytest

from dataflow2text.dataflow.function import (
    ExecutionError,
    ListCtor,
    NumberCtor,
    ValueCtor,
    function,
)
from dataflow2text.dataflow.schema import List, Long, Number, String
from dataflow2text.dataflow.type_name import TypeName
from test_dataflow2text.test_dataflow.examples import (
    EmptyListError,
    ExampleStruct,
    add,
    add_with_default,
    singleton,
    y0_getter,
)


def test_simple_add():
    number_dtype = Number.dtype_ctor()
    plan = add(NumberCtor(1.0), NumberCtor(2.0))
    assert plan.reveal_type() == number_dtype
    assert plan.return_type == number_dtype
    assert plan.__value__ == Number(3.0)


def test_add_with_default():
    number_dtype = Number.dtype_ctor()
    plan = add_with_default(NumberCtor(1.0))
    assert plan.reveal_type() == number_dtype
    assert plan.return_type == number_dtype
    assert plan.__value__ == Number(2.0)


def test_simple_list():
    number_dtype = Number.dtype_ctor()
    plan = singleton(ListCtor(number_dtype, [Number(1.0)]))
    assert plan.reveal_type() == number_dtype
    assert plan.return_type == number_dtype
    assert plan.__value__ == Number(1.0)


def test_nested_list():
    number_dtype = Number.dtype_ctor()
    lnumber_dtype = List.dtype_ctor(number_dtype)
    plan = singleton(
        ListCtor(
            lnumber_dtype,
            [List(number_dtype, [Number(1.0), Number(2.0)])],
        )
    )
    assert plan.reveal_type() == lnumber_dtype
    assert plan.return_type == lnumber_dtype
    assert plan.__value__.type_arg == number_dtype
    assert plan.__value__.inner == [Number(1.0), Number(2.0)]


def test_list_of_struct():
    expected_dtype = TypeName("ExampleStruct", (TypeName("Long"), TypeName("String")))
    one_foo = ExampleStruct(Long(1), String("foo"))
    plan = singleton(ValueCtor(List(expected_dtype, [one_foo])))
    assert plan.reveal_type() == expected_dtype
    assert plan.return_type == expected_dtype
    assert plan.__value__ == one_foo


def test_y0_getter():
    number_dtype = Number.dtype_ctor()
    plan = y0_getter(
        ValueCtor(ExampleStruct(String("foo"), List(number_dtype, [Number(1.0)])))
    )
    assert plan.reveal_type() == number_dtype
    assert plan.return_type == number_dtype
    assert plan.__value__ == Number(1.0)


def test_error_provenance():
    number_dtype = Number.dtype_ctor()
    plan = add(singleton(ListCtor(number_dtype, [])), NumberCtor(2.0))
    # This verifies that the `reveal_type` does not execute the computation.
    assert plan.reveal_type() == number_dtype

    value = plan.__value__
    assert isinstance(value, ExecutionError)
    assert isinstance(value.inner, EmptyListError)
    assert value.provenance == [singleton(ListCtor(number_dtype, [])), plan]


def test_has_forward_ref():
    def some_func1() -> "Number":
        pass

    with pytest.raises(ValueError, match="return annotation contains ForwardRef"):
        function(some_func1)

    def some_func2() -> ExampleStruct["Number", "String"]:
        pass

    with pytest.raises(ValueError, match="return annotation contains ForwardRef"):
        function(some_func2)
