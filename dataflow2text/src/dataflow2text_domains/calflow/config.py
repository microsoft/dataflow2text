"""Global config variables.

These are used as a global variable for passing around the meta information about the current dialogue/turn in
different API calls. This is not safe, so use with caution.
"""
from typing import Optional

preambles_dir: Optional[str] = None
metas_dir: Optional[str] = None

current_dialogue_id: Optional[str] = None
# 0-based turn index.
current_turn_index: Optional[int] = None
