from dataclasses import dataclass
from typing import List
import json
from enum import Enum

@dataclass(frozen=True)
class CubeSettings:
  boostersPerPlayer: int
  cardsPerBooster: int
  powerBand: str

  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

@dataclass(frozen=True)
class CreateCubeRequest:
  name: str
  cardListText: str
  tags: List[str]
  link: str
  author: str
  featuredCardPrintingId: str
  cubeDescription: str
  cubeSettings: CubeSettings
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

@dataclass(frozen=True)
class EditCubeRequest:
  id: str
  name: str
  cardListText: str
  tags: List[str]
  link: str
  author: str
  featuredCardPrintingId: str
  cubeDescription: str
  cubeSettings: CubeSettings
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

@dataclass(frozen=True)
class RetailSetEntry:
  name: str
  id: str
  defaultGameMode: str
  availableGameModes: List[str]
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

@dataclass(frozen=True)
class RetailSet:
  name: str
  id: str
  draftmancerFile: str
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

# @dataclass(frozen=True)
# class CubeMetadata:
#   cardsPerBooster: int
#   cardCount: int
#   boostersPerPlayer: int
#   cubeName: str
#   link: str
#   author: str
#   power_band: str
  
#   def toJSON(self):
#     return json.dumps(
#         self,
#         default=lambda o: o.__dict__, 
#         sort_keys=True,
#         indent=4)

@dataclass(frozen=True)
class CubeListEntry:
  name: str
  cardCount: int
  tags: List[str]
  link: str
  author: str
  lastUpdatedEpochSeconds: str
  id: str
  timesDrafted: int
  timesViewed: int
  featuredCardImageLink: str
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)
  
@dataclass(frozen=True)
class Cube:
  name: str
  nameToCardCount: dict[str, int]
  tags: List[str]
  link: str
  author: str
  lastUpdatedEpochSeconds: int
  id: str
  cubeSettings: CubeSettings
  cubeDescription: str
  featuredCardImageLink: str
  featuredCardPrintingId: str
  timesViewed: int
  timesDrafted: int
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

class OrderType(str, Enum):
    ASC = 'asc'
    DESC = 'desc'

class SortType(str, Enum):
    RANK = 'rank'
    DATE = 'date'

@dataclass(frozen=True)
class SlotInfo:
    name: str
    weight: int
    probability: float
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

@dataclass(frozen=True)
class FormatAnalysisCard:
    name: str
    type: str
    inkCost: int
    rarity: str
    expectedAtTable: float
    copiesPerPack: float
    slotInfo: SlotInfo
    traits: List[str]
    strength: int = None
    willpower: int = None
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

@dataclass(frozen=True)
class FormatAnalysisSettings:
    boostersPerPlayer: int
    name: str
    withReplacement: bool
    playersCount: int
    totalPacks: int
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

@dataclass(frozen=True)
class FormatAnalysisResponse:
    setId: str
    countAtTableByCardType: dict[str, float]
    strengthDistributionByCost: dict[int, dict[str, float]]
    willpowerDistributionByCost: dict[int, dict[str, float]]
    costDistributionByClassification: dict[str, dict[int, float]]
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)