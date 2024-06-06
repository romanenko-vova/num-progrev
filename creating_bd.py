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


async def add_user(id_tg, status, arkans, username, minuses, bithday_date):
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