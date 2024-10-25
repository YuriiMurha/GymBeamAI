from flask import Flask, render_template, request, stream_with_context, Response
from model import Model
from waitress import serve
from flask_cors import CORS

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

if __name__ == '__main__':
    model = Model()
    # serve(app, host='127.0.0.1', port=5000)
    app.run(host="127.0.0.1", port=5000)