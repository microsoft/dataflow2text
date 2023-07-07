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

class MissingPreambleError(RuntimeError):
    def __init__(self, dialogue_id: str):
        self._dialogue_id = dialogue_id
        message = f"Missing preamble for {self._dialogue_id}"
        super().__init__(message)


class InvalidPreambleError(RuntimeError):
    def __init__(self, dialogue_id: str):
        self._dialogue_id = dialogue_id
        message = f"Invalid preamble for {self._dialogue_id}"
        super().__init__(message)


class MissingTimestampError(RuntimeError):
    def __init__(self, dialogue_id: str, turn_index: int):
        self._dialogue_id = dialogue_id
        self._turn_index = turn_index
        message = f"Missing timestamp for {self._dialogue_id} : {self._turn_index}"
        super().__init__(message)
