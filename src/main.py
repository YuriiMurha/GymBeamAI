
from flask import Flask, render_template, request
from model import Model


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    return render_template('index.html', result=model.get_response(request.form['prompt']))

if __name__ == '__main__':
    model = Model()
    app.run()