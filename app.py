from flask import Flask, render_template, request, Response
import json
import create_template
import pixelborn
import lcc_error
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/play.html')
def to_tabletop_sim():
  return render_template('play.html')

@app.route('/disclaimer')
def disclaimer():
  return render_template('disclaimer.html')

@app.route('/draft.html')
def to_draftmancer():
  return render_template('draft.html')

@app.route('/draftmancer-to-inktable/', methods=['POST'])
def draftmancer_to_inktable():
  data = request.get_data()
  json_data = json.loads(request.data)
  all_lines = json_data['draftmancer_export'].split('\n')
  mainboard_lines = create_template.get_mainboard_lines(all_lines)
  id_to_count = create_template.id_to_count_from(mainboard_lines)
  pixelborn_deck = pixelborn.generate_pixelborn_deck(id_to_count)
  return pixelborn.inktable_import_link(pixelborn_deck)

@app.route('/draftmancer-to-tts/', methods=['POST'])
def process_json():
  data = request.get_data()
  json_data = json.loads(request.data)

  all_lines = json_data['draftmancer_export'].split('\n')
  mainboard_lines = create_template.get_mainboard_lines(all_lines)
  id_to_count = create_template.id_to_count_from(mainboard_lines)
  id_to_custom_card = create_template.read_draftmancer_custom_cardlist()
  tts_deck = create_template.generate_tts_deck(id_to_count, id_to_custom_card)

  return json.dumps(tts_deck)


@app.route('/card-list-to-draftmancer/', methods=['POST'])
def card_list_to_draftmancer():
  data = request.get_data()
  json_data = json.loads(request.data)
  card_list = json_data['card_list']
  settings_input = json_data['settings']

  settings = create_template.Settings(
        boosters_per_player=4,
        card_list_name="custom_cube",
        cards_per_booster=settings_input['cards_per_booster'],
        set_card_colors=False,
        color_balance_packs=False
    )
  draftmancer_file = create_template.dreamborn_card_list_to_draftmancer(card_list, create_template.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  return draftmancer_file

@app.route('/dreamborn-to-draftmancer/', methods=['POST'])
def handle_dreamborn_to_draftmancer():
  json_data = json.loads(request.data)
  json_obj_tss_export = json.loads(json_data['dreamborn_export'])
  settings_input = json_data['settings']
  id_to_tts_card = create_template.generate_id_to_tts_card_from_json_obj(json_obj_tss_export)

  settings = create_template.Settings(
        boosters_per_player=4,
        card_list_name="custom_cube",
        cards_per_booster=settings_input['cards_per_booster'],
        set_card_colors=False,
        color_balance_packs=False
    )
  draftmancer_file = create_template.dreamborn_tts_to_draftmancer(id_to_tts_card, create_template.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  return draftmancer_file

@app.errorhandler(lcc_error.LccError)
def handle_foo_exception(error):
    user_facing_lcc_error = {
        "lcc_error": True,
        "user_facing_message": error.user_facing_message,
    }
    response = Response(json.dumps(user_facing_lcc_error), error.http_status_code, content_type="application/json")
    return response