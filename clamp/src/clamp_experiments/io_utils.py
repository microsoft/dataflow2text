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
from typing import List, Optional

from tqdm import tqdm

from clamp.search.datum import FullDatum


def load_data_from_json_file(
    data_file: str, datum_id_allowlist: Optional[List[str]] = None
) -> List[FullDatum]:
    data = []
    print("datum_id_allowlist = ", datum_id_allowlist)
    for line in tqdm(open(data_file, "r")):
        row = json.loads(line.strip())

        dialogue_id = row.get("dialogueId")
        turn_index = row.get("turnIndex")
        datum_id: str = f"{dialogue_id}_{turn_index}"

        if datum_id_allowlist is not None and datum_id not in datum_id_allowlist:
            continue

        datum = FullDatum(
            dialogue_id=dialogue_id,
            turn_index=turn_index,
            natural=row.get("input"),
            canonical=row.get("agentUtterance"),
            agent_context="",
        )
        data.append(datum)

    return data
