from flask import Flask, render_template, request
import json
import create_template
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/draftmancer-to-tts/', methods=['POST'])
def process_json():
    print("request")
    data = request.get_data()
    json_data = json.loads(request.data)
    print(data)
    print(json_data)

    lines = json_data['draftmancer_export'].split('\n')
    count_by_name = create_template.count_by_name_from(lines)
    id_to_custom_card = create_template.read_draftmancer_custom_cardlist()
    tts_deck = create_template.generate_tts_deck(count_by_name, id_to_custom_card)

    return json.dumps(tts_deck)

# @app.route('/draftmancer-to-tts/')
# def draftmancer_to_tts():
  
#   print('I got clicked!')
#   return 'Click.'

if __name__ == '__main__':
  app.run(debug=True)