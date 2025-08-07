from dataclasses import dataclass
import json
from cube_manager import CubeManager, cube_manager
from settings import POWER_BAND_MAX, POWER_BAND_OVERPOWERED
import csv

@dataclass(frozen=True)
class CardPopularityReport: 
    id_to_num_copies_in_cubes: dict[str, int]
    id_to_num_cubes_containing: dict[str, int]
    id_to_ratio_cubes_included: dict[str, float]
    included_tags: list[str]
    included_power_bands: list[str]

    def to_csv(self, filename: str):
        """Export the report to a CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['Card ID', 'Num Copies', 'Num Cubes Containing', 'Ratio Cubes Included'])
            # Write data rows
            for card_id in self.id_to_num_copies_in_cubes:
                writer.writerow([
                    card_id,
                    self.id_to_num_copies_in_cubes[card_id],
                    self.id_to_num_cubes_containing[card_id],
                    self.id_to_ratio_cubes_included[card_id]
                ])
        print(f"CSV file created at {filename}")

    def to_csv_string(self) -> str:
        """Return the report as a CSV formatted string."""
        output = []
        output.append('Card ID,Num Copies,Num Cubes Containing,Ratio Cubes Included')
        for card_id in self.id_to_num_copies_in_cubes:
            output.append(f"{card_id},{self.id_to_num_copies_in_cubes[card_id]},{self.id_to_num_cubes_containing[card_id]},{self.id_to_ratio_cubes_included[card_id]}")
        return '\n'.join(output)

class Cubealytics:
    def generate_card_popularity_report(self, included_tags: list[str] = None, included_power_bands: str = None) -> CardPopularityReport:
        all_cube_lists = cube_manager.get_all_cube_lists(included_tags, included_power_bands)
        id_to_num_copies_in_cubes:dict[str, int] = dict[str, int]()
        id_to_num_cubes_containing: dict[str, int] = dict()
        for cube_list in all_cube_lists:
            for card_id, count in cube_list.items():
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
        card_popularity_report.to_csv("static/reports/power_max_card_popularity_report.csv")
        print(f"Cube report generated for tags: {included_tags}, power bands: {included_power_bands} analyzed {len(all_cube_lists)} cubes.")
        return card_popularity_report

cubealytics:Cubealytics = Cubealytics()
cubealytics.generate_card_popularity_report(included_tags=None, included_power_bands=[POWER_BAND_OVERPOWERED, POWER_BAND_MAX])