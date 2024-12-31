from dataclasses import dataclass
from typing import List
import json
from enum import Enum

@dataclass(frozen=True)
class CubeSettings:
  boostersPerPlayer: int
  cardsPerBooster: int
  
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
  cubeSettings: CubeSettings
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

@dataclass(frozen=True)
class CubeListEntry:
  name: str
  cardCount: int
  tags: List[str]
  link: str
  author: str
  lastUpdatedEpochSeconds: str
  id: str
  
  def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)
  
@dataclass(frozen=True)
class Cube:
  name: str
  cardIdToCardCount: dict[str, int]
  nameToCardCount: dict[str, int]
  tags: List[str]
  link: str
  author: str
  lastUpdatedEpochSeconds: int
  id: str
  cubeSettings: CubeSettings
  
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