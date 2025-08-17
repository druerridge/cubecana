from dataclasses import dataclass

class LccError(Exception):
    def __init__(self, user_facing_message, http_status_code):
        self.user_facing_message = user_facing_message
        self.http_status_code = http_status_code
        super().__init__(self.user_facing_message) # I know the parent isn't necessarily looking for the user-facing one, worth separating later maybe

@dataclass(frozen=True)
class UnidentifiedPrinting():
    unidentifiable_input:str
    available_printing_names:list[str]

class UnidentifiedPrintingError(LccError):
    def __init__(self, unidentified_printing:UnidentifiedPrinting):
        self.unidentified_printing = unidentified_printing
        self.available_printing_names = unidentified_printing.available_printing_names
        user_facing_message = f"Unable to identify printing for card: {unidentified_printing.unidentifiable_input}.\n  Available Printings: {', '.join(unidentified_printing.available_printing_names)}"
        super().__init__(user_facing_message, 404)

class UnidentifiedPrintingsError(LccError):
    def __init__(self, unidentified_printing_errors: list[UnidentifiedPrintingError]):
        user_facing_message = "Unable to identify printings for cards:"
        for unidentified_printing_error in unidentified_printing_errors:
            unidentified_printing = unidentified_printing_error.unidentified_printing
            user_facing_message += f"\n {unidentified_printing.unidentifiable_input}.\n  Available Printings: {', '.join(unidentified_printing.available_printing_names)}"
        super().__init__(user_facing_message, 404)

class UnidentifiedCardError(LccError):
    def __init__(self, unidentified_input:str):
        self.unidentified_input = unidentified_input
        user_facing_message = f"Unable to identify card from: {unidentified_input}"
        super().__init__(user_facing_message, 404)

class UnidentifiedCardsError(LccError):
    def __init__(self, unidentified_card_errors: list[UnidentifiedCardError]):
        user_facing_message = "Unable to identify cards from the following:"
        for unidentified_card_error in unidentified_card_errors:
            user_facing_message += f"\n {unidentified_card_error.unidentified_input}"
        super().__init__(user_facing_message, 404)
   
class UnauthorizedError(LccError):
    def __init__(self, user_facing_message):
        super().__init__(user_facing_message, 401)
        
class CubeNotFoundError(LccError):
    def __init__(self, user_facing_message):
        super().__init__(user_facing_message, 404)
        
class RetailSetNotFoundError(LccError):
    def __init__(self, user_facing_message):
        super().__init__(user_facing_message, 404)