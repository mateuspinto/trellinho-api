from flask import Flask, request, g, session, Response
import json
import sqlite3
from hashlib import md5
from flask_cors import CORS

DATABASE_FILENAME = 'trellinho.sqlite3'
APP = Flask(__name__)
APP.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(APP, supports_credentials=True)


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
        return {'error': 1, 'error_message': 'Erro! Email já cadastrado!'}
    else:
        DB_CUR.execute(f'INSERT INTO user VALUES ("{request.form["email"]}", "{md5(request.form["password"].encode()).hexdigest()}", "{request.form["security_question"]}", "{md5(request.form["security_answer"].encode()).hexdigest()}", "{request.form["name"]}", {int(request.form["birthday_day"])}, {int(request.form["birthday_month"])}, {int(request.form["birthday_year"])})')
        get_database().commit()
        return {'error': 0}


@APP.route('/user/login', methods=['POST'])
def user__login():
    DB_CUR = get_database().cursor()
    if 'email' in session:
        return {'error': 1, 'error_message': f'Erro! Já logado como {session["email"]}'}
    elif list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}" AND password="{md5(request.form["password"].encode()).hexdigest()}"'))[0][0] == 0:
        return {'error': 1, 'error_message': 'Erro! Email ou senha incorretos!'}
    else:
        session['email'] = request.form['email']
        return {'error': 0}


@APP.route('/user/logout', methods=['POST'])
def user__logout():
    if not 'email' in session:
        return {'error': 1, 'error_message': 'Erro! Impossível deslogar um usuario não logado!'}
    else:
        session.pop('email', None)
        return {'error': 0}


@APP.route('/user/get', methods=['POST'])
def user__get():
    DB_CUR = get_database().cursor()
    if not 'email' in session:
        return {'error': 1, 'error_message': 'Erro! Impossível conseguir informações de um usuário não logado!'}
    else:
        return {'error': 0, 'response': list({'email': x[0], 'name': x[1], 'birthday_day': x[2], 'birthday_month': x[3], 'birthday_year': x[4]} for x in DB_CUR.execute(f'SELECT email, name, birthday_day, birthday_month, birthday_year FROM user WHERE email="{session["email"]}"'))[0]}


@APP.route('/user/security/question', methods=['POST'])
def user__security__question():
    DB_CUR = get_database().cursor()
    if list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}"'))[0][0] == 0:
        return {'error': 1, 'error_message': 'Erro! Email não cadastrado!'}
    else:
        return {'error': 0, 'reponse': {'security_question': list(DB_CUR.execute(f'SELECT security_question FROM user WHERE email="{request.form["email"]}"'))}}


@APP.route('/user/security/answer', methods=['POST'])
def user__security__answer():
    DB_CUR = get_database().cursor()
    if list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}"'))[0][0] == 0:
        return {'error': 1, 'error_message': 'Erro! Email não cadastrado!'}
    elif list(DB_CUR.execute(f'SELECT COUNT(*) FROM user WHERE email="{request.form["email"]}" and security_answer="{md5(request.form["security_answer"].encode()).hexdigest()}"'))[0][0] == 0:
        return {'error': 1, 'error_message': 'Erro! Resposta de segurança incorreta!'}
    else:
        DB_CUR.execute(f'UPDATE user SET password="{md5(request.form["password"].encode()).hexdigest()}" WHERE email="{request.form["email"]}"')
        get_database().commit()
        return {'error': 0}


@APP.route('/task/register', methods=['POST'])
def task__register():
    DB_CUR = get_database().cursor()
    if not 'email' in session:
        return {'error': 1, 'error_message': 'Erro! Impossível cadastrar uma tarefa para um usuario não logado!'}
    else:
        DB_CUR.execute(f'INSERT INTO task (user_email, title, description, target_day, target_month, target_year, priority, status) VALUES ("{session["email"]}", "{request.form["title"]}", "{request.form["description"]}", {int(request.form["target_day"])}, {int(request.form["target_month"])}, {int(request.form["target_year"])}, {int(request.form["priority"])}, 0)')
        get_database().commit()
        return {'error': 0}


@APP.route('/task/get', methods=['POST'])
def task__get_all():
    DB_CUR = get_database().cursor()
    if not 'email' in session:
        return {'error': 1, 'error_message': 'Erro! Impossível cadastrar uma tarefa para um usuario não logado!'}
    else:
        return {'error': 0, 'reponse': {'tasks': list({'id': x[0], 'title': x[1], 'description': x[2], 'target_day': x[3], 'target_month': x[4], 'target_year': x[5], 'priority': x[6], 'status': x[7]} for x in list(DB_CUR.execute(f'SELECT id, title, description, target_day, target_month, target_year, priority, status FROM task WHERE user_email="{session["email"]}"')))}}


@APP.route('/task/delete', methods=['POST'])
def task__delete():
    DB_CUR = get_database().cursor()
    if not 'email' in session:
        return {'error': 1, 'error_message': 'Erro! Impossível remover uma tarefa de um usuario não logado!'}
    elif list(DB_CUR.execute(f'SELECT COUNT(*) FROM task WHERE id={request.form["id"]} AND user_email="{session["email"]}"'))[0][0] == 0:
        return {'error': 1, 'error_message': 'Erro! Não há tarefa com esse ID!'}
    else:
        DB_CUR.execute(f'DELETE FROM task WHERE id={int(request.form["id"])} AND user_email="{session["email"]}"')
        get_database().commit()
        return {'error': 0}


@APP.route('/task/status/set', methods=['POST'])
def task__set_status():
    DB_CUR = get_database().cursor()
    if not 'email' in session:
        return {'error': 1, 'error_message': 'Erro! Impossível modificar a prioridade de uma tarefa de um usuario não logado!'}
    elif list(DB_CUR.execute(f'SELECT COUNT(*) FROM task WHERE id={request.form["id"]} AND user_email="{session["email"]}"'))[0][0] == 0:
        return {'error': 1, 'error_message': 'Erro! Não há tarefa com esse ID!'}
    else:
        DB_CUR.execute(f'UPDATE task SET status={int(request.form["status"])} WHERE id={int(request.form["id"])} AND user_email="{session["email"]}"')
        get_database().commit()
        return {'error': 0}


@APP.route('/', methods=['GET', 'POST'])
def index():
    return {'error': 0, 'response': {'session': dict(session)}}


if __name__ == '__main__':
    APP.run('localhost', port=8080)
