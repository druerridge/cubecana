class LccError(Exception):
    def __init__(self, user_facing_message, http_status_code):
        self.user_facing_message = user_facing_message
        self.http_status_code = http_status_code
        super().__init__(self.user_facing_message) # I know the parent isn't necessarily looking for the user-facing one, worth separating later maybe

class UnidentifiedCardError(LccError):
    def __init__(self, user_facing_message):
        super().__init__(user_facing_message, 404)
   
class UnauthorizedError(LccError):
    def __init__(self, user_facing_message):
        super().__init__(user_facing_message, 401)