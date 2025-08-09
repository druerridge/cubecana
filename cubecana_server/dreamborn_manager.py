from pathlib import Path
from . import id_helper

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

    def get_id_to_dreamborn_name(self):
        return self.id_to_dreamborn_name

    def to_language_coded_image_uri(self, image_uri, language_code):
        if language_code == "en":
            return image_uri
        else:
            return image_uri.replace("en", language_code)
        
dreamborn_manager:DreambornManager = DreambornManager()