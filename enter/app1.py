from flask import Flask, jsonify, request
from sqlite3 import connect, Error
from hashlib import sha256
import re
import jwt
import datetime

# создаём объект приложения (наследуя Flask)
app1 = Flask(__name__)
db_lp1 = connect(r'databases/users.db', check_same_thread=False)
cursor_db1 = db_lp1.cursor()


regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


def is_email_valid(email):
    return re.fullmatch(regex, email)


def get_hash(word):
    return sha256(word.encode('utf-8')).hexdigest()


@app1.route('/', methods=['GET'])
def greeting():
    # приветствуем пользователя на микросервисе авторизации
    return jsonify({'answer': 'Добро пожаловать на сервис авторизации.'}), 200


@app1.route('/registration', methods=['POST'])
def registration():
    # функция для регистрации пользователя
    info = request.get_json()
    try:
        username, password = info['username'], info['password']
        email, role = info['email'], info['role']
    except (TypeError, ValueError, SyntaxError):
        return jsonify({'answer': 'Увы, либо не все поля заполнены, либо заполнены некорректно :(\n Повторите попытку'}), 400
    # проверяем email на валидность
    if not is_email_valid(email):
        return jsonify({'answer': 'Увы, адрес электронной почты некорректен :(\n Повторите попытку.'}), 400
    # хэшируем пароль
    password_hash = get_hash(password)
    # пытаемся добавить данные о новом пользователе в БД
    try:
        sql_query = f'''SELECT * FROM user WHERE email = "{email}"'''
        cursor_db1.execute(sql_query)
        records = cursor_db1.fetchall()
        if len(records):
            return jsonify({'answer': 'Ого, так Вы уже зарегистpированы!'}), 403
        sql_insert = '''INSERT INTO user (username, email, password_hash, role) VALUES (?, ?, ?, ?)'''
        cursor_db1.execute(sql_insert,  (username, email, password_hash, role))
        db_lp1.commit()
        return jsonify({'answer': 'Ура, регистрация прошла успешно!'}), 200
    except Error:
        return jsonify({'answer': 'Увы, Вас не удалось зарегистрировать :(\n Повторите попытку.'}), 400


@app1.route('/authorization', methods=['POST'])
def authorization():
    # авторизуем пользователя
    info = request.get_json()
    try:
        email, password = info['email'], info['password']
    except (TypeError, ValueError, SyntaxError):
        return jsonify({'answer': 'Увы, либо не все поля заполнены, либо заполнены некорректно :(\n Повторите попытку'}), 400
    try:
        sql_query = f'''SELECT * FROM user WHERE email = {email}'''
        cursor_db1.execute(sql_query)
        user = cursor_db1.fetchone()
        if user and user[3] == get_hash(password):
            user_id = user[0]
            token_secret = 'got-a-secret-can-you-keep-it-swear-this-one-you-ll-save-better-lock-it-in-your-pocket'
            # генерируем "session jwt token", используемый для аутентификации
            session_jwt_token = jwt.encode(payload=info, secret=token_secret, algorithm='HS256')
            # продлеваем срок действия сеанса на один день
            expires_at = str(datetime.datetime.now() + datetime.timedelta(days=1))
            sql_insert = '''INSERT INTO session (user_id, session_token, expires_at) VALUES (?, ?, ?)'''
            cursor_db1.execute(sql_insert,  (user_id, session_jwt_token, expires_at))
            db_lp1.commit()
            return jsonify({'answer': 'Ура, авторизация прошла успешно!'}), 200
        else:
            return jsonify({'answer': 'Увы, почта или пароль введены неверно :(\n Повторите попытку.'}), 401
    except Error:
        return jsonify({'answer': 'Увы, Вас не удалось авторизовать :(\n Повторите попытку.'}), 401


@app1.route('/user', methods=['GET'])
def user_info():
    # выдаём информацию о пользователе по токену
    token = request.headers.get('Authorization')
    sql_query = '''
    SELECT curr_u.id, curr_u.username, curr_u.email, curr_u.role, curr_u.created_at
    FROM user curr_u
    INNER JOIN session curr_s ON curr_s.user_id = curr_u.id
    WHERE curr_s.session_token = ? AND CURRENT TIMESTAMP < curr_s.expires_at
    '''
    cursor_db1.execute(sql_query, (token, ))
    user = cursor_db1.fetchone()
    if not user:
        return jsonify({'error': 'Увы, не удаётся найти информацию о Вас :('}), 404
    info = {'id': user[0], 'username': user[1], 'email': user[2], 'role': user[3], 'created_at': user[4]}
    return jsonify(info), 200


@app1.errorhandler(404)
def page_not_found():
    return jsonify({'error': 'Увы, страница не найдена :('}), 404


if __name__ == '__main__':
    # create_db1.create_database1()
    app1.run(debug=True, port=5000, host="127.0.0.1")  # убрать потом debug=True
    cursor_db1.close()
    db_lp1.close()
