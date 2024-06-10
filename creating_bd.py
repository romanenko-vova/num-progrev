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

async def add_minuses(id_tg, minuses):
    db = await aiosqlite.connect('num_bot.db')
    await db.execute('''UPDATE users SET minuses = ? WHERE id_tg = ?''', (minuses, id_tg))
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

