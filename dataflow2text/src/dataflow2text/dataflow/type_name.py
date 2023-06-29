from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class TypeName:
    base: str
    # Tuples preferred so TypeNames can be hashable
    type_args: Tuple["TypeName", ...] = field(default_factory=tuple)

    def render(self) -> str:
        if len(self.type_args) == 0:
            return self.base
        else:
            return f'{self.base}[{", ".join(a.render() for a in self.type_args)}]'
