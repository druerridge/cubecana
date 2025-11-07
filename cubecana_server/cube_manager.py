import json
import uuid
import time
from dataclasses import dataclass
from typing import List
from . import api
import uuid
from .settings import Settings
from . import card_list_helper
from .cube_dao import cube_dao, DbCubecanaCube
from .cubecana_cube import CubecanaCube
from .card import PrintingId, toPrintingId
from .lorcast_api import lorcast_api as lorcana_api
from .dreamborn_manager import dreamborn_manager

class CubeManager:
    def determine_printing_id(self, maybe_printing_id_str:str) -> PrintingId:
        tokens = maybe_printing_id_str.split("-")
        if len(tokens) == 3:
            return toPrintingId(maybe_printing_id_str)
        if len(tokens) == 1:
            api_card = lorcana_api.get_api_card(maybe_printing_id_str)
            if api_card is None:
                return None # raise ValueError(f"Invalid PrintingId format: {maybe_printing_id_str} skipping")
            return api_card.default_printing.printing_id()

    def generate_printing_id_to_count(self, maybe_printing_id_str_to_count):
        printing_id_to_count = dict[PrintingId, int]()
        for maybe_printing_id_str, count in maybe_printing_id_str_to_count.items():
            printing_id = self.determine_printing_id(maybe_printing_id_str)
            if printing_id is None:
                continue # skipping invalid data
            printing_id_to_count[printing_id] = count
        return printing_id_to_count

    def from_db_cubecana_cube(self, db_cube: DbCubecanaCube) -> CubecanaCube:
        maybe_printing_id_str_to_count = json.loads(db_cube.card_id_to_count)
        printing_id_to_count = self.generate_printing_id_to_count(maybe_printing_id_str_to_count)
        featured_card_printing_id = toPrintingId(db_cube.featured_card_printing) if db_cube.featured_card_printing else None
        return CubecanaCube(
            name=db_cube.name,
            printing_id_to_count=printing_id_to_count,
            tags=db_cube.tags,
            link=db_cube.link,
            author=db_cube.author,
            last_updated_epoch_seconds=db_cube.last_updated_epoch_seconds,
            id=str(uuid.UUID(bytes=db_cube.id)),
            edit_secret=db_cube.edit_secret,
            card_list_views=db_cube.card_list_views,
            page_views=db_cube.page_views,          
            drafts=db_cube.drafts,
            featured_card_printing_id=featured_card_printing_id,
            cube_description=db_cube.cube_description,
            settings=Settings(
                boosters_per_player=db_cube.boosters_per_player,
                card_list_name=db_cube.name,
                cards_per_booster=db_cube.cards_per_booster,
                set_card_colors=db_cube.set_card_colors,
                color_balance_packs=db_cube.color_balance_packs,
                with_replacement=db_cube.with_replacement,
                power_band=db_cube.power_band,
                author=db_cube.author
            )
        )

    def to_db_cubecana_cube(self, cc_cube: CubecanaCube):
        new_uuid = uuid.UUID(cc_cube.id)
        new_id = new_uuid.bytes
        printing_id_str_to_count = {str(printing_id): count for printing_id, count in cc_cube.printing_id_to_count.items()}
        featured_card_printing_str = str(cc_cube.featured_card_printing_id) if cc_cube.featured_card_printing_id else None
        return DbCubecanaCube(
            id=new_id,
            name=cc_cube.name,
            card_id_to_count=json.dumps(printing_id_str_to_count),
            tags=cc_cube.tags,
            link=cc_cube.link,
            author=cc_cube.author,
            last_updated_epoch_seconds=cc_cube.last_updated_epoch_seconds,
            edit_secret=cc_cube.edit_secret,
            boosters_per_player=cc_cube.settings.boosters_per_player,
            cards_per_booster=cc_cube.settings.cards_per_booster,
            set_card_colors=cc_cube.settings.set_card_colors,
            color_balance_packs=cc_cube.settings.color_balance_packs,
            with_replacement=cc_cube.settings.with_replacement,
            power_band=cc_cube.settings.power_band,
            card_list_views=cc_cube.card_list_views,
            page_views=cc_cube.page_views,          
            drafts=cc_cube.drafts,
            featured_card_printing=featured_card_printing_str,
            cube_description=cc_cube.cube_description,
            popularity=0,
        )

    def get_cube_count(self):
       return cube_dao.get_cubecana_cube_count()
    
    def to_cube_list_entry(self, cube:CubecanaCube) -> api.CubeListEntry:
        expanded_tags = []
        expanded_tags.extend(cube.tags)
        expanded_tags.append("Power: " + cube.settings.power_band.lower())
        
        # Handle featured card image - use the featured card if available, otherwise use the first card in the cube
        featured_printing_id = cube.featured_card_printing_id
        if not featured_printing_id and cube.printing_id_to_count:
            featured_printing_id = next(iter(cube.printing_id_to_count))
        
        featured_image_link = ""
        if featured_printing_id:
            featured_printing = lorcana_api.get_card_printing(featured_printing_id)
            featured_image_link = featured_printing.image_uris.get("en", "")
        
        return api.CubeListEntry(
            name=cube.name,
            cardCount=cube.card_count(),
            tags=expanded_tags,
            link=cube.link,
            author=cube.author,
            lastUpdatedEpochSeconds=cube.last_updated_epoch_seconds,
            timesDrafted=cube.drafts,
            timesViewed=cube.page_views + cube.card_list_views,
            id=cube.id, 
            featuredCardImageLink=featured_image_link
        )

    def get_cubes(self, page: int = 1, per_page: int = 25, sort = api.SortType.RANK, order = api.OrderType.DESC, tags: List[str] = None) -> List[api.CubeListEntry]:
        paginated_db_cubecana_cubes: List[DbCubecanaCube] = cube_dao.get_cubecana_cubes(page, per_page, sort, order, tags)
        paginated_cubes = [self.from_db_cubecana_cube(dbcube) for dbcube in paginated_db_cubecana_cubes]
        paginated_cube_list_entries: api.CubeListEntry = [self.to_cube_list_entry(cube) for cube in paginated_cubes]
        return paginated_cube_list_entries

    def create_cube(self, api_create_cube: api.CreateCubeRequest):
        new_id = str(uuid.uuid4())
        edit_secret = str(uuid.uuid4())
        printing_id_to_count = card_list_helper.printing_id_to_count_from(api_create_cube.cardListText.split('\n'))
        featured_card_printing_id = None
        if api_create_cube.featuredCardPrintingId:
            featured_card_printing_id: PrintingId = card_list_helper.printing_id_from_human_readable_string(api_create_cube.featuredCardPrintingId)
        new_cube = CubecanaCube(
            name=api_create_cube.name,
            printing_id_to_count=printing_id_to_count,
            tags=api_create_cube.tags,
            link=api_create_cube.link,
            author=api_create_cube.author,
            last_updated_epoch_seconds=int(time.time()),
            id=new_id,
            edit_secret=edit_secret,
            featured_card_printing_id=featured_card_printing_id,
            cube_description=api_create_cube.cubeDescription,
            settings=Settings(
                card_list_name=api_create_cube.name,
                boosters_per_player=api_create_cube.cubeSettings.boostersPerPlayer,
                cards_per_booster=api_create_cube.cubeSettings.cardsPerBooster,
                power_band=api_create_cube.cubeSettings.powerBand,
                author=api_create_cube.author,
            ),
        )
        db_cubecana_cube = self.to_db_cubecana_cube(new_cube)
        cube_dao.create_cubecana_cube(db_cubecana_cube)
        return new_cube

    def get_cube(self, id: str) -> CubecanaCube:
        db_cube = cube_dao.get_cubecana_cube_by_id(uuid.UUID(id).bytes)
        if not db_cube:
           return None
        cube = self.from_db_cubecana_cube(db_cube)
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
        printing_id_to_count = card_list_helper.printing_id_to_count_from(api_edit_cube.cardListText.split('\n'))
        featured_card_printing_id: PrintingId = None
        if api_edit_cube.featuredCardPrintingId:
            featured_card_printing_id = card_list_helper.printing_id_from_human_readable_string(api_edit_cube.featuredCardPrintingId)
        updated_cube = CubecanaCube(
            name=api_edit_cube.name,
            printing_id_to_count=printing_id_to_count,
            tags=api_edit_cube.tags,
            link=api_edit_cube.link,
            author=api_edit_cube.author,
            last_updated_epoch_seconds=int(time.time()),
            id=api_edit_cube.id,
            edit_secret=old_cube.edit_secret,
            featured_card_printing_id=featured_card_printing_id,
            cube_description=api_edit_cube.cubeDescription,
            settings=Settings(
                card_list_name=api_edit_cube.name,
                boosters_per_player=api_edit_cube.cubeSettings.boostersPerPlayer,
                cards_per_booster=api_edit_cube.cubeSettings.cardsPerBooster,
                power_band=api_edit_cube.cubeSettings.powerBand,
                author=api_edit_cube.author,
            ),
            page_views=old_cube.page_views,
            card_list_views=old_cube.card_list_views,
            drafts=old_cube.drafts,
        )
        db_cubecana_cube = self.to_db_cubecana_cube(updated_cube)
        id_bytes = uuid.UUID(updated_cube.id).bytes
        cube_dao.update_cubecana_cube(cube_id=id_bytes, updated_cube=db_cubecana_cube)
        return updated_cube    
    
    # big perf hit, do only on startup or when not under load
    def get_all_cube_lists(self, tags: list[str] = None, power_bands: list[str] = None) -> List[dict[PrintingId, int]]:
        count = self.get_cube_count()
        db_cubes: list[DbCubecanaCube] = cube_dao.get_cubecana_cubes(page=1, per_page=count, sort=api.SortType.RANK, order=api.OrderType.DESC, tags=tags, power_bands=power_bands)
        cube_lists = [self.from_db_cubecana_cube(db_cube).printing_id_to_count for db_cube in db_cubes]
        return cube_lists
        
cube_manager: CubeManager = CubeManager()