from dataclasses import dataclass
from enum import Enum

class DraftStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"

class DraftSourceType(str, Enum):
    CUBE = "CUBE"
    RETAIL = "RETAIL"

@dataclass
class Draft:
    draft_id: str
    start_time_epoch_seconds: int
    game_mode: str
    draft_source_type: DraftSourceType
    draft_source_id: str
    draft_status: DraftStatus
    end_time_epoch_seconds: int