from pathlib import Path
from . import id_helper
from .card import PrintingId

ALL_DREAMBORN_NAMES_FILE_PATH = 'inputs/all_dreamborn_names.txt'

class DreambornManager:
    def __init__(self):
        self.id_to_dreamborn_name = self._read_id_to_dreamborn_name()

    def _read_id_to_dreamborn_name(self):
        Path(ALL_DREAMBORN_NAMES_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(ALL_DREAMBORN_NAMES_FILE_PATH, encoding='utf8') as f:
            lines = f.readlines()
        id_to_dreamborn_name = {}
        for l in lines:
            name = l.strip()
            id_to_dreamborn_name[id_helper.to_id(name)] = name
        return id_to_dreamborn_name

    def get_id_to_dreamborn_name(self, id: str) -> str | None:
        return self.id_to_dreamborn_name.get(id)

    def is_number(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def to_image_set_code(self, set_code:str) -> str:
        if self.is_number(set_code):
            return f"{int(set_code):03d}"
        else:
            return set_code

    def to_image_collector_id(self, collector_id:str) -> str:
        if self.is_number(collector_id):
            return f"{int(collector_id):03d}"
        elif collector_id[-1:].isalpha(): # dalmation puppy - tail wagger 4a-4e/1
            # 4a -> 004a
            letter_part = collector_id[-1:]
            number_part = collector_id[0:-1]
            return f"{int(number_part):03d}{letter_part}"

    def image_uri(self, printing_id: PrintingId, language_code:str):
        image_set_code = self.to_image_set_code(printing_id.set_code)
        collector_id = self.to_image_collector_id(printing_id.collector_id)
        return f"https://cdn.dreamborn.ink/images/{language_code}/cards/{image_set_code}-{collector_id}?tts"  
        
dreamborn_manager:DreambornManager = DreambornManager()