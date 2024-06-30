import aiosqlite
import datetime


async def creating_db():
    db = await aiosqlite.connect("num_bot.db")
    await db.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_tg INTEGER NOT NULL,
                    status INTEGER NOT NULL,
                    arkans INTEGER,
                    flat_arkans TEXT,
                    username TEXT,
                    minuses INTEGER,
                    birthday_date TEXT,
                    payed INTEGER default 0,
                    time_register DATETIME default CURRENT_TIMESTAMP,
                    num_progrev INTEGER default 0,
                    phone TEXT,
                    conversation_status INTEGER default 0,
                    file_path TEXT
                    )""")
    await db.commit()
    await db.close()


db_path = "./num_bot.db"


async def add_user(id_tg, status, username):
    db = await aiosqlite.connect(db_path)
    user = await db.execute("""SELECT id FROM users WHERE id_tg = ?""", (id_tg,))
    user = await user.fetchone()
    if not user:
        await db.execute(
            """INSERT INTO users (id_tg, status, username) VALUES (?, ?, ?)""",
            (id_tg, status, username),
        )
        await db.commit()
    await db.close()
    
async def update_conversation_status(id_tg, status):
    db = await aiosqlite.connect(db_path)
    await db.execute(
        """UPDATE users SET conversation_status = ? WHERE id_tg = ?""", (status, id_tg)
    )
    await db.commit()
    await db.close()

async def load_conversation_status(id_tg):
    db = await aiosqlite.connect(db_path)
    result = await db.execute(
        """SELECT conversation_status FROM users WHERE id_tg = ?""", (id_tg,)
    )
    conversation_status = await result.fetchone()
    conversation_status = conversation_status[0]
    await db.close()
    return conversation_status

async def update_flat_arkans(id_tg, flat_arkans):
    str_arkans = ';'.join(list(map(str,flat_arkans)))
    db = await aiosqlite.connect(db_path)
    await db.execute(
        """UPDATE users SET flat_arkans = ? WHERE id_tg = ?""", (str_arkans, id_tg)
    )
    await db.commit()
    await db.close()
    
async def get_flat_arkans(id_tg):
    db = await aiosqlite.connect(db_path)
    flat_arkans = await db.execute(
        """SELECT flat_arkans FROM users WHERE id_tg = ?""", (id_tg,)
    )
    flat_arkans = await flat_arkans.fetchone()
    flat_arkans = flat_arkans[0]
    flat_arkans = list(map(int, flat_arkans.split(';')))
    await db.close()
    return flat_arkans

async def add_birthday_date(id_tg, birthday_date):
    db = await aiosqlite.connect(db_path)
    await db.execute(
        """UPDATE users SET birthday_date = ? WHERE id_tg = ?""", (birthday_date, id_tg)
    )
    await db.commit()
    await db.close()


async def get_birthday_date(id_tg):
    db = await aiosqlite.connect(db_path)
    result = await db.execute(
        """SELECT birthday_date FROM users WHERE id_tg = ?""", (id_tg,)
    )
    birthday_date = await result.fetchone()
    birthday_date = birthday_date[0]
    await db.close()
    return birthday_date


async def get_payment_status(id_tg):
    db = await aiosqlite.connect(db_path)
    result = await db.execute("""SELECT payed FROM users WHERE id_tg = ?""", (id_tg,))
    payed = await result.fetchone()
    payed = payed[0]
    await db.close()
    return payed


async def add_minuses(id_tg, minuses, status):
    db = await aiosqlite.connect(db_path)
    await db.execute(
        """UPDATE users SET minuses = ?, status = ? WHERE id_tg = ?""",
        (minuses, status, id_tg),
    )
    await db.commit()
    await db.close()


async def add_arkans(id_tg, arkans):
    db = await aiosqlite.connect(db_path)
    await db.execute("""UPDATE users SET arkans = ? WHERE id_tg = ?""", (arkans, id_tg))
    await db.commit()
    await db.close()

async def update_file_path(id_tg, file_path):
    db = await aiosqlite.connect(db_path)
    await db.execute("""UPDATE users SET file_path = ? WHERE id_tg = ?""", (file_path, id_tg))
    await db.commit()
    await db.close()
    
async def get_file_path(id_tg):
    db = await aiosqlite.connect(db_path)
    file_path = await db.execute(
        """SELECT file_path FROM users WHERE id_tg = ?""", (id_tg,)
    )
    file_path = await file_path.fetchone()
    file_path = file_path[0]
    await db.close()
    return file_path

async def get_arkans(id_tg):
    db = await aiosqlite.connect(db_path)
    arkans = await db.execute(
        """SELECT arkans FROM users WHERE id_tg = ?""", (id_tg,)
    )
    arkans = await arkans.fetchone()
    arkans = arkans[0]
    await db.close()
    return arkans

async def calculate_30_procents(id_tg):
    db = await aiosqlite.connect(db_path)
    result = await db.execute("""SELECT arkans, minuses FROM users WHERE id_tg = ?""", (id_tg,))
    result = await result.fetchone()
    arkans = result[0]
    minuses = result[1]
    # print(arkans, minuses)
    if int(minuses / arkans * 100) >= 30:
        return 1
    else:
        return 0
    
    


async def get_users_list():
    db = await aiosqlite.connect(db_path)
    cursor = await db.execute(
        """SELECT id, username, id_tg FROM users ORDER BY id ASC"""
    )
    users_list = await cursor.fetchall()
    await db.close()
    return users_list


async def pre_buy_status(id_tg, status):
    db = await aiosqlite.connect(db_path)
    await db.execute("""UPDATE users SET status = ? WHERE id_tg = ?""", (status, id_tg))
    await db.commit()
    await db.close()


async def update_status(id_tg, status):
    db = await aiosqlite.connect(db_path)
    if status == 9:
        payed = 1
    else:
        payed = 0
    await db.execute(
        """UPDATE users SET status = ?, payed = ? WHERE id_tg = ?""",
        (status, payed, id_tg),
    )
    await db.commit()
    await db.close()


async def get_users_to_progrev():
    today = datetime.datetime.now()
    gap1 = datetime.timedelta(hours=9)
    gap2 = datetime.timedelta(days=3, hours=12)
    right_time_end = today - gap1
    right_time_start = today - gap2

    str_end = right_time_end.strftime("%Y-%m-%d %H:%M:%S")
    str_start = right_time_start.strftime("%Y-%m-%d %H:%M:%S")

    db = await aiosqlite.connect(db_path)
    # total_users = await db.execute("SELECT id_tg, num_progrev, status FROM users")
    total_users = await db.execute(f'SELECT id_tg, num_progrev, status FROM users WHERE time_register >= "{str_start}" and time_register <= "{str_end}" and status < 9 and num_progrev < 3"')

    total_users = await total_users.fetchall()
    await db.close()
    return total_users

async def update_num_progrev(id_tg, num_progrev):
    db = await aiosqlite.connect(db_path)
    await db.execute(f'UPDATE users SET num_progrev = {num_progrev + 1} WHERE id_tg = {id_tg}')
    await db.close()

async def update_phone(id_tg, phone):
    db = await aiosqlite.connect(db_path)
    await db.execute(f'UPDATE users SET phone={phone} WHERE id_tg = {id_tg}')
    await db.close()

async def calculate_conversion():
    db = await aiosqlite.connect(db_path)
    total_users = await db.execute("""SELECT COUNT(*) FROM users WHERE status >= 1""")
    total_users = await total_users.fetchone()
    total_users = total_users[0]
    number_users = [total_users]
    list_statuses = [2, 3, 4, 5, 6, 7, 8, 9]
    for status in list_statuses:
        total_users_with_status = await db.execute(
            """SELECT COUNT(*) FROM users WHERE status >= ?""", (status,)
        )
        total_users_with_status = await total_users_with_status.fetchone()
        total_users_with_status = total_users_with_status[0]
        number_users.append(total_users_with_status)
    return number_users
