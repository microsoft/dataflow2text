import pytest

from dataflow2text.dataflow.schema import Dynamic, Long, String
from dataflow2text.dataflow.type_name import TypeName
from test_dataflow2text.test_dataflow.examples import ExampleColor, ExampleStruct


def test_dtype_ctor():
    assert String.dtype_ctor() == TypeName("String")
    with pytest.raises(ValueError):
        String.dtype_ctor(TypeName("String"))


def test_dynamic():
    expected_dtype = TypeName("Dynamic")
    assert Dynamic.dtype_ctor() == expected_dtype

    x = Dynamic(String.dtype_ctor(), String("foo"))
    assert x.dtype == expected_dtype
    assert x.inner.dtype == String.dtype_ctor()


def test_enum_value():
    expected_dtype = TypeName("ExampleColor")
    assert ExampleColor.dtype_ctor() == expected_dtype

    red = ExampleColor.Red()
    assert isinstance(red, ExampleColor)
    assert red.dtype == expected_dtype
    assert red.inner == "Red"

    blue = ExampleColor.Blue()
    assert isinstance(blue, ExampleColor)
    assert blue.dtype == expected_dtype
    assert blue.inner == "Blue"


def test_list_of_struct():
    one_foo = ExampleStruct(Long(1), String("foo"))
    assert one_foo.dtype == TypeName(
        "ExampleStruct", (TypeName("Long"), TypeName("String"))
    )
