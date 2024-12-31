import json
import uuid
import time
from dataclasses import dataclass
import api
import create_template
from typing import List
import uuid
from settings import Settings
from cube_dao import cube_dao, DbCubecanaCube

@dataclass(frozen=True)
class CubecanaCube:
  name: str
  card_id_to_count: dict[str, int]
  tags: List[str]
  link: str
  author: str
  last_updated_epoch_seconds: int
  id: str
  edit_secret: str
  settings: Settings
  
  def card_count(self):
    return sum(self.card_id_to_count.values())
  
  def to_cube_list_entry(self):
    return api.CubeListEntry(
      name=self.name,
      cardCount=self.card_count(),
      tags=self.tags,
      link=self.link,
      author=self.author,
      lastUpdatedEpochSeconds=self.last_updated_epoch_seconds,
      id=self.id
    )
  
  def to_api_cube(self) -> api.Cube:
    return api.Cube(
      name=self.name,
      cardIdToCardCount=self.card_id_to_count,
      nameToCardCount=self.card_id_to_count,
      tags=self.tags,
      link=self.link,
      author=self.author,
      lastUpdatedEpochSeconds=self.last_updated_epoch_seconds,
      id=self.id,
      cubeSettings=self.settings.to_api_cube_settings()
    )

def to_db_cubecana_cube(cc_cube: CubecanaCube):
    new_uuid = uuid.UUID(cc_cube.id)
    new_id = new_uuid.bytes
    return DbCubecanaCube(
        id=new_id,
        name=cc_cube.name.encode('utf-8'),
        card_id_to_count=json.dumps(cc_cube.card_id_to_count).encode('utf-8'), # come back to this
        tags=json.dumps(cc_cube.tags),
        link=cc_cube.link.encode('utf-8'),
        author=cc_cube.author.encode('utf-8'),
        last_updated_epoch_seconds=cc_cube.last_updated_epoch_seconds,
        edit_secret=cc_cube.edit_secret.encode('utf-8'),
        boosters_per_player=cc_cube.settings.boosters_per_player,
        cards_per_booster=cc_cube.settings.cards_per_booster,
        set_card_colors=cc_cube.settings.set_card_colors,
        color_balance_packs=cc_cube.settings.color_balance_packs,
        with_replacement=cc_cube.settings.with_replacement,
        popularity=0
    )

def from_db_cubecana_cube(db_cube: DbCubecanaCube) -> CubecanaCube:
    return CubecanaCube(
        name=db_cube.name,
        card_id_to_count=json.loads(db_cube.card_id_to_count),
        tags=json.loads(db_cube.tags),
        link=db_cube.link,
        author=db_cube.author,
        last_updated_epoch_seconds=db_cube.last_updated_epoch_seconds,
        id=str(uuid.UUID(bytes=db_cube.id)),
        edit_secret=db_cube.edit_secret,
        settings=Settings(
            boosters_per_player=db_cube.boosters_per_player,
            card_list_name=db_cube.name,
            cards_per_booster=db_cube.cards_per_booster,
            set_card_colors=db_cube.set_card_colors,
            color_balance_packs=db_cube.color_balance_packs,
            with_replacement=db_cube.with_replacement
        )
    )

class CubeManager:
    def get_cube_count(self):
       return cube_dao.get_cubecana_cube_count()

    def get_cubes(self, page: int = 1, per_page: int = 25, sort = api.SortType.RANK, order = api.OrderType.DESC):
        paginated_db_cubecana_cubes = cube_dao.get_cubecana_cubes_paginated_by(page, per_page, sort, order)
        # paginated_db_cubecana_cubes = cube_dao.get_cubecana_cubes_paginated_by_popularity(page, per_page)
        paginated_cubes = [from_db_cubecana_cube(dbcube) for dbcube in paginated_db_cubecana_cubes]
        paginated_cube_list_entries = [cube.to_cube_list_entry() for cube in paginated_cubes]
        return paginated_cube_list_entries

    def create_cube(self, api_create_cube: api.CreateCubeRequest):
        new_id = str(uuid.uuid4())
        edit_secret = str(uuid.uuid4())
        id_to_count = create_template.id_to_count_from(api_create_cube.cardListText.split('\n'))
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
                cards_per_booster=api_create_cube.cubeSettings.cardsPerBooster
            ),
        )
        db_cubecana_cube = to_db_cubecana_cube(new_cube)
        cube_dao.create_cubecana_cube(db_cubecana_cube)
        return new_cube

    def get_cube(self, id: str):
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

    def update_cube(self, api_edit_cube: api.EditCubeRequest):
        old_cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(api_edit_cube.id).bytes)
        id_to_count = create_template.id_to_count_from(api_edit_cube.cardListText.split('\n'))
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
                cards_per_booster=api_edit_cube.cubeSettings.cardsPerBooster
            ),
        )
        db_cubecana_cube = to_db_cubecana_cube(updated_cube)
        id_bytes = uuid.UUID(updated_cube.id).bytes
        cube_dao.update_cubecana_cube(cube_id=id_bytes, updated_cube=db_cubecana_cube)
        return updated_cube    

cube_manager: CubeManager = CubeManager()