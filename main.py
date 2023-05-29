import sqlite3


def create_database1():
    # устанавливаем соединение с БД (при необходимости сначала создав её)
    db_lp1 = sqlite3.connect(r'databases/users.db')
    cursor_db1 = db_lp1.cursor()

    # создаём таблицу "user"
    sql_create_user = '''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(10) NOT NULL CHECK (role IN ('customer', 'chef', 'manager')), 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    cursor_db1.execute(sql_create_user)

    # создаём таблицу "session"
    sql_create_session = '''
    CREATE TABLE IF NOT EXISTS session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token VARCHAR(255) NOT NULL, 
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
    '''
    cursor_db1.execute(sql_create_session)

    # сохраняем изменения в БД
    db_lp1.commit()

    # закрываем объекты cursor_db1 и db_lp1 во избежание проблем с БД
    cursor_db1.close()
    db_lp1.close()


def create_database2():
    # устанавливаем соединение с БД (при необходимости сначала создав её)
    db_lp2 = sqlite3.connect(r'databases/dishes_orders.db')
    cursor_db2 = db_lp2.cursor()

    # создаём таблицу "dish"
    sql_create_dish = '''
    CREATE TABLE IF NOT EXISTS dish (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        quantity INT NOT NULL,
        is_available BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    cursor_db2.execute(sql_create_dish)

    # создаём таблицу "order"
    sql_create_orders = '''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        status VARCHAR(50) NOT NULL,
        special_requests TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
    '''
    cursor_db2.execute(sql_create_orders)

    # создаём таблицу "order_dish"
    sql_create_order_dish = '''
    CREATE TABLE IF NOT EXISTS order_dish (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        dish_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (dish_id) REFERENCES dish(id)
    )
    '''
    cursor_db2.execute(sql_create_order_dish)

    # сохраняем изменения в БД
    db_lp2.commit()

    # закрываем объекты cursor_db2 и db_lp2 во избежание проблем с БД
    cursor_db2.close()
    db_lp2.close()


if __name__ == '__main__':
    create_database1()
    create_database2()
