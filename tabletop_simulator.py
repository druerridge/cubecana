import json
from pathlib import Path
import id_helper
from collections import defaultdict
from lorcast_api import ApiCard
from lcc_error import UnidentifiedCardError

TTS_SCALE_X = 1.2
TTS_SCALE_Y = 1
TTS_SCALE_Z = 1.2
TTS_OUTPUT_PATH = "tts_deck.json"

def generate_id_to_tts_card_from_json_obj(json_obj, id_to_tts_card=None, id_to_count_filter:dict[str, ApiCard] = None):
    json_obj = json_obj['ObjectStates'][0]
    if id_to_tts_card == None:
        id_to_tts_card = defaultdict(lambda: {'count': 0})
    i = 1
    while True:
        try:
            id = id_helper.to_id(json_obj['ContainedObjects'][i - 1]['Nickname'])
        except IndexError:
            break
        if (not id_to_count_filter):
            id_to_tts_card[id]['count'] += 1
            id_to_tts_card[id]['name'] = json_obj['ContainedObjects'][i - 1]['Nickname']
            id_to_tts_card[id]['image_uri'] = json_obj['CustomDeck'][str(i)]['FaceURL']
        elif (id_to_count_filter and id in id_to_count_filter):
            id_to_tts_card[id]['count'] = id_to_count_filter[id]
            id_to_tts_card[id]['name'] = json_obj['ContainedObjects'][i - 1]['Nickname']
            id_to_tts_card[id]['image_uri'] = json_obj['CustomDeck'][str(i)]['FaceURL']
        # else case intentionally ignored, as we don't want to add cards that are not in the filter
        i += 1
    return id_to_tts_card


def generate_id_to_tts_card_from_file(file, id_to_tts_card=None, id_to_count_filter:dict[str, ApiCard] = None):
    with file.open(encoding='utf8') as file:
        data = json.load(file)
    return generate_id_to_tts_card_from_json_obj(data, id_to_tts_card, id_to_count_filter)

def read_id_to_tts_card_from_filesystem(dreamborn_tts_export_filepath, id_to_count_filter:dict[str, ApiCard] = None):
    dreamborn_tts_export_path = Path(dreamborn_tts_export_filepath)
    id_to_tts_card = None
    if dreamborn_tts_export_path.is_dir():
        files = dreamborn_tts_export_path.glob('*')
        for file in files:
            if file.is_file():
                print(file)
                id_to_tts_card = generate_id_to_tts_card_from_file(file, id_to_tts_card, id_to_count_filter)
    else:
        id_to_tts_card = generate_id_to_tts_card_from_file(dreamborn_tts_export_path, id_to_tts_card, id_to_count_filter)
    return id_to_tts_card

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
    failed_ids = []
    for id, count in id_to_count.items():
        for i in range(0, count):
            if not id in id_to_custom_card:
                failed_ids.append(id)
                continue
            contained_obj = generate_contained_obj(id_to_custom_card[id]['name'], current_card_index, previous_card_index)
            card_image_url = id_to_custom_card[id]['image_uris']['en']
            custom_deck_obj = generate_custom_deck_obj(card_image_url)
            contained_obj_list.append(contained_obj)
            deck_ids.append(contained_obj['CardID'])
            custom_deck[str(current_card_index)] = custom_deck_obj
            previous_card_index = current_card_index
            current_card_index += 1
    if len(failed_ids) > 0:
        error_message = f"Unable to identify {len(failed_ids)} cards, including:\n"
        for failed_id in failed_ids:
            error_message += f"{failed_id}\n"
        raise UnidentifiedCardError(error_message) 
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
