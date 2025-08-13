import re

pattern = re.compile(r"[\W_]+", re.ASCII)
def to_id(string):
    string = string.replace('ā', 'a')
    string = string.replace('é','e')
    return re.sub(pattern, '', string).lower()