from dataclasses import dataclass
import traceback
from . import api
from typing import List
from . import lcc_error
from . import draftmancer
from . import generate_retail
from .lorcast_api import lorcast_api

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
        ratings_missing: bool = False
        # release_date: # some day - maybe use the APIs?

        def to_retail_set_entry(self) -> api.RetailSetEntry:
                return api.RetailSetEntry(
                        name=self.name,
                        id=self.id,
                        defaultGameMode=get_default_game_mode(self.name),
                        availableGameModes=get_available_game_modes(self.name),
                        ratingsMissing=self.ratings_missing,
                )

class RetailManager:
    def __init__(self):
        self.retail_sets: dict[str, RetailSet] = {}

    def init(self):
        self.regenerate_retail_sets()
        lorcast_api.add_cache_loaded_listener(self.regenerate_retail_sets)

    def generate_retail_set(self, set_code: str) -> RetailSet:
        draftmancer_file_contents = generate_retail.generate_retail_set_file(set_code)
        # parse to validate the generated file before serving it
        draftmancer_file: draftmancer.DraftmancerFile = draftmancer.read_draftmancer_file_as_string(draftmancer_file_contents)
        ratings_missing = bool(getattr(draftmancer_file.draftmancer_settings, 'ratingsMissing', False))
        return RetailSet(set_code, draftmancer_file.draftmancer_settings.name, draftmancer_file_contents, ratings_missing)

    def regenerate_retail_sets(self):
        retail_sets: dict[str, RetailSet] = {}
        for set_code in generate_retail.RETAIL_SETS:
            try:
                retail_sets[set_code] = self.generate_retail_set(set_code)
            except Exception:
                print(f"Failed to generate retail set {set_code}:")
                traceback.print_exc()
                if set_code in self.retail_sets:
                    print(f"Keeping previously generated retail set {set_code}")
                    retail_sets[set_code] = self.retail_sets[set_code]
        self.retail_sets = retail_sets
        print(f"Generated {len(retail_sets)} retail sets.")

    def get_set_count(self) -> int:
       return self.retail_sets.__len__()

    def get_sets(self, page: int = 1, per_page: int = 25, order = api.OrderType.DESC) -> List[api.RetailSetEntry]:
        start = (page - 1) * per_page
        end = start + per_page
        retail_sets_list = sorted(self.retail_sets.values(), key=lambda x: int(x.id), reverse=(order == api.OrderType.DESC))
        paginated_retail_sets: List[RetailSet] = retail_sets_list[start:end]
        paginated_retail_set_entries:List[api.RetailSetEntry] = [retail_set.to_retail_set_entry() for retail_set in paginated_retail_sets]
        return paginated_retail_set_entries

    def get_set(self, id: str) -> RetailSet:
        retail_set = self.retail_sets.get(id)
        if retail_set is None:
            raise lcc_error.RetailSetNotFoundError(f"Retail set with id {id} not found")
        return api.RetailSet(id=retail_set.id, name=retail_set.name, draftmancerFile=retail_set.draftmancer_file_contents)

retail_manager: RetailManager = RetailManager()
retail_manager.init()