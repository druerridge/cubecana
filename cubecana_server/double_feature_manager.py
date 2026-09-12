from . import api
from . import franchise
from . import lcc_error


class DoubleFeatureManager:
    featured_franchise_count = 5

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


double_feature_manager = DoubleFeatureManager()
