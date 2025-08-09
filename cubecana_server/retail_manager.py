from dataclasses import dataclass
from pathlib import Path
from . import api
from typing import List
from . import lcc_error
from . import draftmancer

RETAIL_SETS_DIR_PATH = "inputs/retail_sets"
GAME_MODE_SUPER_SEALED = "SUPER_SEALED"
GAME_MODE_SEALED = "SEALED"
GAME_MODE_DRAFT = "DRAFT"

def get_default_game_mode(retail_set_name) -> str:
    if "Super Sealed" in retail_set_name:
        return GAME_MODE_SUPER_SEALED
    return GAME_MODE_DRAFT

def get_available_game_modes(retail_set_name) -> str:
    if "Super Sealed" in retail_set_name:
        return [GAME_MODE_SUPER_SEALED]
    return [GAME_MODE_DRAFT, GAME_MODE_SEALED]

@dataclass(frozen=True)
class RetailSet:
  id: str
  name: str
  draftmancer_file_contents: str
  # release_date: # some day - maybe use the APIs?
  
  def to_retail_set_entry(self) -> api.RetailSetEntry:
    return api.RetailSetEntry(
      name=self.name,
      id=self.id, 
      defaultGameMode=get_default_game_mode(self.name),
      availableGameModes=get_available_game_modes(self.name)
    )

class RetailManager:
    def __init__(self):
        self.retail_sets: dict[str, RetailSet] = {}
        self.load_retail_sets(RETAIL_SETS_DIR_PATH)

    def generate_retail_set(self, file: Path) -> RetailSet:
        draftmancer_file:draftmancer.DraftmancerFile = draftmancer.read_draftmancer_file(file)
        set_id = file.stem.rstrip('.draftmancer')
        return RetailSet(set_id, draftmancer_file.draftmancer_settings.name, draftmancer_file.text_contents)

    def load_retail_sets(self, retail_sets_filepath: str):
        retail_sets_path = Path(retail_sets_filepath)
        if not retail_sets_path.is_dir():
            raise Exception(f"retail_sets_filepath at {retail_sets_filepath} is not a directory")
        files = retail_sets_path.glob('*')
        for file in files:
            if file.is_file():
                print("loading: " + str(file))
                retail_set = self.generate_retail_set(file)
                self.retail_sets[retail_set.id] = retail_set

    def get_set_count(self) -> int:
       return self.retail_sets.__len__()

    def get_sets(self, page: int = 1, per_page: int = 25, order = api.OrderType.DESC) -> List[api.RetailSetEntry]:
        start = (page - 1) * per_page
        end = start + per_page
        retail_sets_list = list(self.retail_sets.values())
        paginated_retail_sets: List[RetailSet] = sorted(retail_sets_list[start:end], key=lambda x: x.id, reverse=(order == api.OrderType.DESC))
        paginated_retail_set_entries:List[api.RetailSetEntry] = [retail_set.to_retail_set_entry() for retail_set in paginated_retail_sets]
        return paginated_retail_set_entries

    def get_set(self, id: str) -> RetailSet:
        retail_set = self.retail_sets.get(id)
        if retail_set is None:
            raise lcc_error.RetailSetNotFoundError(f"Retail set with id {id} not found")
        return api.RetailSet(id=retail_set.id, name=retail_set.name, draftmancerFile=retail_set.draftmancer_file_contents)

retail_manager: RetailManager = RetailManager()