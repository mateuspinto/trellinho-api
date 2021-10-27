from flask import Flask, request, g, session, Response
import json
import sqlite3
from hashlib import md5

DATABASE_FILENAME = 'trellinho.sqlite3'
APP = Flask(__name__)
APP.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def get_database():
    DATABASE = getattr(g, '_database', None)
    if DATABASE is None:
        DATABASE = g._database = sqlite3.connect(DATABASE_FILENAME)
    return DATABASE


@APP.teardown_appcontext
def close_connection(_):
    DATABASE = getattr(g, '_database', None)
    if DATABASE is not None:
        DATABASE.close()


@APP.route('/user/register', methods=['POST'])
def user__register():
    DB_CUR = get_database().cursor()
    if list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}"'))[0][0] == 1:
        return json.dumps({'info': 'Email ja cadastrado!'}), 500, {'ContentType': 'application/json'}
    else:
        DB_CUR.execute(f'INSERT INTO user VALUES ("{request.form["email"]}", "{md5(request.form["password"].encode()).hexdigest()}", "{request.form["security_question"]}", "{md5(request.form["security_answer"].encode()).hexdigest()}", "{request.form["name"]}", {int(request.form["birthday_day"])}, {int(request.form["birthday_month"])}, {int(request.form["birthday_year"])})')
        get_database().commit()

        return json.dumps({'info': 'Cadastrado com sucesso!'}), 200, {'ContentType': 'application/json'}


@APP.route('/user/login', methods=['POST'])
def user__login():
    DB_CUR = get_database().cursor()
    if 'email' in session:
        return json.dumps({'info': f'Erro! Ja logado como {session["email"]}'}), 500, {'ContentType': 'application/json'}

    if list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}" AND password="{md5(request.form["password"].encode()).hexdigest()}"'))[0][0] == 1:
        session['email'] = request.form['email']
        return json.dumps({'info': 'Logado com sucesso!'}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'info': 'Erro! Email ou senha incorretos!'}), 500, {'ContentType': 'application/json'}


@APP.route('/user/logout', methods=['POST'])
def user__logout():
    if 'email' in session:
        session.pop('email', None)
        return json.dumps({'info': 'Deslogado com sucesso!'}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'info': 'Erro! Impossivel deslogar um usuario nao logado!'}), 500, {'ContentType': 'application/json'}


@APP.route('/user/security/question', methods=['POST'])
def user__security__question():
    DB_CUR = get_database().cursor()
    if list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}"'))[0][0] == 1:
        return json.dumps({'info': 'Questao recuperada com sucesso!', 'security_question': list(DB_CUR.execute(f'SELECT security_question FROM user WHERE email="{request.form["email"]}"'))[0][0]}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'info': 'Email ja cadastrado!'}), 500, {'ContentType': 'application/json'}


@APP.route('/', methods=['GET'])
def index():
    if 'email' in session:
        return json.dumps({'info': f'Logged in as {session["email"]}'}), 200, {'ContentType': 'application/json'}
    return json.dumps({'info': 'usuario nao encontrado'}), 500, {'ContentType': 'application/json'}


if __name__ == '__main__':
    APP.run('localhost', port=8080)
