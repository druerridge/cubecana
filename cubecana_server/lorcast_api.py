from pathlib import Path
import json
from . import id_helper
import requests
from .card import ApiCard, CardPrinting, PrintingId, toPrintingId

CACHED_API_DATA_FILEPATH = 'inputs/lorcast_api_cache/lorcast_api_data_cache.json'
CACHED_API_DATA_SET_Q1_FILEPATH = 'inputs/lorcast_api_cache/lorcast_api_data_cache_q1.json'

lorcast_to_dtd_rarity =  {
    "Common" : "Common",
    "Uncommon" : "Uncommon",
    "Rare" : "Rare",
    "Super_rare" : "Super Rare",
    "Legendary" : "Legendary",
    "Promo": "Legendary",
    "Enchanted": "Legendary",
}

class LorcastApi:
    def __init__(self):
        self.id_to_api_card: dict[str, ApiCard] = {}

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
            for card in cards_in_set:
                full_name = self.get_full_name(card)
                printing_id = PrintingId(
                    card_id=id_helper.to_id(full_name),
                    collector_id=card['collector_number'],
                    set_code=card['set']['code']
                )
                printing_id_str_to_printing_untyped[printing_id.__str__()] = card
        return printing_id_str_to_printing_untyped

    def get_full_name_from_id(self, card_id: str) -> str:
        if card_id not in self.id_to_api_card:
            raise ValueError(f"Card ID {card_id} not found in API data")
        api_card:ApiCard = self.id_to_api_card[card_id]
        return api_card.full_name

    def get_full_name(self, card_untyped) -> str:
        if 'version' in card_untyped:
            full_name: str = f"{card_untyped['name']} - {card_untyped['version']}"
            return full_name
        return card_untyped['name']

    def api_card_from(self, printing_untyped) -> ApiCard:
        full_name:str = str(self.get_full_name(printing_untyped))
        printing: CardPrinting = self.printing_from_printing_untyped(printing_untyped)
        return ApiCard(
            full_name=full_name,    
            cost=printing_untyped['cost'], 
            color=printing_untyped['ink'],
            inks=printing_untyped['inks'],
            types=printing_untyped['type'],
            card_printings=[printing],
            default_printing=printing
        )

    def printing_from_printing_untyped(self, printing_untyped) -> CardPrinting:
        return CardPrinting(
            full_name=printing_untyped['name'],
            collector_id=printing_untyped['collector_number'],
            set_code=printing_untyped['set']['code'],
            rarity=lorcast_to_dtd_rarity[printing_untyped['rarity']]
        )

    def is_alternate_art(self, collector_number: str) -> bool:
        return self.is_number(collector_number) and int(collector_number) > 204

    def is_number(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False
        
    def is_core_printing(self, printing: CardPrinting) -> bool:
        return self.is_core_set(printing.set_code) and not self.is_alternate_art(printing.collector_id)

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

    def read_or_fetch_id_to_api_card(self) -> dict[str, ApiCard]:
        return self.id_to_api_card

    def init(self):
        cached_api_data_file = Path(CACHED_API_DATA_FILEPATH)
        if not cached_api_data_file.is_file():
            printing_id_to_printing_untyped = self.fetch_api_data()
            print("Fetching set Q1 cards from local file...")
            printing_id_to_printing_untyped_q1 = self.fetch_set_q1_data()
            printing_id_to_printing_untyped.update(printing_id_to_printing_untyped_q1) # merge the two dicts
            # self.fix_card_names(name_to_card_untyped)
            Path(cached_api_data_file).parent.mkdir(parents=True, exist_ok=True)
            with cached_api_data_file.open(mode='w') as file_to_write:
                json.dump(printing_id_to_printing_untyped, file_to_write)

        with cached_api_data_file.open(mode='r') as file_to_read:
            printing_id_str_to_printing_untyped = json.load(file_to_read)
            id_to_api_card = self.generate_id_to_api_card(printing_id_str_to_printing_untyped)
        self.id_to_api_card = id_to_api_card

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

    # def fix_card_names(self, name_to_card_untyped):
    #     # there are typos in the https://api.lorcana-api.com card names.  We have to fix those or we cannot translate between data sources
    #     print("Fixing card names")

lorcast_api: LorcastApi = LorcastApi()
lorcast_api.init()