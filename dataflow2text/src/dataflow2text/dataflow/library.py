# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
