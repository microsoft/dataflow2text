from collections import defaultdict
from typing import DefaultDict, Dict, Iterator, List, Optional, Set, Tuple

from dataflow2text.dataflow.function import BaseFunction, ExecutionError
from dataflow2text.dataflow.library import Library
from dataflow2text.dataflow.schema import Long, Number, String
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text.generation.constants import DEFAULT_ACT, TOSTRING_ACT
from dataflow2text.generation.generation_production import (
    GenerationProduction,
    render_generation_production,
)
from dataflow2text.generation.generation_rule import GenerationRule
from dataflow2text.generation.generation_symbol import (
    GenerationNonterminal,
    GenerationSymbol,
    GenerationTerminal,
)
from dataflow2text.generation.generation_tree_builder import GenerationTreeBuilder
from dataflow2text.generation.template import LexicalVariants
from dataflow2text.generation.template_part import (
    TemplateNonterminal,
    TemplatePart,
    TemplateTerminal,
)

_DUMMY_PRODUCTION_NAME = "__dummy__"


class DataflowTransducer:
    """A dataflow transducer to generate CFG productions for dataflow computations."""

    def __init__(self, library: Library, rules: List[GenerationRule]):
        """Constructor

        Args:
            library: The dataflow library.
            rules: The set of dataflow transduction rules.
        """
        self._library = library

        self._rules_lookup: DefaultDict[
            Tuple[str, TypeName], List[GenerationRule]
        ] = defaultdict(list)

        rule: GenerationRule
        for rule in rules:
            # We use a dummy production to expand a visited nonterminal to obtain a new GenerationTreeBuilder.
            # See `_expand_builder`.
            assert rule.name != _DUMMY_PRODUCTION_NAME

            # All LexicalVariants should have been expanded already.
            if any(isinstance(part, LexicalVariants) for part in rule.template.parts):
                raise ValueError(f"{rule.name} contains LexicalVariants.")

            self._rules_lookup[(rule.act, rule.matcher.typ)].append(rule)

        self._visited_nonterminals: Dict[
            GenerationNonterminal, List[GenerationProduction]
        ] = {}

    def generate(self, computation: BaseFunction) -> Iterator[GenerationProduction]:
        self._visited_nonterminals.clear()

        builder = GenerationTreeBuilder(
            GenerationNonterminal(act=DEFAULT_ACT, computation=computation)
        )
        generated_productions: List[GenerationProduction] = []
        self._expand_builder(builder, generated_productions)
        for production in generated_productions:
            if production.name == _DUMMY_PRODUCTION_NAME:
                assert not production.rhs
                continue
            yield production

    def _expand_builder(
        self,
        builder: GenerationTreeBuilder,
        generated_productions: List[GenerationProduction],
    ) -> bool:
        nt = builder.next_nonterminal()
        if nt is None:
            productions = builder.tree[(0,)].productions()
            assert productions, f"Got empty productions.\n{builder.tree}"
            generated_productions += productions
            return True

        new_generated_productions: List[GenerationProduction] = []
        if not self._expand_nonterminal(nt, new_generated_productions):
            return False

        dummy_production = _make_dummy_production(
            nt,
        )
        builder.extend(dummy_production)
        if not self._expand_builder(builder, new_generated_productions):
            return False

        generated_productions += new_generated_productions
        return True

    def _expand_nonterminal(
        self,
        nt: GenerationNonterminal,
        generated_productions: List[GenerationProduction],
    ) -> bool:
        cached_productions = self._visited_nonterminals.get(nt, None)
        if cached_productions is not None:
            generated_productions += cached_productions
            return len(cached_productions) > 0

        new_generated_productions: List[GenerationProduction] = []
        for production in get_applicable_productions(
            nt, self._rules_lookup, self._library
        ):
            builder = GenerationTreeBuilder(start_symbol=nt)
            builder.extend(production)
            self._expand_builder(builder, new_generated_productions)

        # Deduplicate productions for efficiency consideration.
        # 1. We need much more memory to hold the duplicated productions.
        # 2. Concatenating long lists can be very slow.
        new_generated_productions = list(_unique_productions(new_generated_productions))

        generated_productions += new_generated_productions

        # NOTE: If the assertion below failed, it means there are recursion rules like `nt -> ... nt ...`. Such rules
        # do not appear in our data currently. When this is no longer true, we should properly handle it.
        assert nt not in self._visited_nonterminals
        self._visited_nonterminals[nt] = new_generated_productions
        return len(new_generated_productions) > 0

    def _get_applicable_productions(
        self, nt: GenerationNonterminal
    ) -> Iterator[GenerationProduction]:
        if nt.act == TOSTRING_ACT:
            production = nt_to_production(nt)
            yield production

        applicable_rules = (
            self._rules_lookup[(nt.act, nt.computation.return_type)]
            + self._rules_lookup[(nt.act, None)]
        )
        for rule in applicable_rules:
            production = rule_to_production(
                rule,
                nt,
                self._library,
            )
            if production is None:
                continue
            yield production


def _make_dummy_production(nt: GenerationNonterminal) -> GenerationProduction:
    return GenerationProduction(name=_DUMMY_PRODUCTION_NAME, lhs=nt, rhs=[])


def _unique_productions(
    productions: List[GenerationProduction],
) -> Iterator[GenerationProduction]:
    """Returns an iterator over unique productions.

    Right now we cannot directly compare `GenerationProduction` since there is no native `__hash__` defined.
    Therefore, we use `render_generation_production` as the key for each production.
    We should consider defining a proper `__hash__` for `GenerationProduction` in future.
    """
    seen_production_strs: Set[str] = set()
    for production in productions:
        production_str = render_generation_production(production)
        if production_str in seen_production_strs:
            continue
        seen_production_strs.add(production_str)
        yield production


def nt_to_production(nt: GenerationNonterminal) -> GenerationProduction:
    value = nt.computation.__value__
    if isinstance(value, ExecutionError):
        raise value
    # TODO: handle other schemas
    if not isinstance(value, (String, Long, Number)):
        raise ValueError(f"Cannot convert {value} to string.")

    res = str(value.inner)
    return GenerationProduction(
        name=TOSTRING_ACT,
        lhs=nt,
        rhs=[GenerationTerminal(inner=res)],
    )


def rule_to_production(
    rule: GenerationRule,
    nt: GenerationNonterminal,
    library: Library,
) -> Optional[GenerationProduction]:
    template = rule.expand(nt)
    if template is None:
        return None

    production = GenerationProduction(
        name=rule.name,
        lhs=nt,
        rhs=[template_part_to_symbol(part, library) for part in template.parts],
    )
    return production


def get_applicable_productions(
    nt: GenerationNonterminal,
    rules_lookup: DefaultDict[Tuple[str, TypeName], List[GenerationRule]],
    library: Library,
) -> Iterator[GenerationProduction]:
    if nt.act == TOSTRING_ACT:
        production = nt_to_production(nt)
        yield production

    applicable_rules = (
        rules_lookup[(nt.act, nt.computation.return_type)]
        + rules_lookup[(nt.act, None)]
    )
    for rule in applicable_rules:
        production = rule_to_production(
            rule,
            nt,
            library,
        )
        if production is None:
            continue
        yield production


def template_part_to_symbol(part: TemplatePart, library: Library) -> GenerationSymbol:
    """Converts a TemplatePart to a GenerationSymbol.

    The library is needed to convert the expression str in the TemplateNonterminal to a Computation.
    """
    if isinstance(part, TemplateNonterminal):
        # pylint: disable=eval-used
        computation = eval(part.expression, library.components)
        return GenerationNonterminal(act=part.act, computation=computation)
    if isinstance(part, TemplateTerminal):
        return GenerationTerminal(inner=part.inner)
    raise ValueError(f"Unexpected TemplatePart: {part}")
