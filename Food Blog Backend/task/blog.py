import sqlite3
import sys

def connect_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
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
        print('Error create_table', t_name)
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

    flds = '''  serve_id INTEGER PRIMARY KEY,
                meal_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                FOREIGN KEY (meal_id) REFERENCES meals (meal_id),
                FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id)'''
    create_table(conn, 'serve', flds)

    flds = '''  quantity_id INTEGER PRIMARY KEY,
                quantity INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                measure_id INTEGER NOT NULL,
                ingredient_id INTEGER NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id),
                FOREIGN KEY (measure_id) REFERENCES measures (measure_id),
                FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id)
            '''
    create_table(conn, 'quantity', flds)
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

def add_serve(cur, rec_id):
    q = '''1) breakfast  2) brunch  3) lunch  4) supper
Enter proposed meals separated by a space: '''
    meals = input(q).split()
    for id in meals:
        cur.execute(f"""INSERT INTO serve (meal_id, recipe_id)
                    VALUES ('{int(id)}', '{rec_id}');""")

def get_measure_id(m):
    measures = ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")
    if m:
        m_list = [x for x in measures if x.startswith(m)]
        m_id = -1 if len(m_list) != 1 else measures.index(m_list[0]) + 1
    else:
        m_id = 8
    return m_id

def get_ing_id(ing):
    ingredients = ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar")
    m_list = [x for x in ingredients if ing in x]
    ing_id = -1 if len(m_list) != 1 else ingredients.index(m_list[0]) + 1
    return ing_id

def add_quantity(cur, rec_id):
    q = 'Input quantity of ingredient <press enter to stop>: '
    while True:
        vals = input(q).split()
        if not vals:
            return
        m = vals[1] if len(vals) == 3 else ''
        m_id = get_measure_id(m)
        ing_id = get_ing_id(vals[-1])
        if m_id < 0 or ing_id < 0:
            print('The measure is not conclusive!')
            continue
        cur.execute(f"""INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id)
                    VALUES ('{int(vals[0])}', '{rec_id}', '{m_id}', '{ing_id}');""")

def add_recipes(conn):
    cur = conn.cursor()
    print('Pass the empty recipe name to exit.')
    while True:
        name = input('Recipe name: ')
        if not name:
            conn.commit()
            return
        txt = input('Recipe description: ')
        rec_id = cur.execute(f"""INSERT INTO recipes (recipe_name, recipe_description)
                        VALUES ('{name}', '{txt}');""").lastrowid
        add_serve(cur, rec_id)
        add_quantity(cur, rec_id)

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

