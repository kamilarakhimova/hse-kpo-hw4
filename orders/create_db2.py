import sqlite3


def create_database2():
    # устанавливаем соединение с БД (при необходимости сначала создав её)
    db_lp2 = sqlite3.connect('databases/dishes_orders.db')
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
    sql_create_order = '''
    CREATE TABLE IF NOT EXISTS order (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        status VARCHAR(50) NOT NULL,
        special_requests TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
    '''
    cursor_db2.execute(sql_create_order)
    
    # создаём таблицу "order_dish"
    sql_create_order_dish = '''
    CREATE TABLE IF NOT EXISTS order_dish (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        dish_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES order(id),
        FOREIGN KEY (dish_id) REFERENCES dish(id)
    )
    '''
    cursor_db2.execute(sql_create_order_dish)
    
    # сохраняем изменения в БД
    db_lp2.commit()
    
    # закрываем объекты cursor_db2 и db_lp2 во избежание проблем с БД
    cursor_db2.close()
    db_lp2.close()
