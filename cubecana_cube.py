import json
import uuid
import time
from dataclasses import dataclass
import api
from typing import List
import uuid
from settings import Settings
from cube_dao import DbCubecanaCube

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
    card_list_views: int
    page_views: int     
    drafts: int      
    settings: Settings  

    def card_count(self):
        return sum(self.card_id_to_count.values())

    def to_cube_list_entry(self):
        expanded_tags = []
        expanded_tags.extend(self.tags)
        expanded_tags.append("Power: " + self.settings.power_band.lower())
        return api.CubeListEntry(
            name=self.name,
            cardCount=self.card_count(),
            tags=expanded_tags,
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
        card_id_to_count=json.dumps(cc_cube.card_id_to_count).encode('utf-8'),
        tags=cc_cube.tags,
        link=cc_cube.link.encode('utf-8'),
        author=cc_cube.author.encode('utf-8'),
        last_updated_epoch_seconds=cc_cube.last_updated_epoch_seconds,
        edit_secret=cc_cube.edit_secret.encode('utf-8'),
        boosters_per_player=cc_cube.settings.boosters_per_player,
        cards_per_booster=cc_cube.settings.cards_per_booster,
        set_card_colors=cc_cube.settings.set_card_colors,
        color_balance_packs=cc_cube.settings.color_balance_packs,
        with_replacement=cc_cube.settings.with_replacement,
        power_band=cc_cube.settings.power_band,
        card_list_views=cc_cube.card_list_views,
        page_views=cc_cube.page_views,          
        drafts=cc_cube.drafts,
        popularity=0,                   
    )

def from_db_cubecana_cube(db_cube: DbCubecanaCube) -> CubecanaCube:
    return CubecanaCube(
        name=db_cube.name,
        card_id_to_count=json.loads(db_cube.card_id_to_count),
        tags=db_cube.tags,
        link=db_cube.link,
        author=db_cube.author,
        last_updated_epoch_seconds=db_cube.last_updated_epoch_seconds,
        id=str(uuid.UUID(bytes=db_cube.id)),
        edit_secret=db_cube.edit_secret,
        card_list_views=db_cube.card_list_views,
        page_views=db_cube.page_views,          
        drafts=db_cube.drafts,                
        settings=Settings(
            boosters_per_player=db_cube.boosters_per_player,
            card_list_name=db_cube.name,
            cards_per_booster=db_cube.cards_per_booster,
            set_card_colors=db_cube.set_card_colors,
            color_balance_packs=db_cube.color_balance_packs,
            with_replacement=db_cube.with_replacement,
            power_band=db_cube.power_band
        )
    )