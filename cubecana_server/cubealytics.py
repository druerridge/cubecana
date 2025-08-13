import json
from dataclasses import dataclass
from .cube_manager import CubeManager, cube_manager
from .settings import POWER_BAND_MAX, POWER_BAND_OVERPOWERED
from .lorcast_api import lorcast_api as lorcana_api
import csv
from pathlib import Path
from .card import PrintingId

@dataclass(frozen=True)
class CardPopularityReport: 
    id_to_num_copies_in_cubes: dict[str, int]
    id_to_num_cubes_containing: dict[str, int]
    id_to_ratio_cubes_included: dict[str, float]
    included_tags: list[str]
    included_power_bands: list[str]

    def write_to_csv(self, filename: str):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Card Name','Set Number', 'Num Copies', 'Num Cubes Containing', 'Ratio Cubes Included'])
            for card_id in self.id_to_num_copies_in_cubes:
                api_card = lorcana_api.get_api_card(card_id)
                if api_card is None:
                    # print(f"Card ID {card_id} not found in API data while generating CardPopularityReport, skipping.")
                    continue
                full_name = api_card.full_name
                set_code = api_card.default_printing.set_code
                writer.writerow([
                    full_name,
                    set_code,
                    self.id_to_num_copies_in_cubes[card_id],
                    self.id_to_num_cubes_containing[card_id],
                    self.id_to_ratio_cubes_included[card_id],
                ])
        print(f"CSV file created at {filename}")

class Cubealytics:
    def generate_card_popularity_report(self, included_tags: list[str] = None, included_power_bands: str = None) -> CardPopularityReport:
        all_cube_lists: list[dict[PrintingId, int]] = cube_manager.get_all_cube_lists(included_tags, included_power_bands)
        id_to_num_copies_in_cubes:dict[str, int] = dict[str, int]()
        id_to_num_cubes_containing: dict[str, int] = dict()
        for cube_list in all_cube_lists:
            for printing_id, count in cube_list.items():
                card_id = printing_id.card_id
                if card_id not in id_to_num_copies_in_cubes:
                    id_to_num_copies_in_cubes[card_id] = 0
                    id_to_num_cubes_containing[card_id] = 0
                id_to_num_copies_in_cubes[card_id] += count
                id_to_num_cubes_containing[card_id] += 1

        id_to_ratio_cubes_included: dict[str, float] = dict[str, float]()
        for card_id in id_to_num_cubes_containing:
            id_to_ratio_cubes_included[card_id] = id_to_num_cubes_containing[card_id] / all_cube_lists.__len__()

        card_popularity_report = CardPopularityReport(
            id_to_num_copies_in_cubes=id_to_num_copies_in_cubes,
            id_to_num_cubes_containing=id_to_num_cubes_containing,
            id_to_ratio_cubes_included=id_to_ratio_cubes_included,
            included_tags=included_tags,
            included_power_bands=included_power_bands,
        )
        card_popularity_report.write_to_csv("static/reports/power_max_card_popularity_report.csv")
        print(f"Cube report generated for tags: {included_tags}, power bands: {included_power_bands} analyzed {len(all_cube_lists)} cubes.")
        return card_popularity_report

cubealytics:Cubealytics = Cubealytics()
cubealytics.generate_card_popularity_report(included_tags=None, included_power_bands=[POWER_BAND_OVERPOWERED, POWER_BAND_MAX])