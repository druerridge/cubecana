import csv
from . import id_helper
from .cubecana_cube import CubecanaCube
from . import tags

DEFAULT_CARD_EVALUATIONS_FOLDER = "DraftBots/"
DEFAULT_CUBE_CARD_EVALUATIONS_FILE = "DraftBots/FrankKarsten-normalInk-maxPower-Evaluations.csv"
DEFAULT_RETAIL_CARD_EVALUATIONS_FILE = "DraftBots/FrankKarsten-normalInk-retailPower-Evaluations.csv"

class CardEvaluationsManager:

    def read_id_to_draftmancer_rating(self, card_evaluations_file:str, preferred_set_num:str=None) -> dict[str, int]:
        id_to_rating = {}
        with open(file=card_evaluations_file, newline='', encoding='utf8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            dialect.quoting = csv.QUOTE_MINIMAL
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            for row in reader:
                card_id = id_helper.to_id(row['Card Name'])
                card_rating = int(row['Rating - Draftmancer'])
                if preferred_set_num and id_to_rating.get(card_id) and row['Set'] != preferred_set_num:
                    continue
                id_to_rating[card_id] = card_rating
        return id_to_rating
    
    def read_id_to_letter_rating(self, card_evaluations_file:str, preferred_set_num=None) -> dict[str, str]:
        id_to_rating = {}
        with open(file=card_evaluations_file, newline='', encoding='utf8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            dialect.quoting = csv.QUOTE_MINIMAL
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            for row in reader:
                card_id = id_helper.to_id(row['Card Name'])
                card_rating = row['Rating - AF']
                if preferred_set_num and id_to_rating.get(card_id) and row['Set'] != preferred_set_num:
                    continue
                id_to_rating[card_id] = card_rating
        return id_to_rating

    def determine_card_evaluations_file(self, cube:CubecanaCube):
        if tags.TAG_LOW_INK in cube.tags:
            ink_level = "low"
        else:
            ink_level = "normal"
        evaluator = "FrankKarsten"
        evaluations_filename = f"{DEFAULT_CARD_EVALUATIONS_FOLDER}{evaluator}-{ink_level}Ink-{cube.settings.power_band.lower()}Power-Evaluations.csv"
        return evaluations_filename
    
card_evaluations_manager: CardEvaluationsManager = CardEvaluationsManager()