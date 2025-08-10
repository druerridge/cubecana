from dataclasses import dataclass
import json

@dataclass(frozen=True)
class PrintingId:
    card_id: str
    set_code: str
    collector_id: str

    def __hash__(self):
        return hash((self.card_id, self.set_code, self.collector_id))
    
    def __eq__(self, value):
        if not isinstance(value, PrintingId):
            return NotImplemented
        return (self.card_id, self.set_code, self.collector_id) == (value.card_id, value.set_code, value.collector_id)
    
    def __str__(self):
        return f"{self.card_id}-{self.set_code}-{self.collector_id}"
    
    # def toDraftmancer(self):
    #     return f"{self.card_id} ({self.set_code}) {self.collector_id}"

def toPrintingId(value: str) -> PrintingId:
    try:
        card_id, set_code, collector_id = value.split("-")
        return PrintingId(card_id=card_id, set_code=set_code, collector_id=collector_id)
    except ValueError:
        raise ValueError(f"Invalid PrintingId format: {value}")

@dataclass(frozen=True)
class CardPrinting:
    full_name: str
    collector_id: str
    set_code: str
    rarity: str

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)

class ApiCard:
    def __init__(self, full_name: str, cost: int, color: str, inks: list[str], types: list[str], card_printings: list[CardPrinting], default_printing: CardPrinting):
        self.full_name = full_name
        self.cost = cost
        self.color = color
        self.inks = inks
        self.types = types
        self.card_printings = card_printings
        self.default_printing = default_printing

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)