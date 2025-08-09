from pathlib import Path
import json
from . import id_helper
import requests

CACHED_API_DATA_FILEPATH = 'api_data_cache.json'

class ApiCard:
    def __init__(self, cost, rarity, color):
        self.cost = cost
        self.rarity = rarity
        self.color = color

def fetch_api_data():
    name_to_card = {}
    page = 1
    while True:
        url = f'https://api.lorcana-api.com/cards/all?page={page}'
        print(f'Fetching {url}...')
        res = requests.get(url)
        data = res.json()
        if len(data) == 0:
            break
        for card in data:
            name_to_card[card['Name']] = card
        page += 1
    return name_to_card

def api_card_from(card):
    return ApiCard(card['Cost'], 
                   card['Rarity'], 
                   card['Color'])

def generate_id_to_card(name_to_card) -> dict[str, ApiCard]:
    return {id_helper.to_id(card_name) : api_card_from(name_to_card[card_name]) for card_name in name_to_card}

def read_or_fetch_id_to_api_card() -> dict[str, ApiCard]:
    cached_api_data_file = Path(CACHED_API_DATA_FILEPATH)
    if cached_api_data_file.is_file():
        with cached_api_data_file.open() as f:
            id_to_card_untyped = json.load(f)
            id_to_api_card = generate_id_to_card(id_to_card_untyped)
    else:
        name_to_card = fetch_api_data()
        fix_card_names(name_to_card)
        id_to_api_card = generate_id_to_card(name_to_card)
        with cached_api_data_file.open(mode='w') as f:
            json.dump(id_to_api_card, f)
    return id_to_api_card

def fix_card_name(name_to_card, old_name, new_name):
    if old_name not in name_to_card:
        return
    name_to_card[new_name] = name_to_card[old_name]
    name_to_card[new_name]['Name'] = new_name
    del name_to_card[old_name]    

def fix_card_names(name_to_card):
    # there are typos in the https://api.lorcana-api.com card names.  We have to fix those or we cannot translate between data sources
    fix_card_name(name_to_card, 'Benja - Bold United', 'Benja - Bold Uniter')
    fix_card_name(name_to_card, 'Kristoff - Offical Ice Master', 'Kristoff - Official Ice Master')
    fix_card_name(name_to_card, 'Snowanna Rainbeau', 'Snowanna Rainbeau - Cool Competitor')
    fix_card_name(name_to_card, 'Vannelope Von Schweetz - Random Roster Racer', 'Vanellope von Schweetz - Random Roster Racer')
    fix_card_name(name_to_card, 'Snow White - Fair-haired', 'Snow White - Fair-Hearted')
    fix_card_name(name_to_card, 'Merlin\'s Cottage', 'Merlin\'s Cottage - The Wizard\'s Home')
    fix_card_name(name_to_card, 'Arthur - King Victorius', 'Arthur - King Victorious')
    fix_card_name(name_to_card, 'Seven Dwarfs\' Mine', 'Seven Dwarfs\' Mine - Secure Fortress')