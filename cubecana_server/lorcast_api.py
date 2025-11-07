from pathlib import Path
import json

from .dreamborn_manager import dreamborn_manager
from . import id_helper
import requests
from .card import ApiCard, CardPrinting, PrintingId, toPrintingId
from .lorcana import ALT_ART_RARITIES

CACHED_API_DATA_FILEPATH = 'inputs/lorcast_api_cache/lorcast_api_data_cache.json'
CACHED_API_DATA_SET_Q1_FILEPATH = 'inputs/lorcast_api_cache/lorcast_api_data_cache_q1.json'

lorcast_to_cubecana_rarity =  {
    "Common" : "Common",
    "Uncommon" : "Uncommon",
    "Rare" : "Rare",
    "Super_rare" : "Super Rare",
    "Legendary" : "Legendary",
    "Epic": "Epic",
    "Promo": "Legendary",
    "Epic": "Epic",
    "Enchanted": "Enchanted",
    "Iconic": "Iconic",
}

class LorcastApi:
    def __init__(self):
        self.id_to_api_card: dict[str, ApiCard] = {}
    
    def get_lorcast_full_name(self, printing_untyped: dict) -> str:
        if 'version' in printing_untyped:
            return f"{printing_untyped['name']} - {printing_untyped['version']}"
        return printing_untyped['name']

    def id_from_printing_untyped(self, printing_untyped: dict) -> str:
        lorcast_full_name = self.get_lorcast_full_name(printing_untyped)
        return id_helper.to_id(lorcast_full_name)

    def fetch_api_data(self) -> dict[str, dict]:
        printing_id_str_to_printing_untyped: dict[str, dict] = {}
        # get sets
        url = f'https://api.lorcast.com/v0/sets'
        print(f'Fetching {url}...')
        res = requests.get(url=url)
        sets_data = res.json()
        if sets_data is None:
            raise Exception('Failed to fetch sets no json data')
        if 'results' not in sets_data:
            raise Exception('Failed to fetch sets no results in response')
        sets_results = sets_data['results']
        if sets_results is None:
            raise Exception(f'Failed to fetch sets: results are None')
        for set in sets_results:
            code = set['code']
            url = f'https://api.lorcast.com/v0/sets/{code}/cards'
            print(f'Fetching {url}...')
            res = requests.get(url=url)
            cards_in_set = res.json()
            # iterate cards
            for printing_untyped in cards_in_set:
                printing_id = PrintingId(
                    card_id=self.id_from_printing_untyped(printing_untyped),
                    collector_id=printing_untyped['collector_number'],
                    set_code=printing_untyped['set']['code']
                )
                printing_id_str_to_printing_untyped[printing_id.__str__()] = printing_untyped
        return printing_id_str_to_printing_untyped

    def get_cannonical_name(self, printing_untyped:dict) -> str:
        card_id = self.id_from_printing_untyped(printing_untyped)
        dreamborn_name = dreamborn_manager.get_id_to_dreamborn_name(card_id)
        if dreamborn_name is not None:
            return dreamborn_name
        return self.get_lorcast_full_name(printing_untyped)

    def api_card_from(self, printing_untyped) -> ApiCard:
        printing: CardPrinting = self.printing_from_printing_untyped(printing_untyped)
        full_name = self.get_cannonical_name(printing_untyped)
        
        # Extract classifications (traits), strength, and willpower from API data
        classifications = printing_untyped.get('classifications', []) or []
        strength = printing_untyped.get('strength')
        willpower = printing_untyped.get('willpower')
        
        return ApiCard(
            full_name=full_name,    
            cost=printing_untyped['cost'], 
            color=printing_untyped['ink'],
            inks=printing_untyped['inks'],
            types=printing_untyped['type'],
            card_printings=[printing],
            default_printing=printing,
            classifications=classifications,
            strength=strength,
            willpower=willpower
        )

    def printing_from_printing_untyped(self, printing_untyped) -> CardPrinting:
        full_name = self.get_cannonical_name(printing_untyped)
        return CardPrinting(
            full_name=full_name,
            collector_id=printing_untyped['collector_number'],
            set_code=printing_untyped['set']['code'],
            rarity=lorcast_to_cubecana_rarity[printing_untyped['rarity']],
            image_uris={
                'en':printing_untyped['image_uris']['digital']['normal']
            }
        )

    def is_alternate_art(self, printing: CardPrinting) -> bool:
        return self.is_number(printing.collector_id) and int(printing.collector_id) > 204

    def is_number(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False
        
    def is_core_printing(self, printing: CardPrinting) -> bool:
        return self.is_core_set(printing.set_code) and not self.is_alternate_art(printing)

    def is_core_set(self, set_code: str) -> bool:
        # core sets are pure numbers while promos and special sets are not
        return self.is_number(set_code)

    def generate_id_to_api_card(self, printing_id_str_to_printing_untyped: dict[PrintingId, dict]) -> dict[str, ApiCard]:
        id_to_api_card: dict[str, ApiCard] = {}
        for printing_id_str in printing_id_str_to_printing_untyped:
            printing_id = toPrintingId(printing_id_str)
            printing_untyped = printing_id_str_to_printing_untyped[printing_id_str]
            if printing_id.card_id in id_to_api_card:
                api_card = id_to_api_card[printing_id.card_id]
                new_printing = self.printing_from_printing_untyped(printing_untyped)
                api_card.card_printings.append(new_printing)
                if self.is_core_printing(new_printing) and not self.is_core_printing(api_card.default_printing):
                    api_card.default_printing = new_printing
            else:
                id_to_api_card[printing_id.card_id] = self.api_card_from(printing_untyped)
        return id_to_api_card

    def fetch_set_q1_data(self) -> dict[PrintingId, dict]:
        printing_id_str_to_printing_untyped = {}
        cached_set_q1_api_data_file = Path(CACHED_API_DATA_SET_Q1_FILEPATH)
        with cached_set_q1_api_data_file.open(mode='r') as file_to_read:
            printing_id_str_to_printing_untyped = json.load(file_to_read)    
        return printing_id_str_to_printing_untyped

    def get_card_printing(self, printing_id: PrintingId) -> CardPrinting | None:
        api_card = self.get_api_card(printing_id.card_id)
        if not api_card:
            return None
        card_printing = next((printing for printing in api_card.card_printings if printing.printing_id() == printing_id), None)
        if card_printing == None:
            return api_card.default_printing
        return card_printing

    def get_api_card(self, card_id: str) -> ApiCard | None:
        return self.id_to_api_card.get(card_id)

    def read_or_fetch_id_to_api_card(self) -> dict[str, ApiCard]:
        return self.id_to_api_card

    def get_cards_from_set(self, set_code: str) -> list[ApiCard]:
        return [api_card for api_card in self.id_to_api_card.values() if any(printing.set_code == set_code for printing in api_card.card_printings)]
    
    def init(self):
        cached_api_data_file = Path(CACHED_API_DATA_FILEPATH)
        if not cached_api_data_file.is_file():
            printing_id_to_printing_untyped = self.fetch_api_data()
            print("Fetching set Q1 cards from local file...")
            printing_id_to_printing_untyped_q1 = self.fetch_set_q1_data()
            printing_id_to_printing_untyped.update(printing_id_to_printing_untyped_q1) # merge the two dicts
            # self.fix_card_names(name_to_printing_untyped)
            Path(cached_api_data_file).parent.mkdir(parents=True, exist_ok=True)
            with cached_api_data_file.open(mode='w') as file_to_write:
                json.dump(printing_id_to_printing_untyped, file_to_write)

        with cached_api_data_file.open(mode='r') as file_to_read:
            printing_id_str_to_printing_untyped = json.load(file_to_read)
            id_to_api_card = self.generate_id_to_api_card(printing_id_str_to_printing_untyped)
        self.id_to_api_card = id_to_api_card

        # self.print_all_printing_ids_to_file()

    # def print_all_printing_ids_to_file(self, output_filepath: str = 'test_data/all_printing_ids.txt'):
    #     output_file = Path(output_filepath)
    #     output_file.parent.mkdir(parents=True, exist_ok=True)
    #     count = 1
    #     with output_file.open(mode='w', encoding='utf-8') as file:
    #         for card_id, api_card in self.id_to_api_card.items():
    #             for printing in api_card.card_printings:
    #                 if printing.set_code != '9':
    #                     file.write(f"{count} {api_card.full_name} ({printing.printing_id().set_code}) {printing.printing_id().collector_id}\n")
    #     print(f"All PrintingIds written to {output_filepath}")

    # def fix_card_name(self, name_to_card, old_full_name, new_full_name):
    #     if old_full_name not in name_to_card:
    #         return
    #     name_to_card[new_full_name] = name_to_card[old_full_name]
    #     splits = new_full_name.split(' - ')
    #     new_name = splits[0]
    #     name_to_card[new_full_name]['name'] = new_name
    #     if len(splits) > 1:
    #         new_version = splits[1]
    #         name_to_card[new_full_name]['version'] = new_version
    #     del name_to_card[old_full_name]    

    # def fix_card_names(self, name_to_printing_untyped):
    #     # there are typos in the https://api.lorcana-api.com card names.  We have to fix those or we cannot translate between data sources
    #     print("Fixing card names")

lorcast_api: LorcastApi = LorcastApi()
lorcast_api.init()