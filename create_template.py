"""
This is a python script to create a template to convert a dreamborn.ink Tabletop Simulator export into a Draftmancer Custom Card List.

Run the script like so:
python3 create_template.py '/path/to/dreamborn_tabletop_sim_export.json'

TODOs:
- How to balance packs versus random 12 cards?

Notes:
- https://draftmancer.com/cubeformat.html
"""
from collections import defaultdict
import json
from pathlib import Path
import csv
from lcc_error import LccError, UnidentifiedCardError
from settings import Settings
from lorcana_api import ApiCard
import lorcast_api as lorcana_api
import id_helper

DEFAULT_CARD_EVALUATIONS_FILE = "DraftBots/FrankKarstenEvaluations-HighPower.csv"

def get_mainboard_lines(all_lines):
  try: 
    empty_index = all_lines.index("")
    return all_lines[:empty_index]
  except ValueError:
    try:
        empty_index = all_lines.index("\n")
        return all_lines[:empty_index]
    except ValueError:
        return all_lines

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
            id = id_helper.to_id(json_obj['ContainedObjects'][i - 1]['Nickname'])
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

# def read_id_to_dreamborn_name():
#     with open('all_dreamborn_names.txt', encoding='utf8') as f:
#         lines = f.readlines()
#     id_to_dreamborn_name = {}
#     for l in lines:
#         name = l.strip()
#         id_to_dreamborn_name[id_helper.to_id(name)] = name
#     return id_to_dreamborn_name

def read_id_to_dreamborn_name():
    with open('all_dreamborn_names.txt', encoding='utf8') as f:
        lines = f.readlines()
    id_to_dreamborn_name = {}
    for l in lines:
        name = l.strip()
        id_to_dreamborn_name[id_helper.to_id(name)] = name
    return id_to_dreamborn_name

lorcana_color_to_draftmancer_color =  {
    "Amber": "W",
    "Amethyst": "B",
    "Emerald": "G",
    "Ruby": "R",
    "Steel": "",
    "Sapphire": "U"
}
def to_draftmancer_color(lorcana_color, settings: Settings):
    if settings.set_card_colors:
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

# def generate_custom_card_list_non_tts(id_to_api_card, id_to_rating, id_to_count, id_to_dreamborn_name, settings):
#     custom_card_list = []
#     for id in id_to_count:
#         card = id_to_card[id]
#         ink_cost = card['Cost']
#         cannonical_name = canonical_name_from_id(id, id_to_dreamborn_name, None) # only accept cannonical names
#         custom_card = {
#             'name': cannonical_name, 
#             'mana_cost': f'{{{ink_cost}}}',
#             'type': 'Instant',
#             'image_uris': {
#                 'en': id_to_tts_card[id]['image_uri']
#             },
#             'rating': name_to_rating[id],
#             'rarity': to_draftmancer_rarity(card['Rarity']),
#         }
#         if (settings.set_card_colors):
#             custom_card['colors'] = [to_draftmancer_color(card['Color'])]
#         custom_card_list.append(custom_card)
#     return custom_card_list

def generate_custom_card_list(id_to_api_card: dict[str, ApiCard], 
                              id_to_rating: dict[str, int],
                              id_to_tts_card: dict[str, dict], 
                              id_to_dreamborn_name: dict[str, str], 
                              settings: Settings):
    custom_card_list = []
    print(len(id_to_api_card.keys()))
    for id in id_to_tts_card:
        api_card: ApiCard = id_to_api_card[id]
        ink_cost = api_card.cost
        cannonical_name = id_helper.canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card)
        custom_card = {
            'name': cannonical_name, 
            'mana_cost': f'{{{ink_cost}}}',
            'type': 'Instant',
            'image_uris': {
                'en': id_to_tts_card[id]['image_uri']
            },
            'rarity': to_draftmancer_rarity(api_card.rarity),
        }
        if id in id_to_rating:
            custom_card['rating'] = id_to_rating[id]
        else:
            print(f"Missing rating for {cannonical_name}")
            # TODO: probably tell user rating is missing
        
        if (settings.set_card_colors):
            custom_card['colors'] = [to_draftmancer_color(api_card.color, settings)]
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
            id_to_rating[id_helper.to_id(row['Card Name'])] = int(row['Rating - Draftmancer'])
    return id_to_rating

def write_draftmancer_file(draftmancer_file_string, card_list_name):
    draftmancer_file_as_lines = draftmancer_file_string.split('\n')
    file_name = f'{card_list_name}.draftmancer.txt'
    with open(file_name, 'w', encoding="utf-8") as file:
        for line in draftmancer_file_as_lines:
            file.write(line + '\n')
    print(f'Wrote draftmancer file to {file_name}')

def generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings, slot_name_to_slot=None):
    draftmancer_settings = settings.to_draftmancer_settings()
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
        ]
    if slot_name_to_slot==None:
        lines.append(f'[MainSlot({settings.cards_per_booster})]')
        for id in id_to_tts_card:
            cannonical_name = id_helper.canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card)
            line_str = f"{id_to_tts_card[id]['count']} {cannonical_name}"
            lines.append(line_str)
    else:
        for slot_name in slot_name_to_slot:
            slot = slot_name_to_slot[slot_name]
            lines.append(f'[{slot_name}({slot.num_cards})]')
            for slot_card in slot.slot_cards:
                cannonical_name = id_helper.canonical_name_from_id(slot_card.card_id, id_to_dreamborn_name, id_to_tts_card)
                line_str = f"{slot_card.num_copies} {cannonical_name}"
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
            try:
                input_name = custom_card['name']
                id = id_helper.to_id(input_name)
                id_to_custom_card[id] = custom_card
            except KeyError:
                raise UnidentifiedCardError(f"Unable to identify card with input name {input_name} and id {id} ")
        return id_to_custom_card
    return None

def read_draftmancer_export(draftmancer_deck_export_file):
    with open(draftmancer_deck_export_file, encoding='utf8') as file:
        lines = file.readlines()
        mainboard_lines = get_mainboard_lines(lines)
        return id_to_count_from(mainboard_lines)

def id_to_count_from(lines):
    id_to_count = defaultdict(int)
    for line in lines:
        string_count, name = line.rstrip().split(' ', 1)
        try:
            int_count = int(string_count)
            id_to_count[id_helper.to_id(name)] += int_count
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
        print("wrote tts deck to: " + TTS_OUTPUT_PATH)

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
            try:
                contained_obj = generate_contained_obj(id_to_custom_card[id]['name'], current_card_index, previous_card_index)
                card_image_url = id_to_custom_card[id]['image_uris']['en']
                custom_deck_obj = generate_custom_deck_obj(card_image_url)
                contained_obj_list.append(contained_obj)
                deck_ids.append(contained_obj['CardID'])
                custom_deck[str(current_card_index)] = custom_deck_obj
                previous_card_index = current_card_index
                current_card_index += 1
            except KeyError:
                raise UnidentifiedCardError(f"Unable to identify card with id {id} ")
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

def dreamborn_tts_to_draftmancer_from_file(dreamborn_export_for_tabletop_sim, card_evaluations_file, settings):
    id_to_tts_card = read_id_to_tts_card_from_filesystem(dreamborn_export_for_tabletop_sim)
    return dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings)

def dreamborn_card_list_to_draftmancer(card_list_input, card_evaluations_file, settings):
    card_list_lines = card_list_input.split('\n')
    id_to_count_input = id_to_count_from(card_list_lines)
    return add_card_list_to_draftmancer_custom_cards(id_to_count_input, "incomplete_simple_template.draftmancer.txt", settings)

def add_card_list_to_draftmancer_custom_cards(id_to_count_input, draftmancer_custom_card_file, settings):
    file_contents = ""
    with open(draftmancer_custom_card_file, encoding='utf8') as file:
        file_contents = ''.join(file.readlines())
    id_to_custom_card = read_draftmancer_custom_cardlist(draftmancer_custom_card_file)
    draftmancer_settings = settings.to_draftmancer_settings()

    lines = [
            '\n[Settings]',
            json.dumps(
                draftmancer_settings,
                indent=4
            ),
            f'[MainSlot({settings.cards_per_booster})]',
        ]
    file_contents += '\n'.join(lines)
    for id in id_to_count_input:
        try:
            canonical_name = id_to_custom_card[id]['name']
            file_contents += f"\n{id_to_count_input[id]} {canonical_name}"
        except KeyError:
            raise UnidentifiedCardError(f"Unable to identify card with id {id} ")
    return file_contents

def dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings):
    id_to_dreamborn_name = read_id_to_dreamborn_name()
    id_to_api_card = lorcana_api.read_or_fetch_id_to_api_card()
    id_to_rating = read_id_to_rating(card_evaluations_file)
    custom_card_list = generate_custom_card_list(id_to_api_card, id_to_rating, id_to_tts_card, id_to_dreamborn_name, settings)
    return generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings)
