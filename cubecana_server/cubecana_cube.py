import json
import uuid
import time
from dataclasses import dataclass
from . import api
from typing import List
import uuid
from .settings import Settings
from .cube_dao import DbCubecanaCube
from .card import PrintingId, ApiCard, toPrintingId

@dataclass(frozen=True)
class CubecanaCube:
    name: str
    printing_id_to_count: dict[PrintingId, int]
    tags: List[str]
    link: str
    author: str
    last_updated_epoch_seconds: int
    id: str
    edit_secret: str
    settings: Settings
    card_list_views: int = 0
    page_views: int = 0     
    drafts: int = 0  

    def card_count(self):
        return sum(self.printing_id_to_count.values())

    def to_cube_list_entry(self) -> api.CubeListEntry:
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
            timesDrafted=self.drafts,
            timesViewed=self.page_views + self.card_list_views,
            id=self.id
        )

    def to_api_cube(self, id_to_api_card:dict[str, ApiCard]) -> api.Cube:
        full_name_to_card_count = dict[str, int]()
        printing_id_str_to_count = {str(printing_id): count for printing_id, count in self.printing_id_to_count.items()}
        for printing_id, count in self.printing_id_to_count.items():
            api_card = id_to_api_card.get(printing_id.card_id)
            if api_card:
                if printing_id == api_card.default_printing.printing_id():
                    full_name_to_card_count[f"{api_card.full_name}"] = count
                else:
                    full_name_to_card_count[f"{api_card.full_name} ({printing_id.set_code}) {printing_id.collector_id}"] = count

        featured_card_printing = next(iter(self.printing_id_to_count))
        return api.Cube(
            name=self.name,
            cardIdToCardCount=printing_id_str_to_count,
            nameToCardCount=full_name_to_card_count,
            tags=self.tags,
            link=self.link,
            author=self.author,
            lastUpdatedEpochSeconds=self.last_updated_epoch_seconds,
            id=self.id,
            cubeSettings=self.settings.to_api_cube_settings(),
            description= f"A power cube featuring cards across {len(full_name_to_card_count)} unique card names.",
            featuredCardImageLink = f"https://cdn.dreamborn.ink/images/en/cards/{featured_card_printing.set_code.zfill(3)}-{featured_card_printing.collector_id.zfill(3)}",
            timesViewed=self.page_views + self.card_list_views,
            timesDrafted=self.drafts
        )