import aiosqlite

async def creating_db():
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_tg INTEGER NOT NULL,
                    status INTEGER NOT NULL,
                    arkans INTEGER,
                    username TEXT,
                    minuses INTEGER,
                    bithday_date TEXT,
                    payed INTEGER default 0,
                    time_register DATETIME default CURRENT_TIMESTAMP,
                    )''')
    await db.commit()
    await db.close()

db_path = './num_bot.db'

async def add_user(id_tg, status, username):
    db = await aiosqlite.connect(db_path)
    user = await db.execute('''SELECT id FROM users WHERE id_tg = ?''', (id_tg,))
    user = await user.fetchone()
    if not user:
        await db.execute('''INSERT INTO users (id_tg, status, username) VALUES (?, ?, ?)''', (id_tg, status, username))
        await db.commit()
    await db.close()

async def add_bithday_date(id_tg, bithday_date):
    db = await aiosqlite.connect(db_path)
    await db.execute('''UPDATE users SET bithday_date = ? WHERE id_tg = ?''', (bithday_date, id_tg))
    await db.commit()
    await db.close()
    
async def get_bithday_date(id_tg):
    db = await aiosqlite.connect(db_path)
    result = await db.execute('''SELECT birthday_date FROM users WHERE id_tg = ?''', (id_tg,))
    birthday_date = await result.fetchone()[0]
    await db.close()
    return birthday_date
    
async def add_minuses(id_tg, minuses, status):
    db = await aiosqlite.connect(db_path)
    await db.execute('''UPDATE users SET minuses = ?, status = ? WHERE id_tg = ?''', (minuses, status, id_tg))
    await db.commit()
    await db.close()

async def add_arkans(id_tg, arkans):
    db = await aiosqlite.connect(db_path)
    await db.execute('''UPDATE users SET arkans = ? WHERE id_tg = ?''', (arkans, id_tg))
    await db.commit()
    await db.close()

async def calculate_30_procents(id_tg):
    db = await aiosqlite.connect(db_path)
    result = await db.execute('''SELECT arkans FROM users WHERE id_tg = ?''', (id_tg,))
    arkans = await result.fetchone()
    arkans = arkans[0]
    arkans = arkans * 0.3
    arkans = int(arkans)
    minuses = await db.execute('''SELECT minuses FROM users WHERE id_tg = ?''', (id_tg,))
    minuses = await minuses.fetchone()
    minuses = minuses[0]
    minuses = int(minuses)
    if minuses >= arkans:
        return True
    else:
        return False

async def get_users_list():
    db = await aiosqlite.connect(db_path)
    cursor = await db.execute('''SELECT id, username, id_tg FROM users ORDER BY id ASC''')
    users_list = await cursor.fetchall()
    await db.close()
    return users_list

async def pre_buy_status(id_tg, status):
    db = await aiosqlite.connect(db_path)
    await db.execute('''UPDATE users SET status = ? WHERE id_tg = ?''', (status, id_tg))
    await db.commit()
    await db.close()
    
async def update_status(id_tg, status):
    db = await aiosqlite.connect(db_path)
    if status == 9:
        payed = 1
    else:
        payed = 0
    await db.execute('''UPDATE users SET status = ?, payed = ? WHERE id_tg = ?''', (status, payed, id_tg))
    await db.commit()
    await db.close()

    
async def calculate_conversion():
    db = await aiosqlite.connect(db_path)
    total_users = await db.execute('''SELECT COUNT(*) FROM users WHERE status >= 1''')
    total_users = await total_users.fetchone()
    total_users = total_users[0]
    number_users = [total_users]
    list_statuses = [2,3,4,5,6,7,8,9]
    for status in list_statuses:
        total_users_with_status = await db.execute('''SELECT COUNT(*) FROM users WHERE status >= ?''', (status,))
        total_users_with_status = await total_users_with_status.fetchone()
        total_users_with_status = total_users_with_status[0]
        number_users.append(total_users_with_status)
    return number_users