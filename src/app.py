from flask import Flask, render_template, request, stream_with_context, Response, redirect, url_for, session, jsonify
from model import Model
from waitress import serve
from flask_cors import CORS

app = Flask(__name__, static_folder='./static')
CORS(app)

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
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
    if 'username' not in session:
        return redirect(url_for('index'))  # Якщо користувач не залогінений, перенаправити на головну сторінку
    return render_template('dashboard.html')

# Обробка входу
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    remember_me = request.form.get('rememberMe')

    # Перевіряємо, чи існує користувач
    user = next((user for user in users if user['username'] == username and user['password'] == password), None)

    if user:
        session['username'] = username
        if remember_me:
            session.permanent = True  # Запам'ятати сесію
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 400


# Обробка реєстрації
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirmPassword']
    terms_accepted = request.form.get('terms')

    # Перевіряємо правильність даних
    if username and password and confirm_password and terms_accepted:
        if password != confirm_password:
            return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
        if any(user['username'] == username for user in users):
            return jsonify({'status': 'error', 'message': 'User already exists'}), 400
        users.append({'username': username, 'password': password})
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Please fill in all fields and accept the terms'}), 400


# Обробка виходу з сесії
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# Обробка опитування про здоров'я
@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    """
    Save survey info to model's message history and redirect to index.
    """
    survey_data = request.form.to_dict().__str__
    print("Survey completed:", survey_data)

    model.add_survey_data(survey_data)
    
    return jsonify({'status': 'success'}), 200

# Тимчасове сховище користувачів
users = [{'username': 'admin', 'password': 'admin'}]

# Обробка помилки 404 (Сторінка не знайдена)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    model = Model()
    # serve(app, host='127.0.0.1', port=5000)
    app.run(host="127.0.0.1", port=5000)