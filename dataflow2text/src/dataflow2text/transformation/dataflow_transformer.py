import dataclasses
import typing

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.transformation.transformation_rule import TransformationRule


class DataflowTransformer:
    def __init__(self, rules: typing.List[TransformationRule]):
        self._rules = rules

    def transform(self, computation: BaseFunction) -> BaseFunction:
        """Greedily transforms the computation using the first applicable transformation rule.

        TODO: This transformation does not currently preserve reentrant computations. We should first collect reentrant
         computations and then keep the map.
        """

        # Do a first pass so larger computations are rewritten first.
        _, curr = self._apply_rules(computation)

        changed = True
        while changed:
            new_args = {}
            for arg_name, arg_comp in curr.args():
                new_args[arg_name] = self.transform(arg_comp)
            curr = dataclasses.replace(curr, **new_args)  # type: ignore

            # Need to apply the rules again since the args have changed.
            changed, curr = self._apply_rules(curr)

        return curr

    def _apply_rules(
        self, computation: BaseFunction
    ) -> typing.Tuple[bool, BaseFunction]:
        curr = computation
        changed = False
        while True:
            changed_inner_loop = False
            for rule in self._rules:
                res = rule.run(curr)
                if res is not None:
                    changed_inner_loop = True
                    changed = True
                    curr = res
                    break
            if not changed_inner_loop:
                break

        return changed, curr
