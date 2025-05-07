import api

POWER_BAND_OVERPOWERED: str = "OVERPOWERED"
POWER_BAND_MAX: str = "MAX"
POWER_BAND_RETAIL: str = "RETAIL"
POWER_BAND_NARROW_MEDIUM: str = "NARROW_MEDIUM"

class Settings:
    def __init__(self, boosters_per_player=4, card_list_name='custom_cube', cards_per_booster=12, set_card_colors=False, color_balance_packs=False, with_replacement=False, franchise_to_color=False, power_band=POWER_BAND_MAX):
        self.boosters_per_player = int(boosters_per_player)
        self.card_list_name = card_list_name
        self.cards_per_booster = int(cards_per_booster)
        self.set_card_colors = bool(set_card_colors)
        self.color_balance_packs = bool(color_balance_packs)
        self.with_replacement = bool(with_replacement)
        self.franchise_to_color = bool(franchise_to_color)
        self.power_band = power_band

    def to_draftmancer_settings(self):
        draftmancer_settings = {
            'boostersPerPlayer': self.boosters_per_player,
            'name': self.card_list_name,
            'cardBack': 'https://wiki.mushureport.com/images/thumb/d/d7/Card_Back_official.png/450px-Card_Back_official.png',
            'withReplacement': self.with_replacement
        }

        if self.color_balance_packs == True:
            draftmancer_settings['colorBalance'] = True

        return draftmancer_settings
    
    def to_api_cube_settings(self):
        return api.CubeSettings(
            boostersPerPlayer= self.boosters_per_player,
            cardsPerBooster=self.cards_per_booster,
            powerBand=self.power_band
        )