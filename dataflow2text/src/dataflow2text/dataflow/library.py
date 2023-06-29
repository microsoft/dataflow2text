import itertools
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Type, Union

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.dataflow.function_library import FunctionLibrary
from dataflow2text.dataflow.library_utils import safe_build_dict
from dataflow2text.dataflow.schema import BaseSchema, StructAttribute
from dataflow2text.dataflow.schema_library import SchemaLibrary
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.functions.date_ext import DateExt
from dataflow2text_domains.calflow.functions.date_time_ext import DateTimeExt
from dataflow2text_domains.calflow.functions.event_ext import EventExt


@dataclass(frozen=True)
class Library:
    """A dataflow library.

    Currently only used for SimpleGenerationParser.
    """

    schemas: SchemaLibrary
    functions: FunctionLibrary

    @cached_property
    def components(self) -> Dict[str, Type[Union[BaseSchema, BaseFunction, object]]]:
        return safe_build_dict(
            itertools.chain(
                self.schemas._schemas.values(),  # pylint: disable=protected-access
                self.functions._functions.values(),  # pylint: disable=protected-access
                # TODO: Should not hardcode these here and update the return type annotation.
                [
                    StructAttribute,
                    TypeName,
                    DateExt,
                    DateTimeExt,
                    EventExt,
                ],
            ),
            lambda x: x.__name__,
        )
