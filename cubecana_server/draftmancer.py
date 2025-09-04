from dataclasses import dataclass
import json
from pathlib import Path
from .lcc_error import UnidentifiedCardError, LccError
from .settings import Settings
from .card import ApiCard, CardPrinting, PrintingId
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
GENERATED_CUBES_DIR = 'generated_cubes'

class SlotCard:
    def __init__(self, printing_id:PrintingId, num_copies: int):
        self.printing_id = printing_id
        self.num_copies = num_copies

class Slot:
    def __init__(self, name, num_cards, slot_cards):
        self.name: str = name
        self.num_cards: int = num_cards
        self.slot_cards: list[SlotCard] = slot_cards

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

def generate_custom_card_list(
        id_to_rating: dict[str, int],
        printing_ids_to_include: list[PrintingId],
        settings: Settings
    ) -> list[dict]:
    custom_card_list:list[dict] = []
    failed_printing_ids = list[PrintingId]()
    for printing_id in printing_ids_to_include:
        card_id = printing_id.card_id
        api_card: ApiCard = lorcana_api.get_api_card(card_id)
        if api_card is None:
            failed_printing_ids.append(printing_id)
            continue

        # Strict Mode
        # printing: CardPrinting = next(filter(lambda printing: printing.printing_id() == printing_id, api_card.card_printings), None)
        # if printing is None:
        #     failed_printing_ids.append(printing_id)
        #     continue
        # Loose Mode
        printing: CardPrinting = lorcana_api.get_card_printing(printing_id) # will use default printing if it doesn't recognize
        # should add a warning
        ink_cost = api_card.cost
        full_name = api_card.full_name
        custom_card = {
            'name': full_name, 
            'mana_cost': f'{{{ink_cost}}}',
            'type': to_draftmancer_card_type(api_card, settings),
            'image_uris': {
                'en': dreamborn_manager.image_uri(printing_id, 'en'),
                'fr': dreamborn_manager.image_uri(printing_id, 'fr'),
                'de': dreamborn_manager.image_uri(printing_id, 'de'),
                'it': dreamborn_manager.image_uri(printing_id, 'it'),
                'ja': dreamborn_manager.image_uri(printing_id, 'ja'),
                'zh': dreamborn_manager.image_uri(printing_id, 'zh'),
            },
            'rarity': to_draftmancer_rarity(printing.rarity),
            'set': f"{printing.set_code}",
            'collector_number': printing.collector_id,
        }
        if card_id in id_to_rating:
            custom_card['rating'] = id_to_rating[card_id]
        else:
            print(f"Missing rating for {full_name}")
            # TODO: probably tell user rating is missing

        if "Location" in api_card.types:
            custom_card['layout'] = "split" # causes card to be displayed horizontally where possible        

        if (settings.set_card_colors):
                # FYI this is broken for Illumineer's quest boss cards
                custom_card['colors'] = to_draftmancer_colors(api_card.color, settings, api_card.inks)
        if (settings.franchise_to_color): # TODO: This needs additional Testing outside double feature cube
            color = franchise.retrieve_franchise_to_draftmancer_color(card_id)
            if color:
                custom_card['colors'] = [color]
            else:
                custom_card['colors'] = []
        custom_card_list.append(custom_card)
    if len(failed_printing_ids) > 0:
        error_message = f"Unable to identify {len(failed_printing_ids)} cards, including:"
        for failed_printing_id in failed_printing_ids:
            if lorcana_api.get_api_card(failed_printing_id.card_id) is None:
                error_message += f"\n Card: {failed_printing_id.card_id}"
            else:
                error_message += f"\n Print: {failed_printing_id}. "
                error_message += f"\n   Available printings: {', '.join([str(p.printing_id()) for p in api_card.card_printings])}"

        raise LccError(error_message, 404)
    return custom_card_list

def write_draftmancer_file(draftmancer_file_string, card_list_name):
    draftmancer_file_as_lines = draftmancer_file_string.split('\n')
    file_name = f'{card_list_name}.draftmancer.txt'
    file_path = Path(GENERATED_CUBES_DIR).joinpath(file_name)
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding="utf-8") as file:
        for line in draftmancer_file_as_lines:
            file.write(line + '\n')
    print(f'Wrote draftmancer file to {file_name}')

def generate_draftmancer_file(included_printing_ids_to_count:dict[PrintingId, int], card_evaluations_file: str, settings: Settings, slot_name_to_slot:dict[str, Slot]=None):
    id_to_rating = card_evaluations_manager.read_id_to_rating(card_evaluations_file)
    all_printings_from_same_set = all(printing_id.set_code == next(iter(included_printing_ids_to_count)).set_code for printing_id in included_printing_ids_to_count)
    if all_printings_from_same_set:
        preferred_set = next(iter(included_printing_ids_to_count)).set_code
        id_to_rating = card_evaluations_manager.read_id_to_rating(card_evaluations_file, preferred_set=preferred_set)
    custom_card_list = generate_custom_card_list(id_to_rating, list(included_printing_ids_to_count.keys()), settings)
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
        for printing_id in included_printing_ids_to_count:
            api_card = lorcana_api.get_api_card(printing_id.card_id)
            human_readable_printing = printing_id.to_human_readable(api_card.full_name)
            line_str = f"{included_printing_ids_to_count[printing_id]} {human_readable_printing}"
            lines.append(line_str)
    else:
        for slot_name in slot_name_to_slot:
            slot = slot_name_to_slot[slot_name]
            lines.append(f'[{slot_name}({slot.num_cards})]')
            for slot_card in slot.slot_cards:
                api_card = lorcana_api.get_api_card(slot_card.printing_id.card_id)
                human_readable_printing = slot_card.printing_id.to_human_readable(api_card.full_name)
                line_str = f"{slot_card.num_copies} {human_readable_printing}"
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
        # TODO: Read in SlotInfo / SlotCard / SlotPrinting
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
            # if "[" in line and "]" in line:

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
    return generate_draftmancer_file(cube.printing_id_to_count, card_evaluations_filename, cube.settings)

def dreamborn_tts_to_draftmancer_from_file(dreamborn_export_for_tabletop_sim, card_evaluations_file, settings):
    id_to_tts_card = tabletop_simulator.read_id_to_tts_card_from_filesystem(dreamborn_export_for_tabletop_sim)
    return dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings)

def dreamborn_card_list_to_draftmancer(card_list_input, card_evaluations_file, settings):
    card_list_lines = card_list_input.split('\n')
    printing_id_to_count = card_list_helper.printing_id_to_count_from(card_list_lines)
    return generate_draftmancer_file(printing_id_to_count, card_evaluations_file, settings)

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

def generate_printing_id_to_count_from_id_to_tts_card(id_to_tts_card) -> dict[PrintingId,int]:
    id_to_api_card: dict[str, ApiCard] = lorcana_api.read_or_fetch_id_to_api_card()
    printing_id_to_count = dict[PrintingId,int]()
    for card_id in id_to_tts_card:
        api_card: ApiCard = id_to_api_card[card_id]
        printing_id_to_count[api_card.default_printing.printing_id()] = id_to_tts_card[card_id]['count']
    return printing_id_to_count

def dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations_file, settings):
    printing_id_to_count = generate_printing_id_to_count_from_id_to_tts_card(id_to_tts_card)
    return generate_draftmancer_file(printing_id_to_count, card_evaluations_file, settings)
