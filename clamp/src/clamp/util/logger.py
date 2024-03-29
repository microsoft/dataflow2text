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

import contextlib
import io
import pathlib
import sys
import traceback
import warnings
from dataclasses import dataclass
from io import SEEK_SET, TextIOBase
from typing import Iterator, List, Optional, TextIO


@dataclass
class Tee(TextIOBase):
    """A write-only file-like object that forwards writes to `sinks`."""

    sinks: List[TextIO]
    closed: bool = False

    def close(self) -> None:
        self.flush()
        self.closed = True

    def fileno(self) -> int:
        raise OSError

    def flush(self) -> None:
        for sink in self.sinks:
            sink.flush()

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return False

    def readline(self, size=-1) -> str:  # type: ignore
        raise io.UnsupportedOperation

    def readlines(self, hint=-1) -> List[str]:  # type: ignore
        raise io.UnsupportedOperation

    def seek(self, offset, whence=SEEK_SET) -> int:
        raise io.UnsupportedOperation

    def seekable(self) -> bool:
        return False

    def tell(self) -> int:
        raise io.UnsupportedOperation

    def truncate(self, size=None):
        raise io.UnsupportedOperation

    def writable(self) -> bool:
        return True

    def writelines(self, lines: List[str]) -> None:  # type: ignore
        for sink in self.sinks:
            sink.writelines(lines)

    @property
    def encoding(self) -> str:  # type: ignore
        return self.sinks[0].encoding

    @property
    def errors(self) -> Optional[str]:  # type: ignore
        return self.sinks[0].errors

    def detach(self) -> None:
        raise io.UnsupportedOperation

    def read(self, size=-1) -> str:
        raise io.UnsupportedOperation

    def write(self, s: str) -> int:
        results: List[int] = []
        for sink in self.sinks:
            results.append(sink.write(s))
        if not all(r == results[0] for r in results[1:]):
            warnings.warn("Sinks wrote different number of characters", ResourceWarning)
        return results[0]


@contextlib.contextmanager
def intercept_output(
    stdout_path: pathlib.Path, stderr_path: pathlib.Path
) -> Iterator[None]:
    """Write all stdout and stderr to both the screen and these files."""

    with open(stdout_path, "a") as stdout_file, open(stderr_path, "a") as stderr_file:
        true_stdout = sys.stdout
        true_stderr = sys.stderr
        sys.stdout = Tee([true_stdout, stdout_file])  # type: ignore
        sys.stderr = Tee([true_stdout, stderr_file])  # type: ignore
        try:
            yield
        except:
            traceback.print_exc(file=stderr_file)
            raise
        finally:
            sys.stdout = true_stdout
            sys.stderr = true_stderr
