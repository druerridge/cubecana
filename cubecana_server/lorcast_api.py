from pathlib import Path
import json
from . import id_helper
import requests
from .card import ApiCard

CACHED_API_DATA_FILEPATH = 'inputs/lorcast_api_cache/lorcast_api_data_cache.json'
CACHED_API_DATA_SET_Q1_FILEPATH = 'inputs/lorcast_api_cache/lorcast_api_data_cache_q1.json'

lorcast_to_dtd_rarity =  {
    "Common" : "Common",
    "Uncommon" : "Uncommon",
    "Rare" : "Rare",
    "Super_rare" : "Super Rare",
    "Legendary" : "Legendary" 
}

class LorcastApi:
    def __init__(self):
        self.id_to_api_card: dict[str, ApiCard] = {}

    def is_number(self,code):
        try:
            int(code)
            return True
        except ValueError:
            return False

    def fetch_api_data(self) -> dict[str, dict]:
        name_to_card = {}
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
        # iterate sets
        for set in sets_results:
            code = set['code']
            if not self.is_number(code):
                continue
            url = f'https://api.lorcast.com/v0/sets/{code}/cards'
            print(f'Fetching {url}...')
            res = requests.get(url=url)
            cards_in_set = res.json()
            # iterate cards
            for card in cards_in_set:
                full_name = self.get_full_name(card)
                if card['rarity'] == 'Enchanted':
                    continue
                if self.is_number(card['collector_number']) and int(card['collector_number']) > 204:
                    continue
                name_to_card[full_name] = card
        return name_to_card

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

    def api_card_from(self, card_untyped) -> ApiCard:
        full_name:str = str(self.get_full_name(card_untyped))
        return ApiCard(
                    full_name=full_name,    
                    cost=card_untyped['cost'], 
                    rarity=lorcast_to_dtd_rarity[card_untyped['rarity']], 
                    color=card_untyped['ink'],
                    inks=card_untyped['inks'],
                    types=card_untyped['type'],
                    set_num=card_untyped['set']['code'])

    def generate_id_to_card_untyped(self, name_to_card) -> dict[str, ApiCard]:
        id_to_card_untyped: dict[str, dict] = {}
        for card_name in name_to_card:
            card = name_to_card[card_name]
            id_to_card_untyped[id_helper.to_id(card_name)] = card
        return id_to_card_untyped

    def generate_id_to_api_card(self, id_to_card_untyped) -> dict[str, ApiCard]:
        id_to_api_card: dict[str, ApiCard] = {}
        for card_id in id_to_card_untyped:
            card_untyped = id_to_card_untyped[card_id]
            id_to_api_card[card_id] = self.api_card_from(card_untyped)
        return id_to_api_card

    def fetch_set_q1_data(self) -> dict[str, dict]:
        id_to_card_untyped = {}
        cached_set_q1_api_data_file = Path(CACHED_API_DATA_SET_Q1_FILEPATH)
        with cached_set_q1_api_data_file.open(mode='r') as file_to_read:
            id_to_card_untyped = json.load(file_to_read)    
        return id_to_card_untyped

    def read_or_fetch_id_to_api_card(self) -> dict[str, ApiCard]:
        return self.id_to_api_card

    def init(self):
        cached_api_data_file = Path(CACHED_API_DATA_FILEPATH)
        if not cached_api_data_file.is_file():
            name_to_card_untyped = self.fetch_api_data()
            print("Fetching set Q1 cards from local file...")
            name_to_card_untyped_set_q1 = self.fetch_set_q1_data()
            name_to_card_untyped.update(name_to_card_untyped_set_q1) # merge the two dicts
            self.fix_card_names(name_to_card_untyped)
            id_to_card_untyped = self.generate_id_to_card_untyped(name_to_card_untyped)
            Path(cached_api_data_file).parent.mkdir(parents=True, exist_ok=True)
            with cached_api_data_file.open(mode='w') as file_to_write:
                json.dump(id_to_card_untyped, file_to_write)

        with cached_api_data_file.open(mode='r') as file_to_read:
            id_to_card_untyped = json.load(file_to_read)
            id_to_api_card = self.generate_id_to_api_card(id_to_card_untyped)
        self.id_to_api_card = id_to_api_card

    def fix_card_name(self, name_to_card, old_full_name, new_full_name):
        if old_full_name not in name_to_card:
            return
        name_to_card[new_full_name] = name_to_card[old_full_name]
        splits = new_full_name.split(' - ')
        new_name = splits[0]
        name_to_card[new_full_name]['name'] = new_name
        if len(splits) > 1:
            new_version = splits[1]
            name_to_card[new_full_name]['version'] = new_version
        del name_to_card[old_full_name]    

    def fix_card_names(self, name_to_card_untyped):
        # there are typos in the https://api.lorcana-api.com card names.  We have to fix those or we cannot translate between data sources
        print("Fixing card names")

lorcast_api: LorcastApi = LorcastApi()
lorcast_api.init()