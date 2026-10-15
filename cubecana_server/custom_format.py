import json
import re
from dataclasses import dataclass
from .lcc_error import LccError
from .settings import Settings
from .draftmancer import to_draftmancer_colors, to_draftmancer_card_type
from .lorcast_api import lorcast_api as lorcana_api
from . import id_helper

# A custom format mixes retail packs from several sets, e.g. 4 packs each of sets 5-8 for "Jafar Block Super Sealed".
# It's built by combining the already generated retail set files: each set's slots are renamed with a set prefix,
# grouped into one layout per set, and predeterminedLayouts fixes the order packs are opened in.

MIN_PACKS_PER_SET = 1
MAX_PACKS_PER_SET = 16
MAX_PACKS_PER_PLAYER = 24
MAX_NAME_LENGTH = 80
DEFAULT_NAME = "Custom Format"

# matches section headers like [CustomCards], [Settings], [UncommonSlot(3)]
SECTION_HEADER_PATTERN = re.compile(r'^\[(\w+)(?:\((\d+)\))?\]$')

@dataclass(frozen=True)
class PackSelection:
    set_id: str
    count: int

@dataclass(frozen=True)
class _Section:
    name: str
    num_cards: int
    lines: list[str]

def parse_pack_selections(packs) -> list[PackSelection]:
    if not isinstance(packs, list) or len(packs) == 0:
        raise LccError("Add at least one set of packs.", 400)
    pack_selections = []
    for pack in packs:
        if not isinstance(pack, dict):
            raise LccError("Each pack entry must be an object with a setId and count.", 400)
        set_id = str(pack.get('setId', ''))
        try:
            count = int(pack.get('count'))
        except (TypeError, ValueError):
            raise LccError(f"Invalid pack count for set {set_id}.", 400)
        if count < MIN_PACKS_PER_SET or count > MAX_PACKS_PER_SET:
            raise LccError(f"Pack count for set {set_id} must be between {MIN_PACKS_PER_SET} and {MAX_PACKS_PER_SET}.", 400)
        pack_selections.append(PackSelection(set_id, count))
    if total_packs(pack_selections) > MAX_PACKS_PER_PLAYER:
        raise LccError(f"Too many packs: max is {MAX_PACKS_PER_PLAYER} per player.", 400)
    return pack_selections

def clean_name(name) -> str:
    if not isinstance(name, str) or not name.strip():
        return DEFAULT_NAME
    return name.strip()[:MAX_NAME_LENGTH]

def total_packs(pack_selections: list[PackSelection]) -> int:
    return sum(pack_selection.count for pack_selection in pack_selections)

def _split_sections(draftmancer_file_contents: str) -> list[_Section]:
    sections: list[_Section] = []
    for line in draftmancer_file_contents.split('\n'):
        match = SECTION_HEADER_PATTERN.match(line.strip())
        if match:
            num_cards = int(match.group(2)) if match.group(2) else None
            sections.append(_Section(match.group(1), num_cards, []))
        elif sections:
            sections[-1].lines.append(line)
    return sections

def _layout_name(set_id: str) -> str:
    return f"Set{set_id}Layout"

def _slot_name(set_id: str, slot_name: str) -> str:
    return f"Set{set_id}{slot_name}"

def _add_deckbuilding_info(custom_cards: list[dict]):
    # the retail set files are generated without colors or card types, so add them here so cards can be sorted
    # by them when deckbuilding (e.g. sealed)
    settings = Settings(set_card_colors=True, set_card_types=True)
    for custom_card in custom_cards:
        api_card = lorcana_api.get_api_card(id_helper.to_id(custom_card['name']))
        custom_card['colors'] = to_draftmancer_colors(api_card.color, settings, api_card.inks)
        custom_card['type'] = to_draftmancer_card_type(api_card, settings)

def generate_custom_format_file(name: str, pack_selections: list[PackSelection], set_id_to_draftmancer_file: dict[str, str], add_deckbuilding_info: bool = False) -> str:
    custom_cards: list[dict] = []
    layouts: dict[str, dict] = {}
    slot_lines: list[str] = []
    base_settings: dict = None
    ratings_missing = False

    # a set picked in several rows still only needs its cards and slots once
    for set_id in dict.fromkeys(pack_selection.set_id for pack_selection in pack_selections):
        sections = _split_sections(set_id_to_draftmancer_file[set_id])
        layout_slots: dict[str, int] = {}
        for section in sections:
            if section.name == 'CustomCards':
                custom_cards.extend(json.loads('\n'.join(section.lines)))
            elif section.name == 'Settings':
                set_settings = json.loads('\n'.join(section.lines))
                ratings_missing = ratings_missing or set_settings.get('ratingsMissing', False)
                if base_settings is None:
                    base_settings = set_settings
            else:
                if section.num_cards is None:
                    raise LccError(f"Retail set {set_id} slot {section.name} is missing a card count.", 500)
                prefixed_slot_name = _slot_name(set_id, section.name)
                layout_slots[prefixed_slot_name] = section.num_cards
                slot_lines.append(f'[{prefixed_slot_name}]')
                slot_lines.extend(line for line in section.lines if line.strip())
        layouts[_layout_name(set_id)] = {'weight': 1, 'slots': layout_slots}

    if add_deckbuilding_info:
        _add_deckbuilding_info(custom_cards)

    predetermined_layouts = [_layout_name(pack_selection.set_id) for pack_selection in pack_selections for _ in range(pack_selection.count)]
    settings = {
        'boostersPerPlayer': len(predetermined_layouts),
        'name': name,
        'cardBack': base_settings['cardBack'],
        'withReplacement': True,
        'layouts': layouts,
        'predeterminedLayouts': predetermined_layouts,
    }
    if ratings_missing:
        settings['ratingsMissing'] = True

    lines = [
        '[CustomCards]',
        json.dumps(custom_cards, indent=4),
        '[Settings]',
        json.dumps(settings, indent=4),
    ]
    lines.extend(slot_lines)
    return '\n'.join(lines)
