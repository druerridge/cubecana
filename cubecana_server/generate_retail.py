import re
from . import draftmancer
from .draftmancer import Slot, SlotCard
from .lorcast_api import lorcast_api as lorcana_api
from .settings import Settings, POWER_BAND_RETAIL
from .card_evaluations import DEFAULT_RETAIL_CARD_EVALUATIONS_FILE
from .card import CardPrinting, PrintingId

# set code -> display name. Only sets listed here are offered as retail drafts.
RETAIL_SETS = {
    "1": "The First Chapter",
    "2": "Rise of the Floodborn",
    "3": "Into the Inklands",
    "4": "Ursula's Return",
    "5": "Shimmering Skies",
    "6": "Azurite Seas",
    "7": "Archazia's Island",
    "8": "Reign of Jafar",
    "9": "Fabled",
    "10": "Whispers in the Well",
    "11": "Winterspell",
    "12": "Wilds Unknown",
    "13": "Attack of the Vine!",
    "14": "Hyperia City",
}


# source: https://www.reddit.com/r/Lorcana/comments/1tmo95b/wilds_unknown_pull_rate_analysis/#lightbox
default_rarity_to_frequency = {
    "Common": 60_000,
    "Uncommon": 30_000,
    "Rare": 12_341, # guess: whatever is left after higher rarities are accounted for
    "Super Rare": 5_000, # guess: keep it same as pre-12
    "Legendary": 2_659, # 26.59%
    "Epic": 956, # 9.56%
    "Enchanted": 175, # 1.75%
    "Iconic": 19 # 0.19%
}

# old, similar source
rarity_to_frequency_pre_12 = {
    "Common": 60000,
    "Uncommon": 30000,
    "Rare": 13000,
    "Super Rare": 5000,
    "Legendary": 2000,
    "Epic": 200, # revisit w/ more data. ~= 1/50 packs 
    "Enchanted": 100,
    "Iconic": 5 # revisit w/ more data. ~= 1/2k packs
}

set_to_rarity_to_frequency_mapping = {
    "1": rarity_to_frequency_pre_12,
    "2": rarity_to_frequency_pre_12,
    "3": rarity_to_frequency_pre_12,
    "4": rarity_to_frequency_pre_12,
    "5": rarity_to_frequency_pre_12,
    "6": rarity_to_frequency_pre_12,
    "7": rarity_to_frequency_pre_12,
    "8": rarity_to_frequency_pre_12,
    "9": rarity_to_frequency_pre_12,
    "10": rarity_to_frequency_pre_12,
    "11": rarity_to_frequency_pre_12,
}

def get_rarity_to_frequency(set_code: str):
    if set_code in set_to_rarity_to_frequency_mapping:
        return set_to_rarity_to_frequency_mapping[set_code]
    else:
        return default_rarity_to_frequency

def calculate_slots_to_append(rarity, color):
    slots_to_append = []
    if rarity == "Common":
        slots_to_append.append(f"CommonSlot{color}")
    elif rarity == "Uncommon":
        slots_to_append.append("UncommonSlot")
    elif rarity == "Rare" or rarity == "Super Rare" or rarity == "Legendary":
        slots_to_append.append("RareOrHigherSlot")
    slots_to_append.append("FoilSlot")
    return slots_to_append

RETAIL_SET_EXCLUDED_PRINTING_IDS = [
    PrintingId(card_id="pigletpoohpiratecaptain", set_code="3", collector_id="223"), # alt art
    PrintingId(card_id="yensidpowerfulsorcerer", set_code="4", collector_id="223"), # alt art
    PrintingId(card_id="mickeymouseplayfulsorcerer", set_code="4", collector_id="225"), # alt art
    PrintingId(card_id="mulanelitearcher", set_code="4", collector_id="224"), # alt art
    PrintingId(card_id="nerofearsomecrocodile", set_code="8", collector_id="65f"), # alt art
    PrintingId(card_id="brutusfearsomecrocodile", set_code="8", collector_id="125f"), # alt art
    PrintingId(card_id="louieonecoolduck", set_code="8", collector_id="1f"), # alt art
    PrintingId(card_id="deweylovableshowoff", set_code="8", collector_id="2f"), # alt art
    PrintingId(card_id="hueyreliableleader", set_code="8", collector_id="3f"), # alt art
]

def base_collector_id(card_printing: CardPrinting) -> str:
    match = re.match(r'\d+', card_printing.collector_id)
    return match.group(0) if match else card_printing.collector_id

def count_variants_by_base_collector_id(card_printings: list[CardPrinting]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for card_printing in card_printings:
        base = base_collector_id(card_printing)
        counts[base] = counts.get(base, 0) + 1
    return counts

def remove_alt_art_printings(card_printings: list[CardPrinting]) -> list[CardPrinting]:
    # an alt art reprints a card at the same rarity under a higher collector number (e.g. Mr. Incredible - Super Strong 12-127 and 12-243).
    # keep only the lowest-numbered printing per rarity, plus its lettered variants (e.g. 4a-4e).
    rarity_to_lowest_base: dict[str, int] = {}
    for card_printing in card_printings:
        base = int(base_collector_id(card_printing))
        rarity_to_lowest_base[card_printing.rarity] = min(base, rarity_to_lowest_base.get(card_printing.rarity, base))
    return [p for p in card_printings if int(base_collector_id(p)) == rarity_to_lowest_base[p.rarity]]

def generate_retail_set_file(set_code: str) -> str:
    settings = Settings(card_list_name=RETAIL_SETS[set_code], with_replacement=True, power_band=POWER_BAND_RETAIL)
    return generate_retail_draftmancer_file(DEFAULT_RETAIL_CARD_EVALUATIONS_FILE, set_code, settings)

def generate_retail_draftmancer_file(card_evaluations_file, set_code:str, settings: Settings):
    # might have to map set # to this slot distribution situation or a strategy therein even 
    slot_name_to_slot = {
        'CommonSlotSteel': Slot("CommonSlotSteel", 1, []),
        'CommonSlotSapphire': Slot("CommonSlotSapphire", 1, []),
        'CommonSlotRuby': Slot("CommonSlotRuby", 1, []),
        'CommonSlotEmerald': Slot("CommonSlotEmerald", 1, []),
        'CommonSlotAmethyst': Slot("CommonSlotAmethyst", 1, []),
        'CommonSlotAmber': Slot("CommonSlotAmber", 1, []),
        'UncommonSlot': Slot("UncommonSlot", 3, []),
        'RareOrHigherSlot': Slot("RareOrHigherSlot", 2, []),
        'FoilSlot': Slot("FoilSlot", 1, [])
    }

    printing_ids_to_count: dict[PrintingId, int] = {}
    api_cards_from_set = lorcana_api.get_cards_from_set(set_code)
    for api_card in api_cards_from_set:
        card_printings = remove_alt_art_printings([p for p in api_card.card_printings if p.set_code == set_code and p.printing_id() not in RETAIL_SET_EXCLUDED_PRINTING_IDS])
        base_collector_id_to_variant_count = count_variants_by_base_collector_id(card_printings)
        for card_printing in card_printings:
            rarity = card_printing.rarity
            color = api_card.color
            # only commons are slotted by color. dual-ink cards have no single color.
            if rarity == "Common" and (color is None or color == "None"):
                raise ValueError(f"Failed to find color for common card '{api_card.full_name}'")
            printing_id: PrintingId = card_printing.printing_id()

            rarity_to_frequency = get_rarity_to_frequency(set_code)
            # variants (e.g. 4a-4e) share one card's worth of frequency
            frequency = rarity_to_frequency[rarity] // base_collector_id_to_variant_count[base_collector_id(card_printing)]
            printing_ids_to_count[printing_id] = frequency
            slots_to_append = calculate_slots_to_append(rarity, color)
            for slot_name in slots_to_append:
                slot_card = SlotCard(printing_id, frequency)
                slot_name_to_slot[slot_name].slot_cards.append(slot_card)
    return draftmancer.generate_draftmancer_file(printing_ids_to_count, card_evaluations_file, settings, slot_name_to_slot)