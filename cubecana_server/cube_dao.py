import uuid
import json
from pathlib import Path
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Text, JSON, func, exc
from sqlalchemy.dialects.mysql import BINARY, VARCHAR, TEXT
from . import api
from .database import Base, db_connection

MAX_CARD_LIST_LENGTH = 80000  # MIGHT have to update the DB if you change this... but maybe not
PAGE_VIEW_COEFFICIENT = 1
LIST_VIEW_COEFFICIENT = 1
DRAFT_COEFFICIENT = 5 
OPERATIONAL_ERROR_RETRIES = 1

class DbCubecanaCube(Base):
    __tablename__ = 'cubecana_cubes'
    pk = Column(Integer, primary_key=True)
    id = Column(BINARY(16), default=lambda: uuid.uuid4().bytes, unique=True, nullable=False)
    name = Column(VARCHAR(255, charset='utf8mb4', collation='utf8mb4_unicode_ci'))
    card_id_to_count = Column(TEXT(MAX_CARD_LIST_LENGTH, charset='utf8mb4', collation='utf8mb4_unicode_ci'))  # lets see if it accepts the length, doesn't matter as long as it creates the row
    tags = Column(JSON)
    link = Column(VARCHAR(2048, charset='utf8mb4', collation='utf8mb4_unicode_ci'))
    author = Column(VARCHAR(255, charset='utf8mb4', collation='utf8mb4_unicode_ci'))
    last_updated_epoch_seconds = Column(Integer)
    edit_secret = Column(VARCHAR(255, charset='utf8mb4', collation='utf8mb4_unicode_ci'))
    boosters_per_player = Column(Integer)
    cards_per_booster = Column(Integer)
    set_card_colors = Column(Integer)
    color_balance_packs = Column(Integer)
    with_replacement = Column(Integer)
    popularity = Column(Integer)
    power_band = Column(String(255))
    card_list_views = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    drafts = Column(Integer, default=0)
    featured_card_printing = Column(VARCHAR(256, charset='utf8mb4', collation='utf8mb4_unicode_ci'))      
    cube_description = Column(VARCHAR(4096, charset='utf8mb4', collation='utf8mb4_unicode_ci'))      

API_SORT_TYPE_TO_COLUMN = {
    api.SortType.RANK: DbCubecanaCube.popularity,
    api.SortType.DATE: DbCubecanaCube.last_updated_epoch_seconds,
}

class CubeDao:
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

    def increment_card_list_views(self, cube_id: bytes) -> None:
        def operation(session, cube_id):
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
            if cube:
                cube.card_list_views += 1
                cube.popularity = (
                    cube.drafts * DRAFT_COEFFICIENT +
                    cube.card_list_views * LIST_VIEW_COEFFICIENT +
                    cube.page_views * PAGE_VIEW_COEFFICIENT
                )
                session.commit()

        self.execute(operation, cube_id=cube_id)

    def increment_page_views(self, cube_id: bytes) -> None:
        def operation(session, cube_id):
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
            if cube:
                cube.page_views += 1
                cube.popularity = (
                    cube.drafts * DRAFT_COEFFICIENT +
                    cube.card_list_views * LIST_VIEW_COEFFICIENT +
                    cube.page_views * PAGE_VIEW_COEFFICIENT
                )
                session.commit()

        self.execute(operation, cube_id=cube_id)

    def increment_drafts(self, cube_id: bytes) -> None:
        def operation(session, cube_id):
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
            if cube:
                cube.drafts += 1
                cube.popularity = (
                    cube.drafts * DRAFT_COEFFICIENT +
                    cube.card_list_views * LIST_VIEW_COEFFICIENT +
                    cube.page_views * PAGE_VIEW_COEFFICIENT
                )
                session.commit()

        self.execute(operation, cube_id=cube_id)

    def create_cubecana_cube(self, cube: DbCubecanaCube) -> None:
        def operation(session, cube: DbCubecanaCube):
            session.add(cube)
            session.commit()

        self.execute(operation, cube=cube)

    def update_cubecana_cube(self, cube_id: bytes, updated_cube: DbCubecanaCube) -> None:
        def operation(session, cube_id, updated_cube: DbCubecanaCube):
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
            if cube:
                cube.name = updated_cube.name
                cube.card_id_to_count = updated_cube.card_id_to_count
                cube.tags = updated_cube.tags
                cube.link = updated_cube.link
                cube.author = updated_cube.author
                cube.last_updated_epoch_seconds = updated_cube.last_updated_epoch_seconds
                cube.edit_secret = updated_cube.edit_secret
                cube.boosters_per_player = updated_cube.boosters_per_player
                cube.cards_per_booster = updated_cube.cards_per_booster
                cube.set_card_colors = updated_cube.set_card_colors
                cube.color_balance_packs = updated_cube.color_balance_packs
                cube.with_replacement = updated_cube.with_replacement
                cube.power_band = updated_cube.power_band
                cube.card_list_views = updated_cube.card_list_views
                cube.page_views = updated_cube.page_views          
                cube.drafts = updated_cube.drafts
                cube.featured_card_printing = updated_cube.featured_card_printing 
                cube.cube_description = updated_cube.cube_description
                session.commit()

        self.execute(operation, cube_id=cube_id, updated_cube=updated_cube)

    def delete_cubecana_cube(self, cube_id: bytes) -> None:
        def operation(session, cube_id):
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
            if cube:
                session.delete(cube)
                session.commit()

        self.execute(operation, cube_id=cube_id)


    def get_cubecana_cube_by_id(self, cube_id: bytes) -> Optional[DbCubecanaCube]:
        def operation(session, cube_id) -> Optional[DbCubecanaCube]:
            return session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()

        return self.execute(operation, cube_id=cube_id)

    def get_cubecana_cubes(self, page: int, per_page: int, sort: api.SortType, order: api.OrderType, tags: Optional[List[str]] = None, power_bands: Optional[List[str]] = None) -> List[DbCubecanaCube]:
        def operation(session, page, per_page, sort, order, tags, power_bands   ):
            sort_column = API_SORT_TYPE_TO_COLUMN[sort]
            query = session.query(DbCubecanaCube)
            if tags is not None and len(tags) > 0 and tags[0] != "":
                query = query.filter(DbCubecanaCube.tags.isnot(None)).filter(func.json_contains(DbCubecanaCube.tags, json.dumps(tags)))
            if power_bands is not None and len(power_bands) > 0 and power_bands[0] != "":
                query = query.filter(DbCubecanaCube.power_band.isnot(None)).filter(DbCubecanaCube.power_band.in_(power_bands))
            if order == api.OrderType.DESC:
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            return query.offset((page - 1) * per_page).limit(per_page).all()

        return self.execute(operation, page=page, per_page=per_page, sort=sort, order=order, tags=tags, power_bands=power_bands)

    def get_cubecana_cube_count(self) -> int:
        def operation(session):
            return session.query(DbCubecanaCube).count()

        return self.execute(operation)
    
cube_dao: CubeDao = CubeDao()