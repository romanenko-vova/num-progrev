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
                    bithday_date TEXT
                    )''')
    await db.commit()
    await db.close()


async def add_user(id_tg, status, username):
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''INSERT INTO users (id_tg, status, username) VALUES (?, ?, ?)''', (id_tg, status, username))
    await db.commit()
    await db.close()

async def add_bithday_date(id_tg, bithday_date):
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''UPDATE users SET bithday_date = ? WHERE id_tg = ?''', (bithday_date, id_tg))
    await db.commit()
    await db.close()

async def add_minuses(id_tg, minuses, status):
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''UPDATE users SET minuses = ?, status = ? WHERE id_tg = ?''', (minuses, status, id_tg))
    await db.commit()
    await db.close()

async def add_arkans(id_tg, arkans):
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''UPDATE users SET arkans = ? WHERE id_tg = ?''', (arkans, id_tg))
    await db.commit()
    await db.close()

async def calculate_30_procents(id_tg):
    db = await aiosqlite.connect('num_bot.db')
    result = await db.execute('''SELECT arkans FROM users WHERE id_tg = ?''', (id_tg,))
    arkans = await result.fetchone()
    arkans = arkans[0]
    arkans = arkans * 0.3
    arkans = int(arkans)
    minuses = await db.execute('''SELECT minuses FROM users WHERE id_tg = ?''', (id_tg,))
    minuses = await minuses.fetchone()
    minuses = minuses[0]
    minuses = int(minuses)
    if arkans > minuses:
        return 1
    elif arkans < minuses:
        return 0

async def get_users_list():
    db = await aiosqlite.connect('num_bot.db')
    cursor = await db.execute('''SELECT id, username FROM users ORDER BY id ASC''')
    users_list = await cursor.fetchall()
    await db.close()
    return users_list

async def pre_buy_status(id_tg, status):
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''UPDATE users SET status = ? WHERE id_tg = ?''', (status, id_tg))
    await db.commit()
    await db.close()

async def conversion_from_start_to_minuses():
    db = await aiosqlite.connect('num_bot.db')
    total_users = await db.execute('''SELECT COUNT(*) FROM users WHERE status >= 0''')
    total_users = await total_users.fetchone()
    total_users_with_minuses = await db.execute('''SELECT COUNT(*) FROM users WHERE status >= 1''')
    total_users_with_minuses = await total_users_with_minuses.fetchone()
    db.close()
    if total_users[0] > 0:
        conversion_rate_to_minuses = (total_users_with_minuses[0] / total_users[0]) * 100
        return conversion_rate_to_minuses
    else:
        return 0

async def conversion_from_minuses_to_payment():
    db = await aiosqlite.connect('num_bot.db')
    total_users_with_minuses = await db.execute('''SELECT COUNT(*) FROM users WHERE status >= 1''')
    total_users_with_minuses = await total_users_with_minuses.fetchone()
    total_users_with_payment = await db.execute('''SELECT COUNT(*) FROM users WHERE status = 2''')
    total_users_with_payment = await total_users_with_payment.fetchone()
    db.close()
    if total_users_with_minuses[0] > 0:
        conversion_rate_to_payment = (total_users_with_payment[0] / total_users_with_minuses[0]) * 100
        return conversion_rate_to_payment
    else:
        return 0

async def overall_conversion_to_payment():
    db = await aiosqlite.connect('num_bot.db')
    total_users = await db.execute('''SELECT COUNT(*) FROM users WHERE status >= 0''')
    total_users = await total_users.fetchone()
    total_users_with_payment = await db.execute('''SELECT COUNT(*) FROM users WHERE status = 2''')
    total_users_with_payment = await total_users_with_payment.fetchone()
    db.close()
    if total_users[0] > 0:
        conversion_rate_after_payment = (total_users_with_payment[0] / total_users[0]) * 100
        return conversion_rate_after_payment
    else:
        return 0