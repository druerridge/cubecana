from flask import Flask, render_template, request, Response, send_from_directory
import json
import create_template
import pixelborn
import lcc_error
from settings import Settings
from cube_manager import CubecanaCube
from cube_manager import cube_manager
import api
app = Flask(__name__)

MAX_CARD_LIST_LENGTH = 80000

# USER FACING PAGES

@app.route('/')
def serve_index():
  return render_template('index.html')

@app.route('/play')
def serve_play():
  return render_template('play.html')

@app.route('/disclaimer')
def serve_disclaimer():
  return render_template('disclaimer.html')

@app.route('/cubes')
def serve_cubes():
  return render_template('cubes.html')

@app.route('/add-cube/')
def serve_add_cube():
  return render_template('add-cube.html')

@app.route('/edit-cube/<string:cube_id>')
def serve_edit_cube(cube_id):
  return render_template('add-cube.html')

@app.route('/loading')
def serve_loading():
  return render_template('loading.html')

@app.route('/draft')
def serve_draft():
  return render_template('draft.html')

@app.route('/cube/<string:cube_id>/draft', methods=['GET'])
def serve_loading_draft(cube_id):
  return render_template('loading-draft.html')

@app.route('/sitemap.xml')
def serve_sitemap():
    return send_from_directory('static', 'sitemap.xml')

# API Endpoints

@app.route('/api/draftmancer-to-inktable/', methods=['POST'])
def draftmancer_to_inktable():
  data = request.get_data()
  json_data = json.loads(request.data)
  all_lines = json_data['draftmancer_export'].split('\n')
  mainboard_lines = create_template.get_mainboard_lines(all_lines)
  id_to_count = create_template.id_to_count_from(mainboard_lines)
  pixelborn_deck = pixelborn.generate_pixelborn_deck(id_to_count)
  return pixelborn.inktable_import_link(pixelborn_deck)

@app.route('/api/draftmancer-to-tts/', methods=['POST'])
def process_json():
  data = request.get_data()
  json_data = json.loads(request.data)

  all_lines = json_data['draftmancer_export'].split('\n')
  mainboard_lines = create_template.get_mainboard_lines(all_lines)
  id_to_count = create_template.id_to_count_from(mainboard_lines)
  id_to_custom_card = create_template.read_draftmancer_custom_cardlist()
  tts_deck = create_template.generate_tts_deck(id_to_count, id_to_custom_card)

  return json.dumps(tts_deck)

@app.route('/api/card-list-to-draftmancer/', methods=['POST'])
def card_list_to_draftmancer():
  data = request.get_data()
  json_data = json.loads(request.data)
  card_list = json_data['card_list']
  settings_input = json_data['settings']

  card_list_lines = card_list.split('\n')
  id_to_count_input = create_template.id_to_count_from(card_list_lines)
  card_count = 0
  [card_count := card_count + count for count in id_to_count_input.values()]

  settings = Settings(
        boosters_per_player=settings_input.get('boosters_per_player', 4),
        card_list_name="custom_cube",
        cards_per_booster=settings_input.get('cards_per_booster', 12),
        set_card_colors=False,
        color_balance_packs=False
    )
  draftmancer_file = create_template.dreamborn_card_list_to_draftmancer(card_list, create_template.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  response = {'draftmancerFile': draftmancer_file, 'metadata': {'cardCount': card_count, 'cardsPerBooster': settings.cards_per_booster, 'boostersPerPlayer': settings.boosters_per_player}}
  return json.dumps(response)

@app.route('/api/dreamborn-to-draftmancer/', methods=['POST'])
def handle_dreamborn_to_draftmancer():
  json_data = json.loads(request.data)
  json_obj_tss_export = json.loads(json_data['dreamborn_export'])
  settings_input = json_data['settings']
  id_to_tts_card = create_template.generate_id_to_tts_card_from_json_obj(json_obj_tss_export)
  card_count = 0
  [card_count := card_count + card['count'] for card in id_to_tts_card.values()]
  settings = Settings(
        boosters_per_player=settings_input.get('boosters_per_player', 4),
        card_list_name="custom_cube",
        cards_per_booster=settings_input.get('cards_per_booster', 12),
        set_card_colors=False,
        color_balance_packs=False
    )
  draftmancer_file = create_template.dreamborn_tts_to_draftmancer(id_to_tts_card, create_template.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  response = {'draftmancerFile': draftmancer_file, 'metadata': {'cardCount': card_count, 'cardsPerBooster': settings.cards_per_booster, 'boostersPerPlayer': settings.boosters_per_player}}
  return json.dumps(response)

# CUBE API ENDPOINTS

@app.route('/api/cube', methods=['GET'])
def get_cubes():
  page = int(request.args.get('page', 1))
  per_page = int(request.args.get('per_page', 10))
  paginated_cube_list_entries = cube_manager.get_cubes(page, per_page)
  return paginated_cube_list_entries

@app.route('/api/cube', methods=['POST'])
def add_cube():
  if len(request.json['cardListText']) > MAX_CARD_LIST_LENGTH:
    return Response(status=413)
  api_create_cube = api.CreateCubeRequest(
    name=request.json['name'],
    cardListText=request.json['cardListText'],
    tags=request.json['tags'],
    link=request.json['link'],
    author=request.json['author'],
    cubeSettings=api.CubeSettings(**request.json['cubeSettings'])
  )
  cubecana_cube = cube_manager.create_cube(api_create_cube)
  response = {'id': cubecana_cube.id,'editCubeLink': f'/edit-cube/{cubecana_cube.id}?editSecret={cubecana_cube.edit_secret}'}
  return json.dumps(response), 201

@app.route('/api/cube/<string:cube_id>/draftmancerFile', methods=['GET'])
def get_cube_draftmancer_file(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    return Response(status=404)
  draftmancer_file: str = create_template.add_card_list_to_draftmancer_custom_cards(cube.card_id_to_count, "incomplete_simple_template.draftmancer.txt", cube.settings)
  response = {'draftmancerFile': draftmancer_file, 'metadata': {'cardCount': cube.card_count(), 'cardsPerBooster': cube.settings.cards_per_booster, 'boostersPerPlayer': cube.settings.boosters_per_player}}
  return json.dumps(response)

@app.route('/api/cube/<string:cube_id>', methods=['GET'])
def get_cube(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    return Response(status=404)
  api_cube = cube.to_api_cube()
  return api_cube.toJSON()

@app.route('/api/cube/<string:cube_id>', methods=['PUT'])
def update_cube(cube_id):
  cube = cube_manager.get_cube(request.json['id'])
  if not cube:
    return Response(status=404)
  if len(request.json['cardListText']) > MAX_CARD_LIST_LENGTH:
    return Response(status=413)
  if request.args.get('editSecret') != cube.edit_secret:
    return Response(status=401)
  api_edit_cube = api.EditCubeRequest(
    id=request.json['id'],
    name=request.json['name'],
    cardListText=request.json['cardListText'],
    tags=request.json['tags'],
    link=request.json['link'],
    author=request.json['author'],
    cubeSettings=api.CubeSettings(**request.json['cubeSettings'])
  )
  updated_cube: CubecanaCube = cube_manager.update_cube(api_edit_cube)
  response = {'id': updated_cube.id,'editCubeLink': f'/edit-cube/{updated_cube.id}?editSecret={updated_cube.edit_secret}'}
  return json.dumps(response), 201

# can't delete cubes w/o Accounts
# @app.route('/api/cubes/<string:cube_id>', methods=['DELETE'])
# def delete_cube(cube_id):
#   cube = cubes.get(cube_id)
#   if cube:
#     cubes.remove(cube_id)
#     return json.dumps(cube)
#   else:
#     return Response(status=404)

@app.errorhandler(lcc_error.LccError)
def handle_foo_exception(error):
    user_facing_lcc_error = {
        "lcc_error": True,
        "user_facing_message": error.user_facing_message,
    }
    response = Response(json.dumps(user_facing_lcc_error), error.http_status_code, content_type="application/json")
    return response