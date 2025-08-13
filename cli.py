import argparse
from cubecana_server import draftmancer
from cubecana_server import tabletop_simulator
from cubecana_server import generate_retail
from cubecana_server import card_evaluations
from cubecana_server.settings import Settings, POWER_BAND_RETAIL


parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='given a dreamborn \"deck\" of a cube / set / card list, exported in Tabletop Simulator format, create a draftmancer custom card list that can be uploaded and drafted on draftmancer.com',
                    epilog='Text at the bottom of help')

parser.add_argument('verb', help="verb is one of: ( retail_tts_to_draftmancer | tts_to_draftmancer | draftmancer_to_tts )")
parser.add_argument('--dreamborn_export_for_tabletop_sim', help="file path to a .deck export in Tabletop Sim format from dreamborn.ink deck of the cube e.g. example-cube.json or C:\\Users\\dru\\Desktop\\deck.json")
parser.add_argument('--card_evaluations_file', default=card_evaluations.DEFAULT_CARD_EVALUATIONS_FILE, help="relative path to a .csv file containing card name -> 0-5 card rating (power in a vacuum). default: \"DraftBots\\\\FrankKarstenEvaluations-HighPower.csv\"")
parser.add_argument('--boosters_per_player', default=4)
parser.add_argument('--cards_per_booster', default=12)
parser.add_argument('--name', default="custom_card_list", help="Sets name of both the output file and the set/cube list as it appears in draftmancer")
parser.add_argument('--set_card_colors', default=False, help="WARNING** This sets card colors, allowing draftmancer to do color-balancing for you, but it will also encourage bots to draft 1-2 color decks")
parser.add_argument('--color_balance_packs', default=False, help="WARNING** this color-balances ONLY your largest slot, IF it contains enough cards, AND steel may be wonky (treated as colorless). This will ONLY work if card_colors is true, which will encourage bots to draft 1-2 color decks")
parser.add_argument('--franchise_to_color', default=False, help="sets colors based on franchise to enable a double-feature cube")
parser.add_argument('--set_card_types', default=False, help="WARNING** This sets card types... it may affect bots... but I don't know")
parser.add_argument('--set_code', default=None, help="This is required to generate a true retail draft set, but could be left blank to generate retail-like sets")

def retail_tts_to_draftmancer(dreamborn_export_for_tabletop_sim, card_evaluations_file, set_code:str, settings:Settings):
    settings.with_replacement = True
    settings.power_band = POWER_BAND_RETAIL
    id_to_tts_card = tabletop_simulator.read_id_to_tts_card_from_filesystem(dreamborn_export_for_tabletop_sim)
    draftmancer_file_contents = generate_retail.generate_retail_draftmancer_file(id_to_tts_card, card_evaluations_file, set_code, settings)
    draftmancer.write_draftmancer_file(draftmancer_file_contents, settings.card_list_name)

def tts_to_draftmancer(dreamborn_export_for_tabletop_sim, card_evaluations_file, settings:Settings):
    draftmancer_file_contents = draftmancer.dreamborn_tts_to_draftmancer_from_file(dreamborn_export_for_tabletop_sim, card_evaluations_file, settings)
    draftmancer.write_draftmancer_file(draftmancer_file_contents, settings.card_list_name)

if __name__ == '__main__':
    args = parser.parse_args()

    settings = Settings(
        boosters_per_player=args.boosters_per_player,
        card_list_name=args.name,
        cards_per_booster=args.cards_per_booster,
        set_card_colors=args.set_card_colors,
        color_balance_packs=args.color_balance_packs,
        with_replacement=False,
        franchise_to_color=args.franchise_to_color,
        set_card_types=args.set_card_types
    )

    match args.verb:
        case "retail_tts_to_draftmancer":
            retail_tts_to_draftmancer(args.dreamborn_export_for_tabletop_sim, args.card_evaluations_file, args.set_code, settings)
        case "tts_to_draftmancer":
            tts_to_draftmancer(args.dreamborn_export_for_tabletop_sim, args.card_evaluations_file, settings)
        case _:
            raise SystemExit(1, f"no verb '{args.verb}' found, exiting")