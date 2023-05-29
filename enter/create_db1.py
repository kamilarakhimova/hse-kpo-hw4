import sqlite3


def create_database1():
    # устанавливаем соединение с БД (при необходимости сначала создав её)
    db_lp1 = sqlite3.connect('databases/users.db')
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
