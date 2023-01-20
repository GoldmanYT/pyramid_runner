import sqlite3

con = sqlite3.connect('database.sqlite')
cur = con.cursor()

cur.execute('''
    CREATE TABLE records(
        id INTEGER PRIMARY KEY NOT NULL,
        name TEXT,
        score INTEGER NOT NULL
    )
''')

cur.execute('''
    CREATE TABLE levels(
        id INTEGER PRIMARY KEY NOT NULL,
        path TEXT NOT NULL
    )
''')
cur.execute('''
    INSERT INTO levels(id, path)
        VALUES (1, "levels/level0_1"), (2, "levels/level0_2"), (3, "levels/level0_3") 
''')

con.commit()
con.close()
