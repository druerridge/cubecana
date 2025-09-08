from . import draftmancer
from .draftmancer import Slot, SlotCard
from .lorcast_api import lorcast_api as lorcana_api
from .settings import Settings
from .dreamborn_manager import dreamborn_manager
from .card_evaluations import card_evaluations_manager
from .card import ApiCard, PrintingId, CardPrinting
from .lorcana import ALT_ART_RARITIES

rarity_to_frequency = {
    "Common": 60000,
    "Uncommon": 30000,
    "Rare": 13000,
    "Super Rare": 5000,
    "Legendary": 2000,
    "Epic": 200, # revisit w/ more data. ~= 1/50 packs 
    "Enchanted": 100,
    "Iconic": 5 # revisit w/ more data. ~= 1/2k packs
}

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

def get_printing_from_set(api_card: ApiCard, set_code: str):
    if set_code:
        printings_from_set = list(filter(lambda printing: printing.set_code == set_code, api_card.card_printings))
        if not printings_from_set:
            raise ValueError(f"Failed to find printing for card '{api_card.full_name}' in set '{set_code}'")
        return next(filter(lambda printing: printing.rarity not in ALT_ART_RARITIES, api_card.card_printings), printings_from_set[0])
    else:
        return api_card.default_printing

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

def generate_retail_draftmancer_file(card_evaluations_file, set_code:str, settings: Settings):
    print("card_evaluations_file")
    print(card_evaluations_file)

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
        for card_printing in list(filter(lambda p: p.set_code == set_code, api_card.card_printings)):
            if card_printing.printing_id() in RETAIL_SET_EXCLUDED_PRINTING_IDS:
                continue
            rarity = card_printing.rarity
            color = api_card.color
            printing_id: PrintingId = card_printing.printing_id()
            frequency = rarity_to_frequency[rarity]
            printing_ids_to_count[printing_id] = frequency
            slots_to_append = calculate_slots_to_append(rarity, color)
            for slot_name in slots_to_append:
                slot_card = SlotCard(printing_id, frequency)
                slot_name_to_slot[slot_name].slot_cards.append(slot_card)
    return draftmancer.generate_draftmancer_file(printing_ids_to_count, card_evaluations_file, settings, slot_name_to_slot)