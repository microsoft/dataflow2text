from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.dataflow.schema import String
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from test_dataflow2text.test_dataflow.examples import ExampleStruct, add, head


@generation(act=DEFAULT_ACT, template="Hello world!")
def say_hello_world(_: BaseFunction):
    return {}


@generation(
    act=DEFAULT_ACT, typ=TypeName("String"), template="{{Hello [name] | Hi [name]}}"
)
def say_hello_or_hi(c: BaseFunction):
    return {"name": c}


@generation(
    act=DEFAULT_ACT,
    template="The result of [x] plus [y] is [z].",
)
def say_add(c: BaseFunction):
    match c:
        case add(x, y) as z:  # type: ignore
            return {"x": x, "y": y, "z": z}


@generation(
    act=DEFAULT_ACT,
    typ=String.dtype_ctor(),
    template="The first string is [x].",
)
def say_first_string(c: BaseFunction):
    match c:
        case head(_) as x:  # type: ignore
            return {"x": x}


@generation(
    act=DEFAULT_ACT,
    typ=TypeName("ExampleStruct", (TypeName("String"), TypeName("Number"))),
    template="The field y is [y].",
)
def say_struct_y(c: BaseFunction):
    match c:
        case ValueCtor(ExampleStruct(_, y)):  # type: ignore
            # When matching inside the ValueCtor, the binding should be wrapped with a ValueCtor as well.
            return {"y": ValueCtor(y)}


@generation(
    act=DEFAULT_ACT,
    typ=TypeName("ExampleStruct", (TypeName("String"), TypeName("String"))),
    template="{{ x is {NP [x]} and y is {NP [y]} | y is {NP [y]} and x is {NP [x]} }}",
)
def say_struct_x_and_y(c: BaseFunction):
    match c:
        case ValueCtor(ExampleStruct(x, y)):  # type: ignore
            # When matching inside the ValueCtor, the binding should be wrapped with a ValueCtor as well.
            return {"x": ValueCtor(x), "y": ValueCtor(y), "struct": c}


@generation(
    act=DEFAULT_ACT,
    typ=TypeName("ExampleStruct", (TypeName("String"), TypeName("String"))),
    template="The struct {NP [struct]} has x=[x] and y=[y]",
)
def say_struct_x_and_y_2(c: BaseFunction):
    match c:
        case ValueCtor(ExampleStruct(x, y)):  # type: ignore
            return {"x": ValueCtor(x), "y": ValueCtor(y), "struct": c}


@generation(act="NP", typ=String.dtype_ctor(), template="[x]")
def say_string_lowercase(c: BaseFunction[String]):
    match c:
        case ValueCtor(String(x)):  # type: ignore
            return {"x": ValueCtor(String(x.lower()))}


@generation(act="NP", typ=String.dtype_ctor(), template='"[x]"')
def say_string_quoted(c: BaseFunction[String]):
    match c:
        case ValueCtor(String(_)):  # type: ignore
            return {"x": c}
