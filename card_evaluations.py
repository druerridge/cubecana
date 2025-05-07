import csv
import id_helper
from cubecana_cube import CubecanaCube
import tags

DEFAULT_CARD_EVALUATIONS_FOLDER = "DraftBots/"
DEFAULT_CARD_EVALUATIONS_FILE = "DraftBots/FrankKarstenEvaluations-HighPower.csv"

class CardEvaluationsManager:

    def read_id_to_rating(self, card_evaluations_file):
        id_to_rating = {}
        with open(file=card_evaluations_file, newline='', encoding='utf8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            dialect.quoting = csv.QUOTE_MINIMAL
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            for row in reader:
                id_to_rating[id_helper.to_id(row['Card Name'])] = int(row['Rating - Draftmancer'])
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