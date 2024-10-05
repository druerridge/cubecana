from flask import Flask, render_template, request, Response
import json
import create_template
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/to-tabletop-sim.html')
def to_tabletop_sim():
  return render_template('to-tabletop-sim.html')

@app.route('/to-draftmancer.html')
def to_draftmancer():
  return render_template('to-draftmancer.html')


@app.route('/card-list-to-draftmancer/', methods=['POST'])
def card_list_to_draftmancer():
  data = request.get_data()
  json_data = json.loads(request.data)
  print(data)
  print(json_data)
  card_list = json_data['card_list']
  print("cardList")
  print(card_list)
  settings = {
    'boosters_per_player': 4,
    'card_list_name': "custom_cube",
    'cards_per_booster': 12,
    'set_card_colors': False,
    'color_balance_packs': False,
  }

  settings = create_template.Settings(
        boosters_per_player=4,
        card_list_name="custom_cube",
        cards_per_booster=12,
        set_card_colors=False,
        color_balance_packs=False
    )
  draftmancer_file = create_template.dreamborn_card_list_to_draftmancer(card_list, create_template.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  return draftmancer_file

@app.route('/dreamborn-to-draftmancer/', methods=['POST'])
def handle_dreamborn_to_draftmancer():
  data = request.get_data()
  json_data = json.loads(request.data)
  print(data)
  print(json_data)
  json_obj_tss_export = json.loads(json_data['dreamborn_export'])
  print("json_obj_tss_export")
  print(json_obj_tss_export)
  id_to_tts_card = create_template.generate_id_to_tts_card_from_json_obj(json_obj_tss_export)
  settings = {
    'boosters_per_player': 4,
    'card_list_name': "custom_cube",
    'cards_per_booster': 12,
    'set_card_colors': False,
    'color_balance_packs': False,
  }

  settings = create_template.Settings(
        boosters_per_player=4,
        card_list_name="custom_cube",
        cards_per_booster=12,
        set_card_colors=False,
        color_balance_packs=False
    )
  draftmancer_file = create_template.dreamborn_tts_to_draftmancer(id_to_tts_card, create_template.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  return draftmancer_file

@app.route('/draftmancer-to-tts/', methods=['POST'])
def process_json():
  print("request")
  data = request.get_data()
  json_data = json.loads(request.data)
  print(data)
  print(json_data)

  lines = json_data['draftmancer_export'].split('\n')
  count_by_name = create_template.id_to_count_from(lines)
  id_to_custom_card = create_template.read_draftmancer_custom_cardlist()
  tts_deck = create_template.generate_tts_deck(count_by_name, id_to_custom_card)

  return json.dumps(tts_deck)

@app.errorhandler(create_template.UnidentifiedCardError)
def handle_foo_exception(error):
    response = Response(error.message, 404)
    return response