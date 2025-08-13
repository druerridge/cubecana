from collections import defaultdict
from . import id_helper
from .card import CardPrinting, PrintingId, ApiCard
from .lcc_error import LccError, UnidentifiedCardError
from .lorcast_api import lorcast_api as lorcana_api

def get_mainboard_lines(all_lines):
  try: 
    empty_index = all_lines.index("")
    return all_lines[:empty_index]
  except ValueError:
    try:
        empty_index = all_lines.index("\n")
        return all_lines[:empty_index]
    except ValueError:
        return all_lines

def id_to_count_from(lines):
    id_to_count = defaultdict(int)
    for line in lines:
        string_count, name = line.rstrip().split(' ', 1)
        try:
            int_count = int(string_count)
            id_to_count[id_helper.to_id(name)] += int_count
        except ValueError:
            raise LccError("Missing count or name in line:\n " + line + "\nShould look like:\n1 Elsa - Snow Queen", 400)
    return id_to_count

def is_language_code(value: str) -> bool:
    return len(value) == 2 and value.isalpha() and value.islower()

def is_collector_number_format(collector_id: str) -> bool:
    if is_number(collector_id):
        return True
    # Dalmation Puppy - Tail Wagger (3) 4a-e 
    if is_number(collector_id[:-1]) and collector_id[-1].isalpha():
        return True
    #Mickey Mouse - True Friend (P1) 25ja/zh
    if is_number(collector_id[:-2]) and is_language_code(collector_id[-2:]):
        return True
    return False

def determine_input_collector_id(tokens:list[str], token_types: list[str]) -> str:
    collector_id_index = token_types.index(TOKEN_TYPE_COLLECTOR_ID)
    if collector_id_index < token_types.index(TOKEN_TYPE_SET_CODE):
        return None
    collector_id_in = tokens[collector_id_index]
    if not collector_id_in:
        return None
    if not is_collector_number_format(collector_id_in):
        return None
    return collector_id_in

def determine_input_set_code(tokens:list[str], token_types: list[str]) -> str:
    set_code_index = token_types.index(TOKEN_TYPE_SET_CODE)
    set_code_in = tokens[set_code_index]
    if set_code_in and set_code_in[0] == '(' and set_code_in[-1] == ')':
        return set_code_in[1:-1]
    return None

def is_number(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False
    
TOKEN_TYPE_COLLECTOR_ID = 'collector_id'
TOKEN_TYPE_SET_CODE = 'set_code'
TOKEN_TYPE_PARTIAL_CARD_NAME = 'partial_card_name'
TOKEN_TYPE_COUNT = 'count'

def determine_token_type(token: str) -> str:
  if token[0] == '(' and token[-1] == ')':
      return TOKEN_TYPE_SET_CODE
  if is_collector_number_format(token):
      return TOKEN_TYPE_COLLECTOR_ID
  return TOKEN_TYPE_PARTIAL_CARD_NAME

def get_card_name(tokens: list[str], token_types: list[str]):
    if TOKEN_TYPE_SET_CODE in token_types:
        set_code_index = token_types.index(TOKEN_TYPE_SET_CODE)
        return ' '.join(tokens[1:set_code_index])
    return ' '.join(tokens[1:])

def matches_input_printing(printing:CardPrinting, input_set_code: str, input_collector_id: str):
    if input_set_code:
        if printing.set_code != input_set_code:
            return False
        if input_collector_id and printing.collector_id != input_collector_id:
            return False
    return True

def get_matching_printing(input_set_code: str, input_collector_id: str, api_card: ApiCard) -> CardPrinting:
    if not input_set_code and not input_collector_id:
        return api_card.default_printing
    return next(filter(lambda printing: matches_input_printing(printing, input_set_code, input_collector_id), api_card.card_printings), None)

def calculate_token_types(tokens: list[str]) -> list[str]:
    token_types = [TOKEN_TYPE_PARTIAL_CARD_NAME] * len(tokens)
    token_types[0] = TOKEN_TYPE_COUNT
    token_types[-1] = determine_token_type(tokens[-1])
    token_types[-2] = TOKEN_TYPE_PARTIAL_CARD_NAME
    if token_types[-1] == TOKEN_TYPE_COLLECTOR_ID:  
        token_types[-2] = determine_token_type(tokens[-2])
    if token_types[-2] != TOKEN_TYPE_SET_CODE:
        token_types[-1] = TOKEN_TYPE_PARTIAL_CARD_NAME
    return token_types

def printing_id_to_count_from_id_to_count(id_to_count: dict[str, int]) -> dict[PrintingId, int]:
    printing_id_to_count = {}
    for card_id, count in id_to_count.items():
        api_card = lorcana_api.get_api_card(card_id)
        if api_card is None:
            raise UnidentifiedCardError(f"Unable to identify card: {card_id}")
        printing_id = api_card.default_printing.printing_id()
        printing_id_to_count[printing_id] = count
    return printing_id_to_count

def validate_card_list(card_list_input):
    card_list_lines = card_list_input.split('\n')
    printing_id_to_count_from(card_list_lines)
    # this will raise errors if cards are not recognized wholesale

def id_to_count_from_printing_id_to_count(printing_id_to_count: dict[PrintingId, int]) -> dict[str, int]:
    id_to_count = dict[str, int]()
    for printing_id, count in printing_id_to_count.items():
        if printing_id.card_id not in id_to_count:
            id_to_count[printing_id.card_id] = count
        else:
            id_to_count[printing_id.card_id] += count
    return id_to_count

def printing_id_to_count_from(card_list_lines):
    printing_id_to_count = defaultdict(int)
    failed_printing_ids = list[PrintingId]()
    for line in card_list_lines:
        tokens = line.rstrip().split(' ')
        if len(tokens) < 2:
            raise LccError("Missing count or name in line:\n " + line + "\nShould look like:\n1 Elsa - Snow Queen", 400)
        token_types: list[str] = calculate_token_types(tokens)

        try:
            int_count = int(tokens[0])
            
            card_name = get_card_name(tokens, token_types)

            card_id = id_helper.to_id(card_name)
            api_card = lorcana_api.get_api_card(card_id)
            if api_card is None:
                failed_printing_ids.append(PrintingId(card_id=card_id, set_code=None, collector_id=None))
                continue

            input_set_code = None
            input_collector_id = None
            # only case we find special printings
            if TOKEN_TYPE_SET_CODE in token_types:
                input_set_code = determine_input_set_code(tokens, token_types)
                input_collector_id = determine_input_collector_id(tokens, token_types)

            printing: CardPrinting = get_matching_printing(input_set_code, input_collector_id, api_card)
            # Strict Mode
            if printing is None:
                failed_printing_ids.append(PrintingId(card_id=card_id, set_code=input_set_code, collector_id=input_collector_id))
                continue
            # Loose Mode
            # if printing is None:
            #     # todo: send warning to users
            #     printing = api_card.default_printing
            printing_id_to_count[printing.printing_id()] += int_count
        except ValueError:
            raise LccError("Missing count or name in line:\n " + line + "\nShould look like:\n1 Elsa - Snow Queen", 400)

    if failed_printing_ids:
        error_message = f"Unable to identify {len(failed_printing_ids)} cards, including:"
        for failed_printing_id in failed_printing_ids:
            api_card = lorcana_api.get_api_card(failed_printing_id.card_id)
            if api_card is None:
                error_message += f"\n Card: {failed_printing_id.card_id}"
            else:
                error_message += f"\n Print: {failed_printing_id}. "
                error_message += f"\n   Available printings: {', '.join([str(p.printing_id()) for p in api_card.card_printings])}"

        raise UnidentifiedCardError(error_message)
    return printing_id_to_count