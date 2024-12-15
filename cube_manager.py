import uuid
import time
from dataclasses import dataclass
import api
import create_template
from typing import List
import uuid
from settings import Settings

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

class CubeManager:
    cubes: dict[str, CubecanaCube] = {} 

    def get_cubes(self, page: int = 1, per_page: int = 10):
        start = (page - 1) * per_page
        end = start + per_page
        paginated_cubecana_cubes = list(self.cubes.values())[start:end]
        paginated_cube_list_entries = [cube.to_cube_list_entry() for cube in paginated_cubecana_cubes]
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
                boosters_per_player=api_create_cube.cubeSettings.boostersPerPlayer,
                cards_per_booster=api_create_cube.cubeSettings.cardsPerBooster
            ),
        )
        self.cubes[new_id] = new_cube
        return new_cube

    def get_cube(self, id: str):
        cube = self.cubes.get(id)
        return cube

    def update_cube(self, api_edit_cube: api.EditCubeRequest):
        old_cube = self.cubes.get(api_edit_cube.id)
        id_to_count = create_template.id_to_count_from(api_edit_cube.cardListText.split('\n'))
        updated_cube = CubecanaCube(
            name=api_edit_cube.name,
            card_id_to_count=id_to_count,
            tags=api_edit_cube.tags,
            link=api_edit_cube.link,
            author=api_edit_cube.author,
            last_updated_epoch_seconds=int(time.time()),
            id=old_cube.id,
            edit_secret=old_cube.edit_secret,
            settings=Settings(
                boosters_per_player=api_edit_cube.cubeSettings.boostersPerPlayer,
                cards_per_booster=api_edit_cube.cubeSettings.cardsPerBooster
            ),
        )
        self.cubes[old_cube.id] = updated_cube
        return updated_cube    

cube_manager: CubeManager = CubeManager()