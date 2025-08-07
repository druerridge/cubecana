import uuid
import time
from dataclasses import dataclass
import api
import draftmancer
from typing import List
import uuid
from settings import Settings
import card_list_helper
from cube_dao import cube_dao, DbCubecanaCube
from cubecana_cube import CubecanaCube, to_db_cubecana_cube, from_db_cubecana_cube

class CubeManager:
    def get_cube_count(self):
       return cube_dao.get_cubecana_cube_count()

    def get_cubes(self, page: int = 1, per_page: int = 25, sort = api.SortType.RANK, order = api.OrderType.DESC, tags: List[str] = None) -> List[api.CubeListEntry]:
        paginated_db_cubecana_cubes: List[DbCubecanaCube] = cube_dao.get_cubecana_cubes(page, per_page, sort, order, tags)
        paginated_cubes = [from_db_cubecana_cube(dbcube) for dbcube in paginated_db_cubecana_cubes]
        paginated_cube_list_entries: api.CubeListEntry = [cube.to_cube_list_entry() for cube in paginated_cubes]
        return paginated_cube_list_entries

    def create_cube(self, api_create_cube: api.CreateCubeRequest):
        new_id = str(uuid.uuid4())
        edit_secret = str(uuid.uuid4())
        id_to_count = card_list_helper.id_to_count_from(api_create_cube.cardListText.split('\n'))
        new_cube = CubecanaCube(
            name=api_create_cube.name,
            card_id_to_count=id_to_count,
            tags=api_create_cube.tags,
            link=api_create_cube.link,
            author=api_create_cube.author,
            last_updated_epoch_seconds=int(time.time()),
            id=new_id,
            edit_secret=edit_secret,
            settings=Settings(
                card_list_name=api_create_cube.name,
                boosters_per_player=api_create_cube.cubeSettings.boostersPerPlayer,
                cards_per_booster=api_create_cube.cubeSettings.cardsPerBooster,
                power_band=api_create_cube.cubeSettings.powerBand,
                author=api_create_cube.author,
            ),
        )
        db_cubecana_cube = to_db_cubecana_cube(new_cube)
        cube_dao.create_cubecana_cube(db_cubecana_cube)
        return new_cube

    def get_cube(self, id: str) -> CubecanaCube:
        db_cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(id).bytes)
        if not db_cube:
           return None
        cube = from_db_cubecana_cube(db_cube)
        return cube

    def delete_cube(self, id: str, edit_secret: str):
        cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(id).bytes)
        # just... double checking.
        if cube.edit_secret != edit_secret:
            return False
        cube_dao.delete_cubecana_cube(uuid.UUID(id).bytes)
        return True

    def increment_drafts(self, id: str):
        cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(id).bytes)
        if not cube:
            return False
        cube_dao.increment_drafts(uuid.UUID(id).bytes)
        return True

    def increment_page_views(self, id: str):
        cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(id).bytes)
        if not cube:
            return False
        cube_dao.increment_page_views(uuid.UUID(id).bytes)
        return True

    def increment_card_list_views(self, id: str):
        cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(id).bytes)
        if not cube:
            return False
        cube_dao.increment_card_list_views(uuid.UUID(id).bytes)
        return True

    def update_cube(self, api_edit_cube: api.EditCubeRequest):
        old_cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(api_edit_cube.id).bytes)
        id_to_count = card_list_helper.id_to_count_from(api_edit_cube.cardListText.split('\n'))
        updated_cube = CubecanaCube(
            name=api_edit_cube.name,
            card_id_to_count=id_to_count,
            tags=api_edit_cube.tags,
            link=api_edit_cube.link,
            author=api_edit_cube.author,
            last_updated_epoch_seconds=int(time.time()),
            id=api_edit_cube.id,
            edit_secret=old_cube.edit_secret,
            settings=Settings(
                card_list_name=api_edit_cube.name,
                boosters_per_player=api_edit_cube.cubeSettings.boostersPerPlayer,
                cards_per_booster=api_edit_cube.cubeSettings.cardsPerBooster,
                power_band=api_edit_cube.cubeSettings.powerBand,
                author=api_edit_cube.author,
            ),
        )
        db_cubecana_cube = to_db_cubecana_cube(updated_cube)
        id_bytes = uuid.UUID(updated_cube.id).bytes
        cube_dao.update_cubecana_cube(cube_id=id_bytes, updated_cube=db_cubecana_cube)
        return updated_cube    
    
    # big perf hit, do only on startup or when not under load
    def get_all_cube_lists(self, tags: list[str] = None, power_bands: list[str] = None) -> List[dict[str, int]]:
        count = self.get_cube_count()
        db_cubes: list[DbCubecanaCube] = cube_dao.get_cubecana_cubes(page=1, per_page=count, sort=api.SortType.RANK, order=api.OrderType.DESC, tags=tags, power_bands=power_bands)
        cube_lists = [from_db_cubecana_cube(db_cube).card_id_to_count for db_cube in db_cubes]
        return cube_lists
        
cube_manager: CubeManager = CubeManager()