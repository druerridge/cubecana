import random

from . import api
from . import card_evaluations
from . import draftmancer
from . import franchise
from . import lcc_error
from .lorcast_api import lorcast_api as lorcana_api
from .retail_manager import retail_manager
from .settings import Settings


class DoubleFeatureManager:
    featured_franchise_count = 5
    featured_colors = ("W", "U", "B", "R", "G")

    def validate_draft_configuration(
        self, draft_configuration: api.DoubleFeatureDraftRequest
    ) -> None:
        featured_franchises = draft_configuration.featuredFranchises
        if not isinstance(featured_franchises, list):
            raise lcc_error.LccError("Featured franchises must be a list.", 400)
        if len(featured_franchises) != self.featured_franchise_count:
            raise lcc_error.LccError(
                f"Exactly {self.featured_franchise_count} featured franchises must be selected.",
                400,
            )
        if not all(isinstance(franchise_name, str) for franchise_name in featured_franchises):
            raise lcc_error.LccError("Featured franchises must be valid names.", 400)
        if not isinstance(draft_configuration.wildFranchise, str):
            raise lcc_error.LccError("A valid wild franchise must be selected.", 400)

        valid_franchises = set(franchise.load_franchises())
        invalid_featured_franchises = sorted(
            set(featured_franchises).difference(valid_franchises)
        )
        if invalid_featured_franchises:
            raise lcc_error.LccError(
                "Invalid featured franchises: "
                + ", ".join(invalid_featured_franchises),
                400,
            )
        if len(set(featured_franchises)) != self.featured_franchise_count:
            raise lcc_error.LccError(
                "Featured franchises must be unique.",
                400,
            )
        if draft_configuration.wildFranchise not in valid_franchises:
            raise lcc_error.LccError("A valid wild franchise must be selected.", 400)
        if draft_configuration.wildFranchise in featured_franchises:
            raise lcc_error.LccError(
                "The wild franchise must differ from the featured franchises.", 400
            )
        if not isinstance(draft_configuration.setIds, list):
            raise lcc_error.LccError("Selected sets must be a list.", 400)
        if not draft_configuration.setIds:
            raise lcc_error.LccError("At least one set must be selected.", 400)
        if not all(isinstance(set_id, str) for set_id in draft_configuration.setIds):
            raise lcc_error.LccError("Selected sets must have valid IDs.", 400)

        invalid_set_ids = sorted(
            set(draft_configuration.setIds).difference(retail_manager.retail_sets)
        )
        if invalid_set_ids:
            raise lcc_error.LccError(
                "Invalid selected sets: " + ", ".join(invalid_set_ids), 400
            )

    def generate_draftmancer_file(
        self, draft_configuration: api.DoubleFeatureDraftRequest
    ) -> str:
        self.validate_draft_configuration(draft_configuration)

        featured_franchise_to_color = dict(
            zip(
                draft_configuration.featuredFranchises,
                random.sample(self.featured_colors, self.featured_franchise_count),
            )
        )
        selected_franchises = set(featured_franchise_to_color)
        selected_franchises.add(draft_configuration.wildFranchise)
        selected_set_ids = set(draft_configuration.setIds)
        id_to_franchise = franchise.load_id_to_franchise()
        printing_id_to_count = {}
        card_id_to_colors = {}

        for card_id, api_card in lorcana_api.read_or_fetch_id_to_api_card().items():
            card_franchise = id_to_franchise.get(card_id)
            if card_franchise not in selected_franchises:
                continue

            printing = api_card.default_printing
            if printing.set_code not in selected_set_ids:
                printing = next(
                    (
                        card_printing
                        for card_printing in api_card.card_printings
                        if card_printing.set_code in selected_set_ids
                    ),
                    None,
                )
            if printing is None:
                continue

            printing_id_to_count[printing.printing_id()] = 1
            if card_franchise == draft_configuration.wildFranchise:
                card_id_to_colors[card_id] = []
            else:
                card_id_to_colors[card_id] = [
                    featured_franchise_to_color[card_franchise]
                ]

        if not printing_id_to_count:
            raise lcc_error.LccError(
                "No cards are available for the selected franchises.", 400
            )

        settings = Settings(
            card_list_name="Double Feature Draft",
            set_card_colors=True,
            color_balance_packs=True,
        )
        return draftmancer.generate_draftmancer_file(
            printing_id_to_count,
            card_evaluations.DEFAULT_RETAIL_CARD_EVALUATIONS_FILE,
            settings,
            card_id_to_colors=card_id_to_colors,
        )


double_feature_manager = DoubleFeatureManager()
