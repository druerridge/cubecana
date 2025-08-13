from . import draftmancer
from .lorcast_api import lorcast_api as lorcana_api
from .settings import Settings
from .dreamborn_manager import dreamborn_manager
from .card_evaluations import card_evaluations_manager
from .card import ApiCard, PrintingId

rarity_to_frequency = {
    "Common": 60,
    "Uncommon": 30,
    "Rare": 13,
    "Super Rare": 5,
    "Legendary": 2
}

class SlotCard:
    def __init__(self, card_id, num_copies):
        self.card_id = card_id
        self.num_copies = num_copies

class Slot:
    def __init__(self, name, num_cards, slot_cards):
        self.name = name
        self.num_cards = num_cards
        self.slot_cards = slot_cards

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
    for id in id_to_tts_card:
        api_card = id_to_api_card[id]
        card_printing = get_printing_from_set(api_card, set_code)
        rarity = card_printing.rarity
        color = api_card.color
        printing_id: PrintingId = card_printing.printing_id()
        frequency = rarity_to_frequency[rarity]
        printing_ids_to_count[printing_id] = frequency
        slots_to_append = calculate_slots_to_append(rarity, color)
        for slot_name in slots_to_append:
            slot_card = SlotCard(id, frequency)
            slot_name_to_slot[slot_name].slot_cards.append(slot_card)

    return draftmancer.generate_draftmancer_file(printing_ids_to_count, card_evaluations_file, settings, slot_name_to_slot)