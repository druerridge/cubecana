import json
from cubecana_server.card import PrintingId
from .draftmancer import DraftmancerFile
from .api import FormatAnalysisResponse
from . import id_helper
from .lorcast_api import lorcast_api as lorcana_api


class FormatAnalysisManager:
    def __init__(self):
        self.cache: dict[str, FormatAnalysisResponse] = {}

    def analyze(self, draftmancer_file:DraftmancerFile, boosters_per_player:int, num_players:int) -> FormatAnalysisResponse:
        boosters_at_table = boosters_per_player * num_players
        
        # think about this and how/if we need to deal with boosters / player etc.
        # if retail_set_code in self.cache:
        #     return self.cache[retail_set_code]
        
        total_cards_by_slot_name = self.generate_total_cards_by_slot_name(draftmancer_file)
        count_at_table_by_card_id = self.generate_count_at_table_by_card_id(draftmancer_file, boosters_at_table, total_cards_by_slot_name)
        count_at_table_by_card_type = self.generate_count_at_table_by_card_type(count_at_table_by_card_id)
        count_at_table_by_ink_cost = self.generate_cost_distribution(count_at_table_by_card_id)
        strength_distribution_by_cost = self.generate_strength_distribution_by_cost(count_at_table_by_card_id)
        willpower_distribution_by_cost = self.generate_willpower_distribution_by_cost(count_at_table_by_card_id)
        lore_distribution_by_cost = self.generate_lore_distribution_by_cost(count_at_table_by_card_id)
        cost_distribution_by_classification = self.generate_cost_distribution_by_classification(count_at_table_by_card_id)

        format_analysis_response: FormatAnalysisResponse = FormatAnalysisResponse(
            # countAtTableByCardId = count_at_table_by_card_id, # for debugging purposes
            # countAtTableByInkCost = count_at_table_by_ink_cost, # for debugging purposes
            countAtTableByCardType = count_at_table_by_card_type,
            strengthDistributionByCost = strength_distribution_by_cost,
            willpowerDistributionByCost = willpower_distribution_by_cost,
            loreDistributionByCost = lore_distribution_by_cost,
            costDistributionByClassification = cost_distribution_by_classification,
            # countAtTableByRatingByInkCost = count_at_table_by_rating_by_ink_cost,
        )
        # self.cache[retail_set_code] = format_analysis_response
        return format_analysis_response

    def generate_cost_distribution_by_classification(self, count_at_table_by_card_id) -> dict[str, dict[int, float]]:
        count_at_table_by_classification:dict[str, dict[int, float]] = {}
        for card_id, count_at_table in count_at_table_by_card_id.items():
            api_card = lorcana_api.get_api_card(card_id)
            for classification in api_card.classifications:
                if classification not in count_at_table_by_classification:
                    count_at_table_by_classification[classification] = {}
                if api_card.cost not in count_at_table_by_classification[classification]:
                    count_at_table_by_classification[classification][api_card.cost] = 0
                count_at_table_by_classification[classification][api_card.cost] += count_at_table
        return count_at_table_by_classification

    def generate_willpower_distribution_by_cost(self, count_at_table_by_card_id) -> dict[int, dict[int, float]]:
        count_at_table_by_willpower:dict[int, dict[int, float]] = {}
        for card_id, count_at_table in count_at_table_by_card_id.items():
            api_card = lorcana_api.get_api_card(card_id)
            if 'Character' in api_card.types:
                if api_card.cost not in count_at_table_by_willpower:
                    count_at_table_by_willpower[api_card.cost] = {}
                willpower = api_card.willpower
                if willpower == None:
                    print(f"Warning: Card {api_card.full_name} is a Character but has no willpower value.")
                if willpower not in count_at_table_by_willpower[api_card.cost]:
                    count_at_table_by_willpower[api_card.cost][willpower] = 0
                count_at_table_by_willpower[api_card.cost][willpower] += count_at_table
        return count_at_table_by_willpower
    
    def generate_lore_distribution_by_cost(self, count_at_table_by_card_id) -> dict[int, dict[int, float]]:
        count_at_table_by_lore:dict[int, dict[int, float]] = {}
        for card_id, count_at_table in count_at_table_by_card_id.items():
            api_card = lorcana_api.get_api_card(card_id)
            if 'Character' in api_card.types:
                if api_card.cost not in count_at_table_by_lore:
                    count_at_table_by_lore[api_card.cost] = {}
                lore = api_card.lore
                if lore == None:
                    print(f"Warning: Card {api_card.full_name} is a Character but has no lore value.")
                if lore not in count_at_table_by_lore[api_card.cost]:
                    count_at_table_by_lore[api_card.cost][lore] = 0
                count_at_table_by_lore[api_card.cost][lore] += count_at_table
        return count_at_table_by_lore

    def generate_strength_distribution_by_cost(self, count_at_table_by_card_id) -> dict[int, dict[int, float]]:
        count_at_table_by_strength:dict[int, dict[int, float]] = {}
        for card_id, count_at_table in count_at_table_by_card_id.items():
            api_card = lorcana_api.get_api_card(card_id)
            if 'Character' in api_card.types:
                if api_card.cost not in count_at_table_by_strength:
                    count_at_table_by_strength[api_card.cost] = {}
                strength = api_card.strength
                if strength == None:
                    if card_id == 'rapunzelgiftedartist':
                        strength = 0 # Rapunzel, Gifted Artist has null strength in the API but actually 0
                    else:
                        print(f"Warning: Card {api_card.full_name} is a Character but has no strength value.")
                        print(api_card.toJSON())
                if strength not in count_at_table_by_strength[api_card.cost]:
                    count_at_table_by_strength[api_card.cost][strength] = 0
                count_at_table_by_strength[api_card.cost][strength] += count_at_table
        return count_at_table_by_strength

    def generate_cost_distribution(self, count_at_table_by_card_id):
        count_at_table_by_ink_cost:dict[int, float] = {}
        for card_id, count_at_table in count_at_table_by_card_id.items():
            api_card = lorcana_api.get_api_card(card_id)
            count_at_table_by_ink_cost[api_card.cost] = count_at_table_by_ink_cost.get(api_card.cost, 0) + count_at_table
        return count_at_table_by_ink_cost

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
