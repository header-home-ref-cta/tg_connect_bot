import sqlite3
import decouple

def create_tables():
    try:
        with sqlite3.connect(decouple.config('PATH_TO_DATABASE')) as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users "
                        "(tg_id BIGINT PRIMARY KEY, email TEXT, app_password TEXT, prompt TEXT, subscription BOOLEAN, "
                        "run_task BOOLEAN DEFAULT False)")
            conn.commit()
            cur.execute("CREATE TABLE IF NOT EXISTS texts (info TEXT, system_prompt TEXT)")
            conn.commit()
            cur.execute("CREATE TABLE IF NOT EXISTS payments "
                        "(id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id BIGINT, payment_id TEXT, status TEXT, "
                        "FOREIGN KEY (tg_id) REFERENCES users(tg_id))")
            conn.commit()
            cur.execute("CREATE TABLE IF NOT EXISTS subscription "
                        "(tg_id BIGINT, subscription_start DATE, subscription_end DATE, "
                        "FOREIGN KEY (tg_id) REFERENCES users(tg_id))")
            conn.commit()
            cur.execute("CREATE TABLE IF NOT EXISTS used_emails "
                        "(id integer primary key AUTOINCREMENT, tg_id BIGINT, email TEXT, "
                        "FOREIGN KEY (tg_id) REFERENCES users(tg_id))")
            conn.commit()
    except sqlite3.Error as e:
        print(e)
