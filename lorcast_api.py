from pathlib import Path
import json
import id_helper
import requests

CACHED_API_DATA_FILEPATH = 'lorcast_api_data_cache.json'

class ApiCard:
    def __init__(self, cost, rarity, color, inks, types: list[str]):
        self.cost = cost
        self.rarity = rarity
        self.color = color
        self.inks = inks
        self.types = types

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)

lorcast_to_dtd_rarity =  {
    "Common" : "Common",
    "Uncommon" : "Uncommon",
    "Rare" : "Rare",
    "Super_rare" : "Super Rare",
    "Legendary" : "Legendary" 
}

def is_number(code):
    try:
        int(code)
        return True
    except ValueError:
        return False

def fetch_api_data():
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
        if not is_number(code):
            continue
        url = f'https://api.lorcast.com/v0/sets/{code}/cards'
        print(f'Fetching {url}...')
        res = requests.get(url=url)
        cards_in_set = res.json()
        # iterate cards
        for card in cards_in_set:
            full_name = get_full_name(card)
            if card['rarity'] == 'Enchanted':
                continue
            if is_number(card['collector_number']) and int(card['collector_number']) > 204:
                continue
            name_to_card[full_name] = card
    return name_to_card

def get_full_name(card):
    if 'version' in card:
        full_name = f"{card['name']} - {card['version']}"
        return full_name
    return card['name']

def api_card_from(card):
    return ApiCard(card['cost'], 
                   lorcast_to_dtd_rarity[card['rarity']], 
                   card['ink'],
                   card['inks'],
                   card['type'])

def generate_id_to_card_untyped(name_to_card) -> dict[str, ApiCard]:
    id_to_card_untyped: dict[str, dict] = {}
    for card_name in name_to_card:
        card = name_to_card[card_name]
        id_to_card_untyped[id_helper.to_id(card_name)] = card
    return id_to_card_untyped

def generate_id_to_api_card(name_to_card) -> dict[str, ApiCard]:
    id_to_api_card: dict[str, ApiCard] = {}
    for card_name in name_to_card:
        card = name_to_card[card_name]
        id_to_api_card[id_helper.to_id(card_name)] = api_card_from(card)
    return id_to_api_card

def read_or_fetch_id_to_api_card() -> dict[str, ApiCard]:
    cached_api_data_file = Path(CACHED_API_DATA_FILEPATH)
    if not cached_api_data_file.is_file():
        name_to_card_untyped = fetch_api_data()
        fix_card_names(name_to_card_untyped)
        id_to_card_untyped = generate_id_to_card_untyped(name_to_card_untyped)
        with cached_api_data_file.open(mode='w') as file_to_write:
            json.dump(id_to_card_untyped, file_to_write)

    with cached_api_data_file.open(mode='r') as file_to_read:
        id_to_card_untyped = json.load(file_to_read)
        id_to_api_card = generate_id_to_api_card(id_to_card_untyped)
    return id_to_api_card

def fix_card_name(name_to_card, old_full_name, new_full_name):
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

def fix_card_names(name_to_card_untyped):
    # there are typos in the https://api.lorcana-api.com card names.  We have to fix those or we cannot translate between data sources
    print("Fixing card names")