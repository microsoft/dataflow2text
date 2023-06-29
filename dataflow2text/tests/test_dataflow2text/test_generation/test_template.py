from dataflow2text.generation.constants import TOSTRING_ACT
from dataflow2text.generation.template import (
    LexicalVariants,
    Template,
    expand_lexical_variants,
)
from dataflow2text.generation.template_factory import TemplateFactory
from dataflow2text.generation.template_part import TemplateNonterminal, TemplateTerminal


def assert_parser_output(text: str, expected: Template):
    template = TemplateFactory.parse(text)
    assert template == expected


def test_empty():
    assert_parser_output("", Template([TemplateTerminal("")]))


def test_simple():
    assert_parser_output("hello world", Template([TemplateTerminal("hello world")]))


def test_nonterminal_whitespace():
    assert_parser_output("{NP   [expr]}", Template([TemplateNonterminal("NP", "expr")]))
    assert_parser_output("{NP [ expr ]}", Template([TemplateNonterminal("NP", "expr")]))
    assert_parser_output("{NP[expr]}", Template([TemplateNonterminal("NP", "expr")]))
    assert_parser_output(
        "{ NP [expr]    }", Template([TemplateNonterminal("NP", "expr")])
    )


def test_template():
    assert_parser_output(
        "Template with {NP [expr]} two {aPP [expr2]} nonterminals",
        Template(
            [
                TemplateTerminal("Template with "),
                TemplateNonterminal("NP", "expr"),
                TemplateTerminal(" two "),
                TemplateNonterminal("aPP", "expr2"),
                TemplateTerminal(" nonterminals"),
            ]
        ),
    )


def test_expression():
    assert_parser_output(
        "{act [a().attr.value]}",
        Template([TemplateNonterminal("act", "a().attr.value")]),
    )


def test_toString():
    assert_parser_output("[a]", Template([TemplateNonterminal(TOSTRING_ACT, "a")]))


def test_lexical_variants_1():
    assert_parser_output(
        "{{ Hello | _ }}",
        Template(
            [
                LexicalVariants(
                    [
                        Template([TemplateTerminal("Hello")]),
                        Template([TemplateTerminal("")]),
                    ]
                )
            ]
        ),
    )


def test_lexical_variants_2():
    assert_parser_output(
        "{{Hello|_}}",
        Template(
            [
                LexicalVariants(
                    [
                        Template([TemplateTerminal("Hello")]),
                        Template([TemplateTerminal("")]),
                    ]
                )
            ]
        ),
    )


def test_lexical_variants_3():
    assert_parser_output(
        "{{ [a]   | _ }} {AP [foo]}",
        Template(
            [
                LexicalVariants(
                    [
                        Template([TemplateNonterminal(TOSTRING_ACT, "a")]),
                        Template([TemplateTerminal("")]),
                    ],
                ),
                TemplateTerminal(" "),
                TemplateNonterminal("AP", "foo"),
            ]
        ),
    )


def test_lexical_variants_4():
    assert_parser_output(
        "{{Hello {NP [a]} | world}}",
        Template(
            [
                LexicalVariants(
                    [
                        Template(
                            [
                                TemplateTerminal("Hello "),
                                TemplateNonterminal("NP", "a"),
                            ]
                        ),
                        Template([TemplateTerminal("world")]),
                    ]
                )
            ]
        ),
    )


def test_lexical_variants_5():
    assert_parser_output(
        "{{Hello {NP [a]} | world {NP [a().attr.value]} }}",
        Template(
            [
                LexicalVariants(
                    [
                        Template(
                            [
                                TemplateTerminal("Hello "),
                                TemplateNonterminal("NP", "a"),
                            ]
                        ),
                        Template(
                            [
                                TemplateTerminal("world "),
                                # The SimpleGenerationParser would not allow this though, since
                                # it assumes all NT are dataflow computations, but this is a dataflow value.
                                TemplateNonterminal("NP", "a().attr.value"),
                            ]
                        ),
                    ]
                )
            ]
        ),
    )


def test_lexical_variants_6():
    assert_parser_output(
        "{{ one | two | three | four }}",
        Template(
            [
                LexicalVariants(
                    [
                        Template([TemplateTerminal("one")]),
                        Template([TemplateTerminal("two")]),
                        Template([TemplateTerminal("three")]),
                        Template([TemplateTerminal("four")]),
                    ]
                )
            ]
        ),
    )


def test_lexical_variants_7():
    assert_parser_output(
        "{{ one | {{ two | three }} | four }}",
        Template(
            [
                LexicalVariants(
                    [
                        Template([TemplateTerminal("one")]),
                        Template(
                            [
                                LexicalVariants(
                                    [
                                        Template([TemplateTerminal("two")]),
                                        Template([TemplateTerminal("three")]),
                                    ]
                                )
                            ]
                        ),
                        Template([TemplateTerminal("four")]),
                    ]
                )
            ]
        ),
    )


def test_lexical_variants_8():
    assert_parser_output(
        "I found {{ matching event | event }} { PP [constraint] } {{ on your calendar | _ }}",
        Template(
            [
                TemplateTerminal("I found "),
                LexicalVariants(
                    [
                        Template([TemplateTerminal("matching event")]),
                        Template([TemplateTerminal("event")]),
                    ]
                ),
                TemplateTerminal(" "),
                TemplateNonterminal(act="PP", expression="constraint"),
                TemplateTerminal(" "),
                LexicalVariants(
                    [
                        Template([TemplateTerminal("on your calendar")]),
                        Template([TemplateTerminal("")]),
                    ]
                ),
            ]
        ),
    )


def assert_expand_lexical_variants_output(template_str, expected):
    raw_template = TemplateFactory.parse(template_str)
    expanded_templates = expand_lexical_variants(raw_template, [])
    assert expanded_templates == expected


def test_expand_lexical_variants_1():
    assert_expand_lexical_variants_output(
        "{{ Hello | Hi }}",
        [
            Template([TemplateTerminal("Hello")]),
            Template([TemplateTerminal("Hi")]),
        ],
    )


def test_expand_lexical_variants_2():
    assert_expand_lexical_variants_output(
        "I found {{ matching event | event }} { PP [constraint] } {{ on your calendar | _ }}",
        [
            Template(
                [
                    TemplateTerminal("I found "),
                    TemplateTerminal("matching event"),
                    TemplateTerminal(" "),
                    TemplateNonterminal(act="PP", expression="constraint"),
                    TemplateTerminal(" "),
                    TemplateTerminal("on your calendar"),
                ]
            ),
            Template(
                [
                    TemplateTerminal("I found "),
                    TemplateTerminal("matching event"),
                    TemplateTerminal(" "),
                    TemplateNonterminal(act="PP", expression="constraint"),
                    TemplateTerminal(" "),
                    TemplateTerminal(""),
                ]
            ),
            Template(
                [
                    TemplateTerminal("I found "),
                    TemplateTerminal("event"),
                    TemplateTerminal(" "),
                    TemplateNonterminal(act="PP", expression="constraint"),
                    TemplateTerminal(" "),
                    TemplateTerminal("on your calendar"),
                ]
            ),
            Template(
                [
                    TemplateTerminal("I found "),
                    TemplateTerminal("event"),
                    TemplateTerminal(" "),
                    TemplateNonterminal(act="PP", expression="constraint"),
                    TemplateTerminal(" "),
                    TemplateTerminal(""),
                ]
            ),
        ],
    )
