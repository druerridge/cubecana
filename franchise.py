import csv
import id_helper

# only works for The Double Feature Cube, move to a loadable file
franchise_to_draftmancer_color =  {
    "Peter Pan": "W",
    "Moana": "B",
    "The Little Mermaid": "G",
    "Aladdin": "R",
    "Mickey & Friends": None,
    "Beauty and the Beast": "U"
}

def load_id_to_franchise() -> dict:
    id_to_franchise = {}
    # only had characters for the double feature cube. expand to all cards
    card_by_franchise_file = 'inputs\\The Double Feature Cube - CardByFranchise.csv'
    with open(card_by_franchise_file, newline='', encoding='utf8') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        dialect.quoting = csv.QUOTE_MINIMAL
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            id_to_franchise[id_helper.to_id(row['Card Name'])] = row['Franchise']
    return id_to_franchise

def retrieve_franchise_to_draftmancer_color(id: str) -> str:
    id_to_franchise = load_id_to_franchise()
    franchise = id_to_franchise[id]
    return franchise_to_draftmancer_color[franchise]
