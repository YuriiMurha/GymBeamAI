from flask import Flask, render_template, request, stream_with_context, Response, redirect, url_for, session, jsonify
from model import Model
from waitress import serve
from flask_cors import CORS
import json

app = Flask(__name__, static_folder='./static')
CORS(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    @stream_with_context
    def generate_response():
        prompt = request.form['prompt']
        for response_chunk in model.get_response_stream(prompt):
            yield response_chunk
    return Response(generate_response(), content_type='text/event-stream')

# Сторінка дашборду з опитуванням та GymBeam Assistant
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Обробка опитування про здоров'я
@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    """
    Save survey info to model's message history and return success status.
    """
    survey_data = request.form.to_dict()
    print("Survey completed:", survey_data)
    
    model.save_to_csv(survey_data)
    
    data_string = ','.join(f'{key}={value}' for key, value in survey_data.items())
    model.add_survey_data(data_string)
    
    return render_template('index.html')

if __name__ == '__main__':
    # Read JSON file
    with open(r'./src/data/products/gymbeam_products_supplements.json', encoding='utf-8') as f:
        data = json.load(f)[:40]
    model = Model(data.__str__())
    # serve(app, host='127.0.0.1', port=5000)
    app.run(host="127.0.0.1", port=5000)