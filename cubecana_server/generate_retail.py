from . import draftmancer
from .draftmancer import Slot, SlotCard
from .lorcast_api import lorcast_api as lorcana_api
from .settings import Settings
from .dreamborn_manager import dreamborn_manager
from .card_evaluations import card_evaluations_manager
from .card import ApiCard, PrintingId

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
        return next(filter(lambda printing: printing.set_code == set_code, api_card.card_printings))
    else:
        return api_card.default_printing

def generate_retail_draftmancer_file(id_to_tts_card, card_evaluations_file, set_code:str, settings: Settings):
    id_to_api_card:dict[str, ApiCard] = lorcana_api.read_or_fetch_id_to_api_card()
    print("card_evaluations_file")
    print(card_evaluations_file)
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
    failures = []
    for id in id_to_tts_card:
        api_card = id_to_api_card.get(id)
        if not api_card:
            failures.append(id)
            continue
        card_printing = get_printing_from_set(api_card, set_code)
        rarity = card_printing.rarity
        color = api_card.color
        printing_id: PrintingId = card_printing.printing_id()
        frequency = rarity_to_frequency[rarity]
        printing_ids_to_count[printing_id] = frequency
        slots_to_append = calculate_slots_to_append(rarity, color)
        for slot_name in slots_to_append:
            slot_card = SlotCard(printing_id, frequency)
            slot_name_to_slot[slot_name].slot_cards.append(slot_card)
    if failures:
        raise ValueError(f"Failed to find API cards for IDs:\n {'\n'.join(failures)}")
    return draftmancer.generate_draftmancer_file(printing_ids_to_count, card_evaluations_file, settings, slot_name_to_slot)