from dataflow2text.dataflow.type_name import TypeName


def test_render():
    assert TypeName("String").render() == "String"
    assert TypeName("List", (TypeName("String"),)).render() == "List[String]"
    assert (
        TypeName("Struct", (TypeName("String"), TypeName("Number"))).render()
        == "Struct[String, Number]"
    )
