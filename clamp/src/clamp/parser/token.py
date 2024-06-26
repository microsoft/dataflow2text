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

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

import regex
from cached_property import cached_property

ASCII_CHARS: List[str] = [chr(i) for i in range(32, 127)]


class SCFGToken(ABC):
    def render(self) -> str:
        """
        How to render this token when generating it. In most cases, you can just render the underlying value.
        Sometimes you want to modify it, like in TerminalToken.
        """
        return self.value

    @property
    @abstractmethod
    def value(self) -> str:
        """The underlying value of the token."""

    @property
    def lark_value(self) -> str:
        return self.value


class OptionableSCFGToken(SCFGToken, ABC):
    optional: bool


@dataclass(frozen=True)
class NonterminalToken(OptionableSCFGToken):
    underlying: str
    optional: bool

    @property
    def value(self):
        return self.underlying

    def is_regex(self):
        return self.underlying[0] == "/"


@dataclass(frozen=True)
class TerminalToken(OptionableSCFGToken):
    underlying: str
    optional: bool

    def render(self):
        """
        Remove the outermost quotes and unescape the rest of the quotes.
        """
        return json.loads(self.underlying)

    @property
    def value(self):
        return self.underlying

    @property
    def lark_value(self):
        return self.value + "i"


@dataclass(frozen=True)
class MacroToken(SCFGToken):
    name: str
    args: Tuple[SCFGToken, ...]

    @property
    def value(self):
        return f"{self.name}({','.join([a.value for a in self.args])})"


@dataclass(frozen=True)
class EmptyToken(SCFGToken):
    @property
    def value(self):
        return ""


@dataclass(frozen=True)
class RegexToken(NonterminalToken):
    prefix: str

    def render_matching_value(self, value: str) -> str:
        return self.prefix + value

    @property
    def value(self) -> str:
        return self.underlying

    @property
    def lark_value(self) -> str:
        if (
            self.prefix
        ):  # We need to have this condition because lark gets mad if you give it an empty token.
            return f'"{self.prefix}" ' + self.underlying
        else:
            return self.underlying

    @cached_property
    def compiled(self) -> "regex.Pattern[str]":
        assert self.underlying.startswith("/") and self.underlying.endswith("/")
        return regex.compile(self.underlying[1:-1])

    @cached_property
    def ascii_chars(self) -> List[str]:
        return [c for c in ASCII_CHARS if self.compiled.match(c)]
