import base64
from datetime import datetime
import lcc_error
import id_helper

class PixelbornManager:
    def __init__(self):
        self.id_to_pixelborn_name = self._load_id_to_pixelborn_name()

    def _load_id_to_pixelborn_name(self):
        id_to_pixelborn_name = {}
        with open('inputs/pixelborn_all_cards.txt', 'r') as file:
            for line in file:
                pixelborn_name = line.strip()
                id = id_helper.to_id(pixelborn_name)
                id_to_pixelborn_name[id] = pixelborn_name
        return id_to_pixelborn_name

    def generate_pixelborn_deck(self, id_to_count):
        pixelborn_deck_decoded = ""
        for id, count in id_to_count.items():
            try:
                pixelborn_deck_decoded += f"{self.id_to_pixelborn_name[id]}${count}|"            
            except KeyError:
                raise lcc_error.UnidentifiedCardError(f"Unable to identify card with id {id} ")
        pixelborn_deck_encoded = base64.b64encode(pixelborn_deck_decoded.encode('utf-8')).decode('utf-8')
        return pixelborn_deck_encoded

    def inktable_import_link(self, pixelborn_deck_encoded):
        current_time = datetime.now().isoformat()
        return f"https://www.inktable.net/lor/import?svc=dreamborn&name={current_time}&id={pixelborn_deck_encoded}"

    def lorcanito_import_link(self, pixelborn_deck_encoded):
        current_time = datetime.now().isoformat()
        return f"https://db.lorcanito.com/decks/import?source=cubecana&name={current_time}&list={pixelborn_deck_encoded}"
    
pixelborn_manager:PixelbornManager = PixelbornManager()