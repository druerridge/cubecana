from dataclasses import dataclass
import json
from . import id_helper

@dataclass(frozen=True)
class PrintingId:
    card_id: str
    set_code: str
    collector_id: str

    def to_human_readable(self, full_name: str = None) -> str:
        name = self.card_id if not full_name else full_name
        return f"{name} ({self.set_code}) {self.collector_id}"

    def __hash__(self):
        return hash((self.card_id, self.set_code, self.collector_id))
    
    def __eq__(self, value):
        if not isinstance(value, PrintingId):
            return NotImplemented
        return (self.card_id, self.set_code, self.collector_id) == (value.card_id, value.set_code, value.collector_id)

    def __lt__(self, other):
        if not isinstance(other, PrintingId):
            return NotImplemented
        return (self.card_id, self.set_code, self.collector_id) < (other.card_id, other.set_code, other.collector_id)

    def __gt__(self, other):
        if not isinstance(other, PrintingId):
            return NotImplemented
        return (self.card_id, self.set_code, self.collector_id) > (other.card_id, other.set_code, other.collector_id)

    def __str__(self) -> str:
        return f"{self.card_id}-{self.set_code}-{self.collector_id}"
        
    def __repr__(self) -> str:
        return self.__str__()
    
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
    image_uris: dict[str, str]

    def printing_id(self) -> PrintingId:
        return PrintingId(
            card_id=id_helper.to_id(self.full_name),
            set_code=self.set_code,
            collector_id=self.collector_id
        )

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)

class ApiCard:
    def __init__(self, full_name: str, cost: int, color: str, inks: list[str], types: list[str], card_printings: list[CardPrinting], default_printing: CardPrinting, 
                 classifications: list[str] = None, strength: int = None, willpower: int = None):
        self.full_name = full_name
        self.cost = cost
        self.color = color
        self.inks = inks
        self.types = types
        self.card_printings = card_printings
        self.default_printing = default_printing
        self.classifications = classifications or []
        self.strength = strength
        self.willpower = willpower

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)