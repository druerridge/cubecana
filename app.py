from flask import Flask, render_template, request, Response, send_from_directory, redirect
import json
import create_template
import pixelborn
import lcc_error
import card_evaluations
from settings import Settings
from cube_manager import CubecanaCube
from cube_manager import cube_manager
from retail_manager import retail_manager
import api
from flask import jsonify
from cube_dao import MAX_CARD_LIST_LENGTH
app = Flask(__name__)

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

@app.route('/cube-directory')
def serve_cubes():
  return render_template('cube-directory.html')

@app.route('/retail-directory')
def serve_retail_sets():
  return render_template('retail-directory.html')

@app.route('/add-cube/')
def serve_add_cube():
  return render_template('add-cube.html')

@app.route('/edit-cube/<string:cube_id>')
def serve_edit_cube(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    raise lcc_error.CubeNotFoundError("Cube not found")
  if request.args.get('editSecret') != cube.edit_secret:
    raise lcc_error.UnauthorizedError("Edit secret is incorrect")
  return render_template('edit-cube.html')

@app.route('/loading')
def serve_loading():
  return render_template('loading.html')

@app.route('/draft')
def serve_draft():
  return render_template('draft.html')

@app.route('/cube/<string:cube_id>/draft', methods=['GET'])
def serve_loading_draft(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    raise lcc_error.CubeNotFoundError("Cube not found")
  cube_manager.increment_page_views(cube_id)
  return render_template('loading-draft.html')

@app.route('/cube/<string:cube_id>/inspect-list', methods=['GET'])
def serve_inspect_list(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    raise lcc_error.CubeNotFoundError("Cube not found")
  cube_manager.increment_card_list_views(cube_id)
  return redirect(cube.link)

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

  create_template.validate_card_list_against(card_list)

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
  draftmancer_file = create_template.dreamborn_card_list_to_draftmancer(card_list, card_evaluations.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  response = {
    'draftmancerFile': draftmancer_file, 
    'metadata': {
      'cardCount': card_count, 
      'cardsPerBooster': settings.cards_per_booster, 
      'boostersPerPlayer': settings.boosters_per_player, 
      'cubeName': settings.card_list_name
    }
  }
  return jsonify(response)

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
  draftmancer_file = create_template.dreamborn_tts_to_draftmancer(id_to_tts_card, card_evaluations.DEFAULT_CARD_EVALUATIONS_FILE, settings)
  response = {'draftmancerFile': draftmancer_file, 'metadata': {'cardCount': card_count, 'cardsPerBooster': settings.cards_per_booster, 'boostersPerPlayer': settings.boosters_per_player}}
  return jsonify(response)

# RETAIL API ENDPOINTS

@app.route('/api/retail_sets', methods=['GET'])
def get_retail_sets():
  page = int(request.args.get('page', 1))
  per_page = min(int(request.args.get('per_page', 10)), 100)
  order = request.args.get('order', api.OrderType.DESC)
  paginated_retail_set_entries = retail_manager.get_sets(page, per_page, order)
  response = {'sets': paginated_retail_set_entries, 'totalSets': retail_manager.get_set_count()}
  return jsonify(response)

@app.route('/api/retail_sets/<string:set_id>', methods=['GET'])
def get_retail_set(set_id:str):
  set = retail_manager.get_set(set_id)
  if not set:
    return lcc_error.RetailSetNotFoundError("Retail set not found")
  return jsonify(set)

@app.route('/api/retail_sets/<string:set_id>/draftmancerFile', methods=['GET'])
def get_retail_set_draftmancer_file(set_id:str):
  set: api.RetailSet = retail_manager.get_set(set_id)
  if not set:
    return lcc_error.RetailSetNotFoundError("Retail set not found")
  response = {
    'draftmancerFile': set.draftmancerFile, 
    'metadata': {
      'cardCount': 4 * 12 * 8, 
      'cardsPerBooster': 12, 
      'boostersPerPlayer': 4, 
      'cubeName': set.name, 
      'link': f"https://www.cubecana.com//api/retail_sets/{set_id}",
      'author': "Ravensburger"}}
  return jsonify(response)

# CUBE API ENDPOINTS

@app.route('/api/cube/count', methods=['GET'])
def get_cube_count():
  return jsonify({'count': cube_manager.get_cube_count()})

@app.route('/api/cube', methods=['GET'])
def get_cubes():
  page = int(request.args.get('page', 1))
  per_page = min(int(request.args.get('per_page', 10)), 100)
  sort = request.args.get('sort', api.SortType.RANK)
  order = request.args.get('order', api.OrderType.DESC)
  paginated_cube_list_entries = cube_manager.get_cubes(page, per_page, sort, order)
  response = {'cubes': paginated_cube_list_entries, 'totalCubes': cube_manager.get_cube_count()}
  return jsonify(response)

@app.route('/api/cube', methods=['POST'])
def add_cube():
  if len(request.json['cardListText']) == 0:
    return Response(status=400)
  if len(request.json['cardListText']) > MAX_CARD_LIST_LENGTH:
    return Response(status=413)
  create_template.validate_card_list_against(request.json['cardListText'])
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
  return jsonify(response)

@app.route('/api/cube/<string:cube_id>/draftmancerFile', methods=['GET'])
def get_cube_draftmancer_file(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    return Response(status=404)
  draftmancer_file: str = create_template.generate_draftmancer_file_from_cube(cube)
  response = {
    'draftmancerFile': draftmancer_file, 
    'metadata': {
      'cardCount': cube.card_count(), 
      'cardsPerBooster': cube.settings.cards_per_booster, 
      'boostersPerPlayer': cube.settings.boosters_per_player, 
      'cubeName': cube.name, 
      'link': cube.link,
      'author': cube.author}}
  cube_manager.increment_drafts(cube_id)
  return jsonify(response)

@app.route('/api/cube/<string:cube_id>', methods=['GET'])
def get_cube(cube_id):
  cube: CubecanaCube = cube_manager.get_cube(cube_id)
  if not cube:
    return Response(status=404)
  api_cube = cube.to_api_cube()
  r = api_cube.__dict__
  r['cubeSettings'] = r['cubeSettings'].__dict__
  return jsonify(r)

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
  return jsonify(response)

@app.route('/api/cube/<string:cube_id>', methods=['DELETE'])
def delete_cube(cube_id):
  cube = cube_manager.get_cube(cube_id)
  if not cube:
    return Response(status=404)
  edit_secret = request.args.get('editSecret')
  if edit_secret != cube.edit_secret:
    return Response(status=401)
  if not cube_manager.delete_cube(cube_id, edit_secret):
    return Response(401)
  return Response(status=200)

@app.errorhandler(lcc_error.UnauthorizedError)
def handle_401_exception(error):
  return render_template('401.html'), error.http_status_code

@app.errorhandler(lcc_error.CubeNotFoundError)
def handle_404_exception(error):
  return render_template('404.html'), error.http_status_code

@app.errorhandler(lcc_error.LccError)
def handle_foo_exception(error):
    user_facing_lcc_error = {
        "lcc_error": True,
        "user_facing_message": error.user_facing_message,
    }
    response = Response(json.dumps(user_facing_lcc_error), error.http_status_code, content_type="application/json")
    return response