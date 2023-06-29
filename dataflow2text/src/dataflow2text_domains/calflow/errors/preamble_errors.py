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
