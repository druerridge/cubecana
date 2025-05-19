import create_template
import lorcast_api as lorcana_api
from settings import Settings
from card_evaluations import card_evaluations_manager, CardEvaluationsManager

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

def generate_retail_draftmancer_file(id_to_tts_card, card_evaluations_file, settings: Settings):
    id_to_dreamborn_name = create_template.read_id_to_dreamborn_name()
    id_to_api_card = lorcana_api.read_or_fetch_id_to_api_card()
    print("card_evaluations_file")
    print(card_evaluations_file)
    id_to_rating = card_evaluations_manager.read_id_to_rating(card_evaluations_file)
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

    for id in id_to_tts_card:
        api_card = id_to_api_card[id]
        rarity = api_card.rarity
        color = api_card.color
        frequency = rarity_to_frequency[rarity]
        slots_to_append = calculate_slots_to_append(rarity, color)
        for slot_name in slots_to_append:
            slot_card = SlotCard(id, frequency)
            slot_name_to_slot[slot_name].slot_cards.append(slot_card)

    custom_card_list = create_template.generate_custom_card_list(id_to_api_card, id_to_rating, id_to_tts_card, id_to_dreamborn_name, settings)
    return create_template.generate_draftmancer_file(custom_card_list, id_to_tts_card, id_to_dreamborn_name, settings, slot_name_to_slot)