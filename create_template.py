"""
This is a python script to create a template to convert a dreamborn.ink Tabletop Simulator export into a Draftmancer Custom Card List.

Run the script like so:
python3 create_template.py '/path/to/dreamborn_tabletop_sim_export.json'

TODOs:
- How to balance packs versus random 12 cards?

Notes:
- https://draftmancer.com/cubeformat.html
"""
import requests
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import csv
from lcc_error import LccError, UnidentifiedCardError

CACHED_API_DATA_FILEPATH = 'api_data_cache.json'
DEFAULT_CARD_EVALUATIONS_FILE = "DraftBots\\FrankKarstenEvaluations-HighPower.csv"

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='given a dreamborn \"deck\" of a cube / set / card list, exported in Tabletop Simulator format, create a draftmancer custom card list that can be uploaded and drafted on draftmancer.com',
                    epilog='Text at the bottom of help')

parser.add_argument('dreamborn_export_for_tabletop_sim', help="file path to a .deck export in Tabletop Sim format from dreamborn.ink deck of the cube e.g. example-cube.json or C:\\Users\\dru\\Desktop\\deck.json")
parser.add_argument('--card_evaluations_file', default=DEFAULT_CARD_EVALUATIONS_FILE, help="relative path to a .csv file containing card name -> 0-5 card rating (power in a vacuum). default: \"DraftBots\\\\FrankKarstenEvaluations-HighPower.csv\"")
parser.add_argument('--boosters_per_player', default=4)
parser.add_argument('--cards_per_booster', default=12)
parser.add_argument('--name', default="custom_card_list", help="Sets name of both the output file and the set/cube list as it appears in draftmancer")
parser.add_argument('--set_card_colors', default=False, help="WARNING** This sets card colors, allowing draftmancer to do color-balancing for you, but it will also encourage bots to draft 1-2 color decks")
parser.add_argument('--color_balance_packs', default=False, help="WARNING** this color-balances ONLY your largest slot, IF it contains enough cards, AND steel may be wonky (treated as colorless). This will ONLY work if card_colors is true, which will encourage bots to draft 1-2 color decks")
# parser.add_argument('--draftmancer_card_list', default=False, help="card list to use for deck conversion to tts")
parser.add_argument('--draftmancer_deck_export', default=False, help="deck export to convert to tts")

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

def generate_id_to_card(name_to_card):
    return {to_id(card_name) : name_to_card[card_name] for card_name in name_to_card}

def read_or_fetch_id_to_api_card():
    cached_api_data_file = Path(CACHED_API_DATA_FILEPATH)
    if cached_api_data_file.is_file():
        with cached_api_data_file.open() as f:
            id_to_card = json.load(f)
    else:
        name_to_card = fetch_api_data()
        fix_card_names(name_to_card)
        id_to_card = generate_id_to_card(name_to_card)
        with cached_api_data_file.open(mode='w') as f:
            json.dump(id_to_card, f)
    return id_to_card

def generate_id_to_tts_card_from_file(file, id_to_tts_card=None):
    with file.open(encoding='utf8') as file:
        data = json.load(file)
    return generate_id_to_tts_card_from_json_obj(data, id_to_tts_card)

def generate_id_to_tts_card_from_json_obj(json_obj, id_to_tts_card=None):
    json_obj = json_obj['ObjectStates'][0]
    if id_to_tts_card == None:
        id_to_tts_card = defaultdict(lambda: {'count': 0})
    i = 1
    while True:
        try:
            id = to_id(json_obj['ContainedObjects'][i - 1]['Nickname'])
        except IndexError:
            break
        id_to_tts_card[id]['count'] += 1
        id_to_tts_card[id]['name'] = json_obj['ContainedObjects'][i - 1]['Nickname']
        id_to_tts_card[id]['image_uri'] = json_obj['CustomDeck'][str(i)]['FaceURL']
        i += 1
    return id_to_tts_card

def read_id_to_tts_card_from_filesystem(dreamborn_tts_export_filepath):
    dreamborn_tts_export_path = Path(dreamborn_tts_export_filepath)
    id_to_tts_card = None
    if dreamborn_tts_export_path.is_dir():
        files = dreamborn_tts_export_path.glob('*')
        for file in files:
            if file.is_file():
                print(file)
                id_to_tts_card = generate_id_to_tts_card_from_file(file, id_to_tts_card)
    else:
        id_to_tts_card = generate_id_to_tts_card_from_file(dreamborn_tts_export_path, id_to_tts_card)
    return id_to_tts_card

pattern = re.compile(r"[\W_]+", re.ASCII)
def to_id(string):
    string = string.replace('ā', 'a')
    string = string.replace('é','e')
    return re.sub(pattern, '', string).lower()

def fix_card_name(name_to_card, old_name, new_name):
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

def canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card):
    # IMPORTANT dreamborn names are canonical to enable import / export to / from dreamborn.ink (which subsequently enables deck export to inktable.net + Tabletop Simulator)
    # dreamborn plain export is the best name for our custom card list, enabling all import / export and hand-editing of the card list (e.g. simple_template.draftmancer.txt)
    # UPDATE INSTRUCTIONS: dreamborn.ink > Collection > export > copy-paste the "Name" column w/o the header row
    cannonical_name = id_to_dreamborn_name.get(id, None) 
    
    # dreamborn TTS export is the second best name
    # this enables us to generate cubes with cards we haven't exported yet in all_dreamborn_names.txt, and import / export from dreamborn
    # HOWEVER, hand-editing the booster slot(s) after generation has edge cases, e.g. card names are missing apostrophes (') in custom card list, so they won't match
    # therefore this method is not suitable to generate simple_template.draftmancer.txt which is meant to have the booster slot(s) "hand-edited"
    if cannonical_name is None: 
        cannonical_name = id_to_tts_card[id]['name']
    return cannonical_name

def read_id_to_dreamborn_name():
    with open('all_dreamborn_names.txt', encoding='utf8') as f:
        lines = f.readlines()
    id_to_dreamborn_name = {}
    for l in lines:
        name = l.strip()
        id_to_dreamborn_name[to_id(name)] = name
    return id_to_dreamborn_name

lorcana_color_to_draftmancer_color =  {
    "Amber": "W",
    "Amethyst": "B",
    "Emerald": "G",
    "Ruby": "R",
    "Steel": "",
    "Sapphire": "U"
}
def to_draftmancer_color(lorcana_color):
    if set_card_colors:
        return lorcana_color_to_draftmancer_color[lorcana_color]
    else:
        return ""

lorcana_rarity_to_draftmancer_rarity =  {
    "Common": "common",
    "Uncommon": "uncommon",
    "Rare": "rare",
    "Super Rare": "mythic",
    "Legendary": "mythic"
}
def to_draftmancer_rarity(lorcana_rarity):
    return lorcana_rarity_to_draftmancer_rarity[lorcana_rarity]

def generate_custom_card_list_non_tts(id_to_api_card, id_to_rating, id_to_count, id_to_dreamborn_name):
    custom_card_list = []
    for id in id_to_count:
        card = id_to_card[id]
        ink_cost = card['Cost']
        cannonical_name = canonical_name_from_id(id, id_to_dreamborn_name, None) # only accept cannonical names
        custom_card = {
            'name': cannonical_name, 
            'mana_cost': f'{{{ink_cost}}}',
            'type': 'Instant',
            'image_uris': {
                'en': id_to_tts_card[id]['image_uri']
            },
            'rating': name_to_rating[id],
            'rarity': to_draftmancer_rarity(card['Rarity']),
        }
        if (set_card_colors):
            custom_card['colors'] = [to_draftmancer_color(card['Color'])]
        custom_card_list.append(custom_card)
    return custom_card_list

def generate_custom_card_list(id_to_card, name_to_rating, id_to_tts_card, id_to_dreamborn_name):
    custom_card_list = []
    for id in id_to_tts_card:
        card = id_to_card[id]
        ink_cost = card['Cost']
        cannonical_name = canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card)
        custom_card = {
            'name': cannonical_name, 
            'mana_cost': f'{{{ink_cost}}}',
            'type': 'Instant',
            'image_uris': {
                'en': id_to_tts_card[id]['image_uri']
            },
            'rating': name_to_rating[id],
            'rarity': to_draftmancer_rarity(card['Rarity']),
        }
        if (set_card_colors):
            custom_card['colors'] = [to_draftmancer_color(card['Color'])]
        custom_card_list.append(custom_card)
    return custom_card_list

def read_id_to_rating(card_evaluations_file):
    id_to_rating = {}
    with open(file=card_evaluations_file, newline='', encoding='utf8') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        dialect.quoting = csv.QUOTE_MINIMAL
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            id_to_rating[to_id(row['Card Name'])] = int(row['Rating - Draftmancer'])
    return id_to_rating

def write_draftmancer_file(draftmancer_file_string, card_list_name):
    draftmancer_file_as_lines = draftmancer_file_string.split('\n')
    file_name = f'{card_list_name}.draftmancer.txt'
    with open(file_name, 'w', encoding="utf-8") as file:
        for line in draftmancer_file_as_lines:
            file.write(line + '\n')

def generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings):
    draftmancer_settings = {
        'boostersPerPlayer': settings.boosters_per_player,
        'name': settings.card_list_name,
        'cardBack': 'https://wiki.mushureport.com/images/thumb/d/d7/Card_Back_official.png/450px-Card_Back_official.png'
    }
    if settings.color_balance_packs == True:
        draftmancer_settings['colorBalance'] = True
            
    lines = [
            '[CustomCards]',
            json.dumps(custom_card_list, indent=4),
            '[Settings]',
            json.dumps(
                draftmancer_settings,
                indent=4
            ),
            f'[MainSlot({settings.cards_per_booster})]',
        ]
    for id in id_to_tts_card:
        cannonical_name = canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card)
        line_str = f"{id_to_tts_card[id]['count']} {cannonical_name}"
        lines.append(line_str)
    return '\n'.join(lines)

def read_draftmancer_custom_cardlist(file_path='all_cards_cube.draftmancer.txt'):
    with open(file_path, encoding='utf8') as f:
        # custom_card_string = "{\"CustomCards\":"
        custom_card_string = ""
        read_custom_cards = False
        for line in f:
            if "[Settings]" in line:
                # custom_card_string += "}"
                read_custom_cards = False
                break

            if read_custom_cards:
                custom_card_string += line.strip()

            if "[CustomCards]" in line:
                read_custom_cards = True
        custom_cards_json = json.loads(custom_card_string)
        
        id_to_custom_card = {}
        for custom_card in custom_cards_json:
            id_to_custom_card[to_id(custom_card['name'])] = custom_card
        return id_to_custom_card
    return None

def read_draftmancer_export(draftmancer_deck_export_file):
    with open(draftmancer_deck_export_file, encoding='utf8') as file:
        lines = file.readlines()
    return id_to_count_from(lines)

def id_to_count_from(lines):
    id_to_count = defaultdict(int)
    for line in lines:
        string_count, name = line.rstrip().split(' ', 1)
        try:
            int_count = int(string_count)
            id_to_count[to_id(name)] += int_count
        except ValueError:
            raise LccError("Missing count or name in line:\n " + line + "\nShould look like:\n1 Elsa - Snow Queen", 400)
    return id_to_count

TTS_SCALE_X = 1.2
TTS_SCALE_Y = 1
TTS_SCALE_Z = 1.2
TTS_OUTPUT_PATH = "tts_deck.json"

def write_tts_deck_file(tts_deck):
    with open(TTS_OUTPUT_PATH, "w") as file:
        json.dump(tts_deck, file)

def generate_contained_obj(card_name, current_card_index, previous_card_index):
    card_id = '{cur}{prev:02d}'.format(cur=current_card_index, prev=previous_card_index)
    return {
        'CardID': card_id,
        'Name': "Card",
        'Nickname': card_name,
        'Transform': {
            'posX': 0,
            'posY': 0,
            'posZ': 0,
            'rotX': 0,
            'rotY': 180,
            'rotZ': 180,
            'scaleX': TTS_SCALE_X,
            'scaleY': TTS_SCALE_Y,
            'scaleZ': TTS_SCALE_Z
        }
    }

def generate_custom_deck_obj(card_image_url):
    return {
        'FaceURL': card_image_url,
        'BackURL': "https://steamusercontent-a.akamaihd.net/ugc/2073388328677586509/478B51BE25275FD0AC2CFC48828F9FD7B9864526/",
        'NumHeight': 1,
        'NumWidth': 1,
        'BackIsHidden': True
    }

def generate_tts_deck(id_to_count, id_to_custom_card):
    previous_card_index = 0
    current_card_index = 1
    contained_obj_list = []
    deck_ids = []
    custom_deck = {}
    for id, count in id_to_count.items():
        for i in range(0, count):
            contained_obj = generate_contained_obj(id_to_custom_card[id]['name'], current_card_index, previous_card_index)
            card_image_url = id_to_custom_card[id]['image_uris']['en']
            custom_deck_obj = generate_custom_deck_obj(card_image_url)
            contained_obj_list.append(contained_obj)
            deck_ids.append(contained_obj['CardID'])
            custom_deck[str(current_card_index)] = custom_deck_obj
            previous_card_index = current_card_index
            current_card_index += 1
    return {
        'ObjectStates': [
            {
                'Name': "DeckCustom",
                'ContainedObjects': contained_obj_list,
                'DeckIDs': deck_ids,
                'CustomDeck': custom_deck,
                'Transform': {
                    'posX': 0,
                    'posY': 1,
                    'posZ': 0,
                    'rotX': 0,
                    'rotY': 180,
                    'rotZ': 180,
                    'scaleX': TTS_SCALE_X,
                    'scaleY': TTS_SCALE_Y,
                    'scaleZ': TTS_SCALE_Z
                }
            }
        ]
    }

card_evaluations_file = None
boosters_per_player = None
cards_per_booster = None
card_list_name = None
set_card_colors = False
color_balance_packs = False

def dreamborn_tts_to_draftmancer_from_file(dreamborn_export_for_tabletop_sim, card_evaluations_file, settings):
    id_to_tts_card = read_id_to_tts_card_from_filesystem(dreamborn_export_for_tabletop_sim)
    return dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings)

def dreamborn_card_list_to_draftmancer(card_list_input, card_evaluations_file, settings):
    card_list_lines = card_list_input.split('\n')
    id_to_count_input = id_to_count_from(card_list_lines)
    return add_card_list_to_draftmancer_custom_cards(id_to_count_input, "simple_template.draftmancer.txt")

def add_card_list_to_draftmancer_custom_cards(id_to_count_input, draftmancer_custom_card_file):
    file_contents = ""
    with open(draftmancer_custom_card_file, encoding='utf8') as file:
        file_contents = '\n'.join(file.readlines())
    id_to_custom_card = read_draftmancer_custom_cardlist(draftmancer_custom_card_file)
    for id in id_to_count_input:
        try:
            canonical_name = id_to_custom_card[id]['name']
            file_contents += f"\n{id_to_count_input[id]} {canonical_name}"
        except KeyError:
            raise UnidentifiedCardError(f"Unable to identify card with id {id} ")
    return file_contents

def dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings):
    id_to_dreamborn_name = read_id_to_dreamborn_name()
    id_to_api_card = read_or_fetch_id_to_api_card()
    id_to_rating = read_id_to_rating(card_evaluations_file)
    custom_card_list = generate_custom_card_list(id_to_api_card, id_to_rating, id_to_tts_card, id_to_dreamborn_name)
    return generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings)

class Settings:
    def __init__(self, boosters_per_player, card_list_name, cards_per_booster, set_card_colors, color_balance_packs):
        self.boosters_per_player = int(boosters_per_player)
        self.card_list_name = card_list_name
        self.cards_per_booster = int(cards_per_booster)
        self.set_card_colors = bool(set_card_colors)
        self.color_balance_packs = bool(color_balance_packs)

if __name__ == '__main__':
    # parse CLI arguments
    args = parser.parse_args()
    card_evaluations_file = args.card_evaluations_file

    settings = Settings(
        args.boosters_per_player,
        args.name,
        args.cards_per_booster,
        args.set_card_colors,
        args.color_balance_packs
    )

    if args.draftmancer_deck_export:
        id_to_custom_card = read_draftmancer_custom_cardlist()
        id_to_count = read_draftmancer_export(args.draftmancer_deck_export)
        tts_deck = generate_tts_deck(id_to_count, id_to_custom_card)
        write_tts_deck_file(tts_deck)
        print("wrote tts deck to: " + TTS_OUTPUT_PATH)
    else:
        draftmancer_file_string = dreamborn_tts_to_draftmancer_from_file(args.dreamborn_export_for_tabletop_sim, card_evaluations_file, settings)
        write_draftmancer_file(draftmancer_file_string, args.name)