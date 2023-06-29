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
