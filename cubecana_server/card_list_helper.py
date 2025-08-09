from collections import defaultdict
from . import id_helper
from .lcc_error import LccError

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