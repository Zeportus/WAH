import sqlite3

con = sqlite3.connect("whatsAppSpam.db", check_same_thread=False)
cur = con.cursor()

def add_user(name, password):
    cur.execute(f"INSERT INTO users(name, password) VALUES ('{name}', '{password}')")
    con.commit()
    user_id = get_user_id(name)
    cur.execute(f"INSERT INTO users_settings(user_id) VALUES ({user_id})")
    con.commit()

def del_user(name):
    user_id = get_user_id(name)
    cur.execute(f"DELETE FROM users WHERE name = '{name}'")
    cur.execute(f"DELETE FROM users_settings WHERE user_id = {user_id}")
    cur.execute(f"DELETE FROM users_autoanswers WHERE user_id = {user_id}")
    con.commit()

def save_user(name, phones, message, delay, trigger, answer, manager_phone):
    user_id = get_user_id(name)
    cur.execute(f"UPDATE users_settings SET phones = '{phones}', message = '{message}', delay = {delay} WHERE user_id = {user_id}")
    cur.execute(f"UPDATE users SET phone = '{manager_phone}' WHERE id = {user_id}")
    auto_answers_ids = get_user_auto_answers(name)
    for i in range(len(trigger)):
        cur.execute(f"UPDATE users_autoanswers SET trigger = '{trigger[i]}', answer = '{answer[i]}' WHERE user_id = {user_id} AND id = {auto_answers_ids[i][0]}")
    con.commit()

def get_user_phone(name):
    return cur.execute(f"SELECT phone FROM users WHERE name = '{name}'").fetchone()[0]

def add_empty_auto_answer(name):
    user_id = get_user_id(name)
    cur.execute(f"INSERT INTO users_autoanswers(user_id) VALUES ({user_id})")
    con.commit()

def del_auto_answer(answer_id):
    cur.execute(f"DELETE FROM users_autoanswers WHERE id = {answer_id}")
    con.commit()

def get_users():
    return cur.execute("SELECT name, password FROM users")

def get_user_id(name):
    return cur.execute(f"SELECT id FROM users WHERE name = '{name}'").fetchone()[0]

def get_user_id_by_phone(manager_phone):
    return cur.execute(f"SELECT id FROM users WHERE phone = '{manager_phone}'").fetchone()[0]

def get_user_seetings(name):
    user_id = get_user_id(name)
    return cur.execute(f"SELECT phones, message, delay FROM users_settings WHERE user_id = {user_id}").fetchone()

def get_user_auto_answers(name):
    user_id = get_user_id(name)
    return cur.execute(f"SELECT id, trigger, answer FROM users_autoanswers WHERE user_id = {user_id}").fetchall()

def check_user(name, password):
    return cur.execute(f"SELECT name FROM users WHERE name = '{name}' AND password = '{password}'").fetchone() is not None

def stop_phone(phone):
    cur.execute(f"INSERT INTO phones_stoplist VALUES ('{phone}')")
    con.commit()

def get_phones(name):
    user_id = get_user_id(name)
    phones_str = cur.execute(f"SELECT phones FROM users_settings WHERE user_id = {user_id}").fetchone()[0]
    return phones_str.replace('\r', '').split('\n')

def check_phone(phone):
    return cur.execute(f"SELECT phone FROM phones_stoplist WHERE phone = '{phone}'").fetchone() is None

def get_auto_info(manager_phone):
    user_id = get_user_id_by_phone(manager_phone)
    return cur.execute(f"SELECT trigger, answer FROM users_autoanswers WHERE user_id = {user_id}").fetchall()

def get_delay(manager_phone):
    user_id = get_user_id_by_phone(manager_phone)
    return cur.execute(f"SELECT delay FROM users_settings WHERE user_id = '{user_id}'").fetchone()[0]

