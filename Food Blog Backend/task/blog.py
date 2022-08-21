import sqlite3
import sys

def connect_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, t_name, flds):
    sql = f'CREATE TABLE IF NOT EXISTS {t_name} ({flds});'
    try:
        c = conn.cursor()
        c.execute(sql)
    except sqlite3.Error as e:
        print(e)

def create_db(db_name):
    conn = connect_db(db_name)
    flds = '''  measure_id INTEGER PRIMARY KEY,
                measure_name TEXT UNIQUE'''
    create_table(conn, 'measures', flds)
    flds = '''  ingredient_id INTEGER PRIMARY KEY,
                ingredient_name TEXT NOT NULL UNIQUE'''
    create_table(conn, 'ingredients', flds)
    flds = '''  meal_id INTEGER PRIMARY KEY,
                meal_name TEXT NOT NULL UNIQUE'''
    create_table(conn, 'meals', flds)
    flds = '''  recipe_id INTEGER PRIMARY KEY,
                recipe_name TEXT NOT NULL,
                recipe_description TEXT'''
    create_table(conn, 'recipes', flds)
    return conn

def add_data(conn):
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    cur = conn.cursor()
    cur.execute("SELECT * FROM meals")
    rows = cur.fetchall()
    if len(rows) == 0:
        for d in data:
            for v in data[d]:
                cur.execute(f"INSERT INTO {d} ({d[:-1]}_name) VALUES ('{v}');")

    conn.commit()

def add_recipes(conn):
    cur = conn.cursor()
    print('Pass the empty recipe name to exit.')
    while True:
        name = input('Recipe name: ')
        if not name:
            conn.commit()
            return
        txt = input('Recipe description: ')
        cur.execute(f"""INSERT INTO recipes (recipe_name, recipe_description)
                        VALUES ('{name}', '{txt}');""")


def main():
    args = sys.argv
    if len(args) != 2:
        print('Specify the DB name as an argument')
        exit()

    db_name = args[1]
    conn = create_db(db_name)
    add_data(conn)
    add_recipes(conn)
    conn.close()

if __name__ == "__main__":
    main()

