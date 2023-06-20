from flask import Flask, jsonify, request
from sqlite3 import connect, Error
import datetime
import time

# создаём объект приложения (наследуя Flask)
app2 = Flask(__name__)
db_lp2 = connect(r'databases/dishes_orders.db', check_same_thread=False)
cursor_db2 = db_lp2.cursor()
db_lp1 = connect(r'databases/users.db', check_same_thread=False)
cursor_db1 = db_lp1.cursor()


def check_args_existence(data, args):
    for arg in args:
        if arg not in data or data[arg] == "":
            return {'answer': 'Увы, либо не все поля заполнены, либо заполнены некорректно :( Повторите попытку.'}
    return {'answer': 'ok'}


@app2.route('/', methods=['GET'])
def greeting():
    # приветствуем пользователя на микросервисе обработки заказов
    return jsonify({'answer': 'Добро пожаловать на сервис обработки заказов.'}), 200


@app2.route('/create_order', methods=['POST'])
def create_order():
    # функция для создания заказа пользователя
    info = request.get_json()
    is_ok = check_args_existence(info, ["user_id", "dishes", "special_requests"])
    if is_ok['answer'] != 'ok':
        return jsonify(is_ok)
    user_id, dishes, special_requests = info['user_id'], info['dishes'], info['special_requests']
    created_at = str(datetime.datetime.now())
    status = 'processing'
    # проверяем тип int у user_id
    if not user_id.isdigit():
        return jsonify({'answer': 'Увы, поле user_id может представлять из себя только положительное число...'})
    # проверяем существование пользователя с данным "user_id"
    sql_query = '''SELECT * FROM user WHERE id = ?'''
    cursor_db1.execute(sql_query, (user_id, ))
    user = cursor_db1.fetchone()
    if not user:
        return jsonify({'error': 'Увы, не удаётся найти информацию о Вас :('}), 404
    for dish in dishes:
        is_ok = check_args_existence(dish, ["id", "quantity"])
        if is_ok['answer'] != 'ok':
            return jsonify(is_ok)
        dish_id, dish_quantity = dish['id'], dish['quantity']
        if not dish_id.isdigit():
            return jsonify({'answer': 'Увы, поле dish_id может представлять из себя только положительное число...'})
        if not dish_quantity.isdigit():
            return jsonify({'answer': 'Увы, поле dish_quantity может представлять из себя только положительное число...'})
        dish_quantity = int(dish_quantity)
        # проверяем существование блюда с данным "dish_id"
        sql_query = '''SELECT * FROM dish WHERE id = ?'''
        cursor_db2.execute(sql_query, (dish_id, ))
        dish_db = cursor_db2.fetchone()
        if not dish_db:
            return jsonify({'error': 'Увы, не удаётся найти указанное блюдо :('}), 404
        # проверяем наличие необходимых порций блюда
        dish_available = dish_db[4]
        if dish_quantity > dish_available:
            return jsonify({'answer': f'Увы, не хватает порций блюда {dish_id} для выполнения Вашего заказа :('}), 400
    # непосредственно создаём заказ
    try:
        sql_insert = '''INSERT INTO orders (user_id, status, special_requests, created_at) VALUES (?, ?, ?, ?)'''
        cursor_db2.execute(sql_insert, (user_id, status, special_requests, created_at))
        db_lp2.commit()
        sql_query = '''SELECT * FROM orders WHERE user_id = ?'''
        cursor_db2.execute(sql_query, (user_id, ))
        user_dishes = cursor_db2.fetchall()
        order_id = user_dishes[-1][0]
        for dish in dishes:
            dish_id, dish_quantity = dish['id'], dish['quantity']
            sql_query = '''SELECT * FROM dish WHERE id = ?'''
            cursor_db2.execute(sql_query, (dish_id, ))
            dish_info = cursor_db2.fetchall()
            price = dish_info[-1][3]
            sql_insert = '''INSERT INTO order_dish (order_id, dish_id, quantity, price) VALUES (?, ?, ?, ?)'''
            cursor_db2.execute(sql_insert, (order_id, dish_id, dish_quantity, price))
            cursor_db2.execute("UPDATE dish SET quantity = quantity - ? WHERE id = ?", (dish_quantity, dish_id))
            dish_quantity = int(dish_quantity)
            dish_available = dish_info[-1][4] - dish_quantity
            if dish_available <= 0:
                cursor_db2.execute("UPDATE dish SET is_available = 'False' WHERE id = ?", (dish_id, ))
            db_lp2.commit()
        return jsonify({'answer': 'Ура, заказ создан успешно!'}, {'order_id': order_id}), 201
    except Error:
        return jsonify({'answer': 'Увы, не удалось создать Ваш заказ :( Повторите попытку.'}), 400


@app2.route('/process_order', methods=['POST'])
def process_order():
    # функция для обработки заказов пользователей
    sql_query = '''SELECT * FROM orders WHERE status = ?'''
    cursor_db2.execute(sql_query, ('processing', ))
    orders = cursor_db2.fetchall()
    # начинаем готовить заказы
    for order in orders:
        order_id = order[0]
        time.sleep(2)
        updated_at = str(datetime.datetime.now())
        cursor_db2.execute("UPDATE orders SET status = ? WHERE id = ?", ('cooking', order_id))
        cursor_db2.execute("UPDATE orders SET updated_at = ? WHERE id = ?", (updated_at, order_id))
    db_lp2.commit()
    # заканчиваем готовить заказы
    for order in orders:
        order_id = order[0]
        time.sleep(3)
        updated_at = str(datetime.datetime.now())
        cursor_db2.execute("UPDATE orders SET status = ? WHERE id = ?", ('done', order_id))
        cursor_db2.execute("UPDATE orders SET updated_at = ? WHERE id = ?", (updated_at, order_id))
    db_lp2.commit()
    return jsonify({'answer': 'Ура, заказы успешно обработаны!'}), 200


@app2.route('/order', methods=['GET'])
def order_info():
    # выдаём информацию о заказе по его "id"
    info = request.get_json()
    is_ok = check_args_existence(info, ["order_id"])
    if is_ok['answer'] != 'ok':
        return jsonify(is_ok)
    order_id = info['order_id']
    if not order_id.isdigit():
        return jsonify({'answer': 'Увы, поле order_id может представлять из себя только положительное число...'})
    sql_query = '''SELECT * FROM orders WHERE id = ?'''
    cursor_db2.execute(sql_query, (order_id, ))
    order = cursor_db2.fetchone()
    if not order:
        return jsonify({'error': 'Увы, не удаётся найти указанный заказ :('}), 404
    answer = {'id': order[0], 'user_id': order[1], 'status': order[2],
              'special_requests': order[3], 'created_at': order[4], 'updated_at': order[5]}
    return jsonify(answer), 200


@app2.route('/manage_dishes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_dishes():
    # функция для управления блюдами. доступна только менеджеру
    info = request.get_json()
    is_ok = check_args_existence(info, ["user_id"])
    if is_ok['answer'] != 'ok':
        return jsonify(is_ok)
    user_id = info['user_id']
    if not user_id.isdigit():
        return jsonify({'answer': 'Увы, поле user_id может представлять из себя только положительное число...'})
    sql_query = '''SELECT * FROM user WHERE id = ?'''
    cursor_db1.execute(sql_query, (user_id,))
    user = cursor_db1.fetchone()
    if not user:
        return jsonify({'error': 'Увы, не удаётся найти информацию о Вас :('}), 404
    role = user[4]
    if role != 'manager':
        return jsonify({'error': 'Увы, Вы не можете управлять блюдами в связи с Вашей ролью :('}), 405
    if request.method == 'GET':
        is_ok = check_args_existence(info, ["dish_id"])
        if is_ok['answer'] != 'ok':
            return jsonify(is_ok)
        dish_id = info['dish_id']
        if not dish_id.isdigit():
            return jsonify({'answer': 'Увы, поле dish_id может представлять из себя только положительное число...'})
        sql_query = '''SELECT * FROM dish WHERE id = ?'''
        cursor_db2.execute(sql_query, (dish_id,))
        dish = cursor_db2.fetchone()
        if not dish:
            return jsonify({'error': 'Увы, не удаётся найти указанное блюдо :('}), 404
        if not dish[5]:
            return jsonify({'error': 'Увы, указанное блюдо более не доступно (закончились порции) :('}), 404
        return jsonify({'dish': dish}), 200
    elif request.method == 'POST':
        is_ok = check_args_existence(info, ["name", "description", "price", "quantity"])
        if is_ok['answer'] != 'ok':
            return jsonify(is_ok)
        name, description = info['name'], info['description']
        price, quantity = info['price'], info['quantity']
        if not price.isdigit():
            return jsonify({'answer': 'Увы, поле price может представлять из себя только положительное число...'})
        price  = int(price)
        if not quantity.isdigit():
            return jsonify({'answer': 'Увы, поле quantity может представлять из себя только положительное число...'})
        quantity = int(quantity)
        is_available = False
        if quantity > 0:
            is_available = True
        created_at = str(datetime.datetime.now())
        sql_insert = '''INSERT INTO dish (name, description, price, quantity, is_available, created_at) VALUES (?, ?, ?, ?, ?, ?)'''
        cursor_db2.execute(sql_insert, (name, description, price, quantity, is_available, created_at))
        db_lp2.commit()
        return jsonify({'answer': 'Ура, блюдо успешно создано!'}), 201
    elif request.method == 'PUT':
        is_ok = check_args_existence(info, ["name", "description", "price", "quantity", "dish_id"])
        if is_ok['answer'] != 'ok':
            return jsonify(is_ok)
        dish_id, name, description = info['dish_id'], info['name'], info['description']
        price, quantity = info['price'], info['quantity']
        if not dish_id.isdigit():
            return jsonify({'answer': 'Увы, поле dish_id может представлять из себя только положительное число...'})
        if not price.isdigit():
            return jsonify({'answer': 'Увы, поле price может представлять из себя только положительное число...'})
        price = int(price)
        if not quantity.isdigit():
            return jsonify({'answer': 'Увы, поле quantity может представлять из себя только положительное число...'})
        quantity = int(quantity)
        sql_query = '''SELECT * FROM dish WHERE id = ?'''
        cursor_db2.execute(sql_query, (dish_id,))
        dish = cursor_db2.fetchone()
        if not dish:
            return jsonify({'error': 'Увы, не удаётся найти указанное блюдо :('}), 404
        is_available = False
        if quantity > 0:
            is_available = True
        updated_at = str(datetime.datetime.now())
        sql_update = '''UPDATE dish SET name = ?, description = ?, price = ?, quantity = ?, is_available = ?, updated_at = ? WHERE id = ?'''
        cursor_db2.execute(sql_update, (name, description, price, quantity, is_available, updated_at, dish_id))
        db_lp2.commit()
        return jsonify({'answer': 'Ура, блюдо успешно обновлено!'}), 200
    elif request.method == 'DELETE':
        is_ok = check_args_existence(info, ["dish_id"])
        if is_ok['answer'] != 'ok':
            return jsonify(is_ok)
        dish_id = info['dish_id']
        if not dish_id.isdigit():
            return jsonify({'answer': 'Увы, поле dish_id может представлять из себя только положительное число...'})
        sql_query = '''SELECT * FROM dish WHERE id = ?'''
        cursor_db2.execute(sql_query, (dish_id, ))
        dish = cursor_db2.fetchone()
        if not dish:
            return jsonify({'error': 'Увы, не удаётся найти указанное блюдо :('}), 404
        delete_query = '''DELETE FROM dish WHERE id = ?'''
        cursor_db2.execute(delete_query, (dish_id, ))
        db_lp2.commit()
        return jsonify({'answer': 'Мини-ура, блюдо успешно удалено (к сожалению)!'}), 200


@app2.route('/menu', methods=['GET'])
def menu_info():
    # выдаём информацию о доступных блюдах в меню
    sql_query = '''SELECT * FROM dish WHERE is_available = True'''
    cursor_db2.execute(sql_query)
    dishes = cursor_db2.fetchall()
    answer = []
    for dish in dishes:
        dish_info = {'id': dish[0], 'name': dish[1], 'description': dish[2],
                     'price': dish[3], 'quantity': dish[4]}
        answer.append(dish_info)
    return jsonify({'menu': answer}), 200


if __name__ == '__main__':
    app2.run(debug=False, port=7000, host="127.0.0.1")
    cursor_db2.close()
    db_lp2.close()
    cursor_db1.close()
    db_lp1.close()
