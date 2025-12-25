import uuid
import time
from typing import Optional
from sqlalchemy import Column, Integer, exc
from sqlalchemy.dialects.mysql import BINARY, VARCHAR
from .database import Base, db_connection
from .cubecana_draft import DraftStatus, DraftSourceType

OPERATIONAL_ERROR_RETRIES = 1

class DbCubecanaDraft(Base):
    __tablename__ = 'cubecana_draft'
    pk = Column(Integer, primary_key=True)
    draft_id = Column(BINARY(16), nullable=False, unique=True)
    start_time_epoch_seconds = Column(Integer)
    game_mode = Column(VARCHAR(32), nullable=False)
    draft_source_type = Column(VARCHAR(32), nullable=False)
    draft_source_id = Column(BINARY(16), nullable=False)
    end_time_epoch_seconds = Column(Integer)
    draft_status = Column(VARCHAR(32), nullable=False)

class DraftDao:
    def __init__(self):
        # Use the shared database connection
        pass

    def get_session(self):
        return db_connection.get_session()

    def execute(self, operation, retries_attempted=0, *args, **kwargs):
        session = None
        try:
            session = self.get_session()
            return operation(session, *args, **kwargs)
        except exc.OperationalError as e:
            session.close()
            session = None
            if retries_attempted < OPERATIONAL_ERROR_RETRIES:
                print(f"OperationalError: {e}, retrying...")
                return self.execute(operation, retries_attempted + 1, *args, **kwargs)
            else:
                print("Max retries reached, raising exception")
                raise e
        except Exception as e:
            print("Error executing db query")
            print(e)
            raise e
        finally:
            if session:
                session.close()

    def create(
        self,
        db_draft: DbCubecanaDraft
    ) -> None:
        def operation(session, db_draft):
            session.add(db_draft)
            session.commit()

        return self.execute(operation, db_draft=db_draft)

    def get(self, draft_id: str) -> Optional[DbCubecanaDraft]:
        def operation(session, draft_id):
            draft_id_binary = uuid.UUID(draft_id).bytes
            
            db_draft = session.query(DbCubecanaDraft).filter(
                DbCubecanaDraft.draft_id == draft_id_binary
            ).first()
            
            if not db_draft:
                return None
            
            return db_draft

        return self.execute(operation, draft_id=draft_id)

    def ended_at(self, draft_id: str, draft_status: DraftStatus) -> bool:
        """
        Mark a draft as ended with the specified status and set the end time.
        
        Args:
            draft_id: The UUID string of the draft to update
            draft_status: The final status (COMPLETED)
            
        Returns:
            bool: True if the update was successful, False if draft not found
        """
        def operation(session, draft_id, draft_status):
            draft_id_binary = uuid.UUID(draft_id).bytes
            end_time = int(time.time())
            
            db_draft = session.query(DbCubecanaDraft).filter(
                DbCubecanaDraft.draft_id == draft_id_binary
            ).first()
            
            if not db_draft:
                return False
            
            db_draft.draft_status = draft_status.value
            db_draft.end_time_epoch_seconds = end_time
            session.commit()
            
            return True

        return self.execute(operation, draft_id=draft_id, draft_status=draft_status)

# Convenience instance for easy importing
draft_dao = DraftDao()