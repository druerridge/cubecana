from enum import Enum
import json
import time
from typing import Optional
import uuid

from pathlib import Path
from cubecana_server.cubecana_draft import Draft, DraftSourceType
from cubecana_server.draft_dao import DbCubecanaDraft, draft_dao, DraftDao, DraftStatus
from cubecana_server.retail_manager import GAME_MODE_DRAFT
from cubecana_server.cube_manager import CubeManager, cube_manager
from cubecana_server.cubecana_cube import CubecanaCube

class DraftSourceType(str, Enum):
    CUBE = "CUBE"
    RETAIL = "RETAIL"

class PodCompositionType(str, Enum):
    HUMANS_ONLY = "HUMANS_ONLY"
    MIXED_HUMANS_AND_BOTS = "MIXED_HUMANS_AND_BOTS"
    SOLO_WITH_BOTS = "SOLO_WITH_BOTS"
    UNKNOWN = "UNKNOWN"

def calculate_pod_composition_type(draft_log_dict: dict, num_human_players: int) -> PodCompositionType:
    if is_all_human_draft(draft_log_dict, num_human_players):
        return PodCompositionType.HUMANS_ONLY
    elif is_mixed_draft(draft_log_dict, num_human_players):
        return PodCompositionType.MIXED_HUMANS_AND_BOTS  
    elif is_solo_draft(num_human_players):
        return PodCompositionType.SOLO_WITH_BOTS
    else:
        return PodCompositionType.UNKNOWN

def is_real_draft(draft_log_dict: dict, draft: Draft) -> bool:
    if draft.game_mode != GAME_MODE_DRAFT:
        return False # not sure what to do for sealed yet
    
    num_human_players = sum(1 for human in filter(lambda user: not user["isBot"], draft_log_dict["users"].values()))
    print(f"Number of human players: {num_human_players}")

    pod_composition_type: PodCompositionType = calculate_pod_composition_type(draft_log_dict, num_human_players)
    print(f"Pod composition type: {pod_composition_type}")

    picks_per_human = [len(human["picks"]) for human in filter(lambda user: not user["isBot"], draft_log_dict["users"].values())]
    print(f"Picks per human: {picks_per_human}")

    picks_to_finish = 48 # retail is 12 * 4 = 48
    if draft.draft_source_type == DraftSourceType.CUBE: 
        cube: CubecanaCube = cube_manager.get_cube(draft.draft_source_id)
        picks_to_finish = cube.settings.boosters_per_player * cube.settings.cards_per_booster
    num_humans_finished_picking = sum(1 for picks in picks_per_human if picks >= picks_to_finish)
    print(f"Number of humans finished picking: {num_humans_finished_picking}")

    num_human_decklists = sum(1 for player in filter(lambda user: not user["isBot"], draft_log_dict["users"].values()) if player.get("decklist"))
    print(f"Number of human decklists: {num_human_decklists}")

    return num_humans_finished_picking >= 1

def is_solo_draft(num_human_players):
    return num_human_players == 1

def is_mixed_draft(draft_log_dict, num_human_players):
    return num_human_players > 1 and num_human_players < len(draft_log_dict["users"].values())

def is_all_human_draft(draft_log_dict, num_human_players):
    is_all_humans = num_human_players >= len(draft_log_dict["users"].values())
    return is_all_humans

def write_draft_to_disk(draft_log_dict: dict, draft: Draft):
    try:
        draft_id = draft.draft_id
        filename = f"draft_logs/draft_{draft_id}.json"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as f:
            json.dump(draft_log_dict, f, separators=(',', ':'))
        print(f"Draft log written to {filename}")
    except Exception as e:
        print(f"Error writing draft log to disk: {e}")

class DraftManager:

    def __init__(self):
        pass

    def draft_to_db_draft(self, draft: Draft) -> DbCubecanaDraft:
        draft_id_binary = uuid.UUID(draft.draft_id).bytes
        draft_source_id_binary = uuid.UUID(draft.draft_source_id).bytes
        
        return DbCubecanaDraft(
            draft_id=draft_id_binary,
            start_time_epoch_seconds=draft.start_time_epoch_seconds,
            game_mode=draft.game_mode,
            draft_source_type=draft.draft_source_type.value,
            draft_source_id=draft_source_id_binary,
            draft_status=draft.draft_status.value,
            end_time_epoch_seconds=draft.end_time_epoch_seconds
        )

    def create_draft(self, draft_source_id: str, draft_source_type: DraftSourceType, game_mode: str) -> Draft:
        draft_id = str(uuid.uuid4())
        start_time = int(time.time())
        
        draft = Draft(
            draft_id=draft_id,
            start_time_epoch_seconds=start_time,
            game_mode=game_mode,
            draft_source_type=draft_source_type,
            draft_source_id=draft_source_id,
            draft_status=DraftStatus.STARTED,
            end_time_epoch_seconds=None,
        )

        db_draft = self.draft_to_db_draft(draft)

        draft_dao.create(db_draft)
        
        return draft

    def create_cube_draft(self, cube_id: str, game_mode: str, draft_settings: dict) -> Optional[Draft]:
        return self.create_draft(
            draft_source_id=cube_id,
            draft_source_type=DraftSourceType.CUBE,
            game_mode=game_mode,
        )

    def create_retail_draft(self, retail_set_id: str, game_mode: str) -> Optional[Draft]:
        retail_set_int = int(retail_set_id)
        retail_set_uuid = uuid.UUID(int=retail_set_int)
        retail_set_uuid_str = str(retail_set_uuid)
        return self.create_draft(
            draft_source_id=retail_set_uuid_str,
            draft_source_type=DraftSourceType.RETAIL,
            game_mode=game_mode,        
        )

    def get_draft(self, draft_id: str) -> Optional[Draft]:
        db_draft: Optional[DbCubecanaDraft] = draft_dao.get(draft_id)
        if not db_draft:
            return None

        # Convert binary UUIDs back to strings
        draft_id_str = str(uuid.UUID(bytes=db_draft.draft_id))
        draft_source_id_str = str(uuid.UUID(bytes=db_draft.draft_source_id))
        
        return Draft(
            draft_id=draft_id_str,
            start_time_epoch_seconds=db_draft.start_time_epoch_seconds,
            game_mode=db_draft.game_mode,
            draft_source_type=DraftSourceType(db_draft.draft_source_type),
            draft_source_id=draft_source_id_str,
            end_time_epoch_seconds=db_draft.end_time_epoch_seconds,
            draft_status=DraftStatus(db_draft.draft_status)
        )
    
    def end_draft(self, draft_id: str, draft_log_dict: dict) -> bool:
        draft: Optional[Draft] = self.get_draft(draft_id)
        if not draft:
            return False
        
        is_real_draft(draft_log_dict, draft)

        write_draft_to_disk(draft_log_dict, draft)

        draft.end_time_epoch_seconds = int(time.time())
        draft.draft_status = DraftStatus.COMPLETED

        db_draft = self.draft_to_db_draft(draft)
        success = draft_dao.update(db_draft)
        
        if not success:
            return None
        
        return draft
        
draft_manager: DraftManager = DraftManager()