from enum import Enum
import time
from typing import Optional
import uuid
from cubecana_server.cubecana_draft import Draft, DraftSourceType
from cubecana_server.draft_dao import DbCubecanaDraft, draft_dao, DraftDao, DraftStatus
from cubecana_server.retail_manager import GAME_MODE_DRAFT

class DraftSourceType(str, Enum):
    CUBE = "CUBE"
    RETAIL = "RETAIL"

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
        
        draft.end_time_epoch_seconds = int(time.time())
        draft.draft_status = DraftStatus.COMPLETED

        db_draft = self.draft_to_db_draft(draft)
        success = draft_dao.update(db_draft)

        if not success:
            return None
        
        return draft
        
draft_manager: DraftManager = DraftManager()