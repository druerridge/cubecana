from dataclasses import dataclass
from . import api
from typing import List
from .settings import Settings
from .card import PrintingId, ApiCard

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
    featured_card_printing_id: PrintingId = None
    card_list_views: int = 0
    page_views: int = 0     
    drafts: int = 0  
    cube_description: str = ""

    def card_count(self):
        return sum(self.printing_id_to_count.values())

    def to_api_cube(self, id_to_api_card:dict[str, ApiCard]) -> api.Cube:
        full_name_to_card_count = dict[str, int]()
        for printing_id, count in self.printing_id_to_count.items():
            api_card = id_to_api_card.get(printing_id.card_id)
            if api_card:
                if printing_id == api_card.default_printing.printing_id():
                    full_name_to_card_count[f"{api_card.full_name}"] = count
                else:
                    full_name_to_card_count[f"{api_card.full_name} ({printing_id.set_code}) {printing_id.collector_id}"] = count

        
        # Get human-readable format with full card name if possible

        featured_card_printing_id = self.featured_card_printing_id if self.featured_card_printing_id else next(iter(self.printing_id_to_count))
        featured_card_image_link = ""
        if self.featured_card_printing_id:
            featured_card_printing_id = self.featured_card_printing_id
            
        api_card = id_to_api_card.get(featured_card_printing_id.card_id)
        if api_card:
            featured_card_printing_id_str = f"{api_card.full_name} ({featured_card_printing_id.set_code}) {featured_card_printing_id.collector_id}"
            
            featured_card_printing = next((printing for printing in api_card.card_printings if printing.printing_id() == featured_card_printing_id), None)
            if featured_card_printing == None:
                featured_card_printing = api_card.default_printing

            featured_card_image_link = featured_card_printing.image_uris.get("en", "")
        else:
            featured_card_printing_id_str = featured_card_printing_id.to_human_readable()
        
        return api.Cube(
            name=self.name,
            nameToCardCount=full_name_to_card_count,
            tags=self.tags,
            link=self.link,
            author=self.author,
            lastUpdatedEpochSeconds=self.last_updated_epoch_seconds,
            id=self.id,
            cubeSettings=self.settings.to_api_cube_settings(),
            featuredCardImageLink=featured_card_image_link,
            featuredCardPrintingId=featured_card_printing_id_str,
            cubeDescription=self.cube_description,
            timesViewed=self.page_views + self.card_list_views,
            timesDrafted=self.drafts
        )