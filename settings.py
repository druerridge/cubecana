class Settings:
    def __init__(self, boosters_per_player, card_list_name, cards_per_booster, set_card_colors, color_balance_packs, with_replacement=False):
        self.boosters_per_player = int(boosters_per_player)
        self.card_list_name = card_list_name
        self.cards_per_booster = int(cards_per_booster)
        self.set_card_colors = bool(set_card_colors)
        self.color_balance_packs = bool(color_balance_packs)
        self.with_replacement = bool(with_replacement)

    def to_draftmancer_settings(self):
        return {
            'boostersPerPlayer': self.boosters_per_player,
            'name': self.card_list_name,
            'cardBack': 'https://wiki.mushureport.com/images/thumb/d/d7/Card_Back_official.png/450px-Card_Back_official.png',
            'withReplacement': self.with_replacement
        }