import re

pattern = re.compile(r"[\W_]+", re.ASCII)
def to_id(string):
    string = string.replace('ā', 'a')
    string = string.replace('é','e')
    return re.sub(pattern, '', string).lower()

def canonical_name_from_id(id, id_to_dreamborn_name, id_to_tts_card):
    # IMPORTANT dreamborn names are canonical to enable import / export to / from dreamborn.ink (which subsequently enables deck export to inktable.net + Tabletop Simulator)
    # dreamborn plain export is the best name for our custom card list, enabling all import / export and hand-editing of the card list (e.g. simple_template.draftmancer.txt)
    # UPDATE INSTRUCTIONS: dreamborn.ink > Collection > export > copy-paste the "Name" column w/o the header row
    cannonical_name = id_to_dreamborn_name.get(id, None) 
    
    # dreamborn TTS export is the second best name
    # this enables us to generate cubes with cards we haven't exported yet in all_dreamborn_names.txt, and import / export from dreamborn
    # HOWEVER, hand-editing the booster slot(s) after generation has edge cases, e.g. card names are missing apostrophes (') in custom card list, so they won't match
    # therefore this method is not suitable to generate simple_template.draftmancer.txt which is meant to have the booster slot(s) "hand-edited"
    if cannonical_name is None: 
        cannonical_name = id_to_tts_card[id]['name']
    return cannonical_name