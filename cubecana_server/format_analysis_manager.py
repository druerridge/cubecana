from .draftmancer import DraftmancerFile
from .api import FormatAnalysisResponse
from . import id_helper
from .lorcast_api import lorcast_api as lorcana_api


class FormatAnalysisManager:
    def __init__(self):
        self.cache: dict[str, FormatAnalysisResponse] = {}

    def analyze(self, retail_set_code: str, draftmancer_file:DraftmancerFile, boosters_per_player:int = None, num_players:int = None) -> FormatAnalysisResponse:
        # think about this and how/if we need to deal with boosters / player etc.
        # if retail_set_code in self.cache:
        #     return self.cache[retail_set_code]
        
        countAtTableById: dict[str, float] = {}
        # for 
        
        countAtTableByCardType:dict[str, float] = {}
        for custom_card in draftmancer_file.id_to_custom_card.values():
            name = custom_card['name']
            api_card = lorcana_api.get_api_card(name)
            
            # countAtTable = 
            countAtTableByCardType[api_card.type] = countAtTableByCardType.get(api_card.type, 0) + 1

        format_analysis_response = FormatAnalysisResponse(
            setId=draftmancer_file.id,
            setName=draftmancer_file.draftmancer_settings.name,
            countAtTableByCardType=countAtTableByCardType,
            countOfClassificationAtTableByInkCost={},
            strengthDistributionByInkCostAtTable={},
            willpowerDistributionByInkCost={},
            settings={draftmancer_file.draftmancer_settings.__dict__}
        )
        self.cache[retail_set_code] = format_analysis_response
        return format_analysis_response

format_analysis_manager:FormatAnalysisManager = FormatAnalysisManager()
