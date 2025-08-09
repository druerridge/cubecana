import json

class ApiCard:
    def __init__(self, full_name: str, cost: int, rarity: str, color: str, inks: list[str], types: list[str], set_num: int):
        self.full_name = full_name
        self.cost = cost
        self.rarity = rarity
        self.color = color
        self.inks = inks
        self.types = types
        self.set_num = set_num

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)