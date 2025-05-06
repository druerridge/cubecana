import json
from pathlib import Path
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import BINARY
import api
import uuid

Base = declarative_base()

MAX_CARD_LIST_LENGTH = 80000 # MIGHT have to update the DB if you change this... but maybe not


class DbCubecanaCube(Base):
    __tablename__ = 'cubecana_cubes'
    pk = Column(Integer, primary_key=True)
    id = Column(BINARY(16), default=lambda: uuid.uuid4().bytes, unique=True, nullable=False)
    name = Column(String(255))
    card_id_to_count = Column(Text(MAX_CARD_LIST_LENGTH)) # lets see if it accepts the length, doesn't matter as long as it creates the row
    tags = Column(JSON)
    link = Column(String(2048))
    author = Column(String(255))
    last_updated_epoch_seconds = Column(Integer)
    edit_secret = Column(String(255))
    boosters_per_player = Column(Integer)
    cards_per_booster = Column(Integer)
    set_card_colors = Column(Integer)
    color_balance_packs = Column(Integer)
    with_replacement = Column(Integer)
    popularity = Column(Integer)
    power_band = Column(String(255))

API_SORT_TYPE_TO_COLUMN =  {
    api.SortType.RANK: DbCubecanaCube.popularity,
    api.SortType.DATE: DbCubecanaCube.last_updated_epoch_seconds,
}

class CubeDao:
    def __init__(self):
        creds_file = Path('creds/creds.json')
        if creds_file.is_file():
            with creds_file.open() as f:
                creds_json = json.load(f)
                self.db_url = f"mysql://{creds_json['db_username']}:{creds_json['db_password']}@{creds_json['db_host']}/{creds_json['db_name']}?charset=utf8"
        else:
            print("No creds file found, exiting")
            raise SystemExit(1)

    def get_session(self):
        engine = create_engine(self.db_url)
        Session = sessionmaker(bind=engine)
        return Session()

    def create_cubecana_cube(self, cube: DbCubecanaCube) -> None:
        session = self.get_session()
        try:
            session.add(cube)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_cubecana_cube(self, cube_id: bytes, updated_cube: DbCubecanaCube) -> None:
        session = self.get_session()
        try:
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
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_cubecana_cube(self, cube_id: bytes) -> None:
        session = self.get_session()
        try:
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
            if cube:
                session.delete(cube)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_cubecana_cube_by_id(self, cube_id: bytes) -> Optional[DbCubecanaCube]:
        session = self.get_session()
        try:
            cube = session.query(DbCubecanaCube).filter(DbCubecanaCube.id == cube_id).first()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return cube

    def get_cubecana_cubes_paginated_by(self, page: int, per_page: int, sort: api.SortType, order: api.OrderType) -> List[DbCubecanaCube]:
        session = self.get_session()
        sort_column = API_SORT_TYPE_TO_COLUMN[sort]
        try:
            if order == api.OrderType.DESC:
                cubes = session.query(DbCubecanaCube).order_by(sort_column.desc()).offset((page - 1) * per_page).limit(per_page).all()
            else:
                cubes = session.query(DbCubecanaCube).order_by(sort_column.asc()).offset((page - 1) * per_page).limit(per_page).all()
            return cubes
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_cubecana_cube_count(self) -> int:
        session = self.get_session()
        try:
            count = session.query(DbCubecanaCube).count()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return count

cube_dao: CubeDao = CubeDao()