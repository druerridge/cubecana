import json
from cubecana_server.card import PrintingId
from .draftmancer import DraftmancerFile
from .api import FormatAnalysisResponse
from . import id_helper
from .lorcast_api import lorcast_api as lorcana_api


class FormatAnalysisManager:
    def __init__(self):
        self.cache: dict[str, FormatAnalysisResponse] = {}

    def analyze(self, retail_set_code: str, draftmancer_file:DraftmancerFile, boosters_per_player:int, num_players:int) -> FormatAnalysisResponse:
        boosters_at_table = boosters_per_player * num_players
        
        # think about this and how/if we need to deal with boosters / player etc.
        # if retail_set_code in self.cache:
        #     return self.cache[retail_set_code]
        
        total_cards_by_slot_name = self.generate_total_cards_by_slot_name(draftmancer_file)
        count_at_table_by_card_id = self.generate_count_at_table_by_card_id(draftmancer_file, boosters_at_table, total_cards_by_slot_name)
        count_at_table_by_card_type = self.generate_count_at_table_by_card_type(count_at_table_by_card_id)

        format_analysis_response = {
            'setId': retail_set_code,
            'countAtTableByCardId': count_at_table_by_card_id,
            'countAtTableByCardType': count_at_table_by_card_type
        }
        self.cache[retail_set_code] = format_analysis_response
        return format_analysis_response

    def generate_count_at_table_by_card_type(self, count_at_table_by_card_id):
        countAtTableByCardType:dict[str, float] = {}
        for card_id, count_at_table in count_at_table_by_card_id.items():
            api_card = lorcana_api.get_api_card(card_id)
            for card_type in api_card.types:
                countAtTableByCardType[card_type] = countAtTableByCardType.get(card_type, 0) + count_at_table
        return countAtTableByCardType

    def generate_count_at_table_by_card_id(self, draftmancer_file, boosters_at_table, total_cards_by_slot_name):
        count_at_table_by_card_id: dict[str, float] = {}
        for slot in draftmancer_file.slots_by_name.values():
            for slot_card in slot.slot_cards:
                printing_id: PrintingId = slot_card.printing_id
                num_copies: int = slot_card.num_copies
                weight_per_booster_slot_for_printing: float = num_copies / total_cards_by_slot_name[slot.name] * slot.num_cards
                weight_per_table_slot_for_printing: float = weight_per_booster_slot_for_printing * boosters_at_table
                
                card_id: str = printing_id.card_id
                weight_per_table_for_card_id: float = count_at_table_by_card_id.get(card_id, 0) + weight_per_table_slot_for_printing
                count_at_table_by_card_id[card_id] = weight_per_table_for_card_id
        return count_at_table_by_card_id

    def generate_total_cards_by_slot_name(self, draftmancer_file):
        total_cards_by_slot_name: dict[str, int] = {}
        for slot in draftmancer_file.slots_by_name.values():
            for slot_card in slot.slot_cards:
                num_copies: int = slot_card.num_copies
                total_cards_by_slot_name[slot.name] = total_cards_by_slot_name.get(slot.name, 0) + num_copies
        return total_cards_by_slot_name

format_analysis_manager:FormatAnalysisManager = FormatAnalysisManager()
