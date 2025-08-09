from dataclasses import dataclass
from collections import defaultdict
import json
from .lcc_error import LccError, UnidentifiedCardError
from .settings import Settings
from .card import ApiCard
from .lorcast_api import lorcast_api as lorcana_api
from . import id_helper
from . import franchise
from .cube_manager import CubecanaCube
from . import card_list_helper
from .card_evaluations import card_evaluations_manager
from . import tabletop_simulator
from .dreamborn_manager import dreamborn_manager

ALL_CARDS_DREAMBORN_TTS = "inputs/dreamborn_tts_all_cards"
INCOMPLETE_SIMPLE_TEMPLATE_PATH = "inputs/incomplete_simple_template.draftmancer.txt"
ALL_CARDS_CUBE_PATH = 'inputs/all_cards_cube.draftmancer.txt'

@dataclass(frozen=True)
class DraftmancerSettings:
  boostersPerPlayer: int = 4
  name: str = "Custom Cube"
  cardBack: str = "https://wiki.mushureport.com/images/thumb/d/d7/Card_Back_official.png/450px-Card_Back_official.png"
  withReplacement: bool = False
  # colorBalance: bool = False # do I need to add this back in?

  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

@dataclass(frozen=True)
class DraftmancerFile:
  draftmancer_settings: DraftmancerSettings
  id_to_custom_card: dict[str, dict]
  text_contents: str

lorcana_color_to_draftmancer_color =  {
    "Amber": "W",
    "Amethyst": "B",
    "Emerald": "G",
    "Ruby": "R",
    "Steel": "",
    "Sapphire": "U"
}
def to_draftmancer_colors(lorcana_ink, settings: Settings, lorcast_inks: list[str]):
    if not settings.set_card_colors:
        return []
    if lorcast_inks:
        draftmancer_colors = []
        for lorcast_color in lorcast_inks:
            draftmancer_colors.append(lorcana_color_to_draftmancer_color[lorcast_color])
        return draftmancer_colors
    if lorcana_color_to_draftmancer_color[lorcana_ink]:
        return [lorcana_color_to_draftmancer_color[lorcana_ink]]
    return []

lorcana_rarity_to_draftmancer_rarity =  {
    "Common": "common",
    "Uncommon": "uncommon",
    "Rare": "rare",
    "Super Rare": "mythic",
    "Legendary": "mythic"
}
def to_draftmancer_rarity(lorcana_rarity):
    return lorcana_rarity_to_draftmancer_rarity[lorcana_rarity]

def to_draftmancer_card_type(api_card: ApiCard, settings: Settings):
    if not settings.set_card_types:
        return "Instant"
    
    if "Character" in api_card.types:
        return "Creature"
    if "Song" in api_card.types: # must come before "Action"
        return "Instant"
    if "Action" in api_card.types:
        return "Sorcery"
    if "Item" in api_card.types:
        return "Artifact"
    if "Location" in api_card.types:
        return "Battle"
    return "Instant"  # Default

def generate_custom_card_list(id_to_api_card: dict[str, ApiCard], 
                              id_to_rating: dict[str, int],
                              id_to_tts_card: dict[str, dict], 
                              id_to_dreamborn_name: dict[str, str], 
                              settings: Settings):
    custom_card_list = []
    failed_ids = []
    for id in id_to_tts_card:
        if not id in id_to_api_card:
            failed_ids.append(id)
            continue
        api_card: ApiCard = id_to_api_card[id]            
        ink_cost = api_card.cost
        cannonical_name = id_helper.canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card)
        custom_card = {
            'name': cannonical_name, 
            'mana_cost': f'{{{ink_cost}}}',
            'type': to_draftmancer_card_type(api_card, settings),
            'image_uris': {
                'en': dreamborn_manager.to_language_coded_image_uri(id_to_tts_card[id]['image_uri'], 'en'),
                'fr': dreamborn_manager.to_language_coded_image_uri(id_to_tts_card[id]['image_uri'], 'fr'),
                'de': dreamborn_manager.to_language_coded_image_uri(id_to_tts_card[id]['image_uri'], 'de'),
                'it': dreamborn_manager.to_language_coded_image_uri(id_to_tts_card[id]['image_uri'], 'it'),
                'ja': dreamborn_manager.to_language_coded_image_uri(id_to_tts_card[id]['image_uri'], 'ja'),
                'zh': dreamborn_manager.to_language_coded_image_uri(id_to_tts_card[id]['image_uri'], 'zh'),
            },
            'rarity': to_draftmancer_rarity(api_card.rarity),
        }
        if id in id_to_rating:
            custom_card['rating'] = id_to_rating[id]
        else:
            print(f"Missing rating for {cannonical_name}")
            # TODO: probably tell user rating is missing

        if "Location" in api_card.types:
            custom_card['layout'] = "split" # causes card to be displayed horizontally were possible        

        if (settings.set_card_colors):
                # FYI this is broken for Illumineer's quest boss cards
                custom_card['colors'] = to_draftmancer_colors(api_card.color, settings, api_card.inks)
        if (settings.franchise_to_color): # TODO: This needs additional Testing outside double feature cube
            color = franchise.retrieve_franchise_to_draftmancer_color(id)
            if color:
                custom_card['colors'] = [color]
            else:
                custom_card['colors'] = []
        custom_card_list.append(custom_card)
    if len(failed_ids) > 0:
        error_message = f"Unable to identify {len(failed_ids)} cards, including:\n"
        for failed_id in failed_ids:
            error_message += f"{failed_id}\n"
        raise UnidentifiedCardError(error_message)
    return custom_card_list

def write_draftmancer_file(draftmancer_file_string, card_list_name):
    draftmancer_file_as_lines = draftmancer_file_string.split('\n')
    file_name = f'{card_list_name}.draftmancer.txt'
    with open(file_name, 'w', encoding="utf-8") as file:
        for line in draftmancer_file_as_lines:
            file.write(line + '\n')
    print(f'Wrote draftmancer file to {file_name}')

def generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings: Settings, slot_name_to_slot=None):
    draftmancer_settings = settings.to_draftmancer_settings()
            
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

def read_draftmancer_custom_cardlist(file_path=ALL_CARDS_CUBE_PATH):
    draftmancer_file:DraftmancerFile = read_draftmancer_file(file_path)
    if draftmancer_file == None:
        return None
    return draftmancer_file.id_to_custom_card

def read_draftmancer_file(file_path: str):
    with open(file_path, encoding='utf8') as f:
        custom_card_string = ""
        read_custom_cards = False
        settings_string = ""
        read_settings = False
        text_contents = ""
        open_braces = 0
        draftmancer_settings: DraftmancerSettings = None
        for line in f:
            text_contents += line
            if "[CustomCards]" in line:
                read_custom_cards = True
                read_settings = False
                continue
            if "[Settings]" in line:
                read_custom_cards = False
                read_settings = True
                continue
            if read_custom_cards:
                custom_card_string += line.strip()
            if read_settings:
                settings_string += line.strip()
                # try to decode, if it's done, it'll decode, otherwise it'll fail and we continue
                if "{" in line:
                    open_braces += 1
                if "}" in line:
                    open_braces -= 1
                    if open_braces <= 0:
                        try:
                            # Get the set of allowed keys from the dataclass fields
                            allowed_keys = set(DraftmancerSettings.__dataclass_fields__.keys())

                            # Parse the JSON string into a dictionary
                            settings_dict = json.loads(settings_string)

                            # Filter the dictionary to only include allowed keys
                            filtered_settings = {k: v for k, v in settings_dict.items() if k in allowed_keys}

                            # Now safely instantiate the dataclass
                            draftmancer_settings = DraftmancerSettings(**filtered_settings)
                            read_settings = False
                        except json.JSONDecodeError:
                            continue
        custom_cards_json = json.loads(custom_card_string)
        
        id_to_custom_card = {}
        for custom_card in custom_cards_json:
            try:
                input_name = custom_card['name']
                id = id_helper.to_id(input_name)
                id_to_custom_card[id] = custom_card
            except KeyError:
                raise UnidentifiedCardError(f"Unable to identify card with input name {input_name} and id {id} ")
        draftmancer_file = DraftmancerFile(draftmancer_settings, id_to_custom_card, text_contents)
        return draftmancer_file
    return None

def read_draftmancer_export(draftmancer_deck_export_file):
    with open(draftmancer_deck_export_file, encoding='utf8') as file:
        lines = file.readlines()
        mainboard_lines = card_list_helper.get_mainboard_lines(lines)
        return card_list_helper.id_to_count_from(mainboard_lines)

def generate_draftmancer_file_from_cube(cube: CubecanaCube):
    card_evaluations_filename = card_evaluations_manager.determine_card_evaluations_file(cube)
    return generate_draftmancer_file_from(cube.card_id_to_count, card_evaluations_filename, cube.settings)   

def generate_draftmancer_file_from(id_to_count_input, card_evaluations_file, settings):
    id_to_tts_card = tabletop_simulator.read_id_to_tts_card_from_filesystem(ALL_CARDS_DREAMBORN_TTS, id_to_count_input)
    return dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings)

def dreamborn_tts_to_draftmancer_from_file(dreamborn_export_for_tabletop_sim, card_evaluations_file, settings):
    id_to_tts_card = tabletop_simulator.read_id_to_tts_card_from_filesystem(dreamborn_export_for_tabletop_sim)
    return dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings)

def dreamborn_card_list_to_draftmancer(card_list_input, card_evaluations_file, settings):
    card_list_lines = card_list_input.split('\n')
    id_to_count_input = card_list_helper.id_to_count_from(card_list_lines)
    return add_card_list_to_draftmancer_custom_cards(id_to_count_input, INCOMPLETE_SIMPLE_TEMPLATE_PATH, settings)

def add_card_list_to_draftmancer_custom_cards(id_to_count_input, draftmancer_custom_card_file, settings: Settings):
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
    failed_ids = []
    for id in id_to_count_input:
        if not id in id_to_custom_card:
            failed_ids.append(id)
            continue
        canonical_name = id_to_custom_card[id]['name']
        file_contents += f"\n{id_to_count_input[id]} {canonical_name}"
    if len(failed_ids) > 0:
        error_message = f"Unable to identify {len(failed_ids)} cards, including:\n"
        for failed_id in failed_ids:
            error_message += f"{failed_id}\n"
        raise UnidentifiedCardError(error_message)
    return file_contents

def validate_card_list_against(card_list_input, draftmancer_custom_card_file=INCOMPLETE_SIMPLE_TEMPLATE_PATH):
    id_to_custom_card = read_draftmancer_custom_cardlist(draftmancer_custom_card_file)
    card_list_lines = card_list_input.split('\n')
    failed_card_names = []

    for line in card_list_lines:
        string_count, name = line.rstrip().split(' ', 1)
        try:
            int(string_count)
        except ValueError:
            raise LccError("Missing count or name in line:\n " + line + "\nShould look like:\n1 Elsa - Snow Queen", 400)
        id = id_helper.to_id(name)
        if not id in id_to_custom_card:
            failed_card_names.append(name)
            continue
        
    if len(failed_card_names) > 0:
        error_message = f"Unable to identify {len(failed_card_names)} cards, including:\n"
        if len(failed_card_names) > len(card_list_lines) / 2: 
            error_message = "If using non-English cards, you must convert to English card names for now\n" + error_message
        for failed_id in failed_card_names:
            error_message += f"{failed_id}\n"
        raise UnidentifiedCardError(error_message)
    

def dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings):
    id_to_dreamborn_name = dreamborn_manager.get_id_to_dreamborn_name()
    id_to_api_card = lorcana_api.read_or_fetch_id_to_api_card()
    id_to_rating = card_evaluations_manager.read_id_to_rating(card_evaluations_file)
    custom_card_list = generate_custom_card_list(id_to_api_card, id_to_rating, id_to_tts_card, id_to_dreamborn_name, settings)
    return generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings)
