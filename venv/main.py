from http.client import HTTPResponse
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask import Flask, session
from flask_session import Session
from flask_api import status
from flask_cors import CORS, cross_origin
import sqlite3

DATABASE = 'database.db'
app = Flask("main")
app.secret_key = 'BAD_SECRET_KEY'
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, support_credentials=True)
sess = Session()

app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='None'
    )

@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE users (id_user INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, admin BOOLEAN)')
    conn.execute('CREATE TABLE ingredients (id_ingredient INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT)')
    conn.execute('CREATE TABLE recipes (id_recipe INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT)')
    conn.execute('CREATE TABLE recipes_ingredients (id_recipe_ingredient INTEGER PRIMARY KEY AUTOINCREMENT, id_r INTEGER, id_i INTEGER, value TEXT)')
    conn.execute('INSERT INTO users (username, password, admin) VALUES (?,?,?)',('admin','admin', 1) )
    conn.execute('INSERT INTO ingredients (name, type) VALUES (?,?)',('apple','fruit') )
    conn.execute('INSERT INTO ingredients (name, type) VALUES (?,?)',('banana','fruit') )
    conn.execute('INSERT INTO ingredients (name, type) VALUES (?,?)',('eggplant','vegetable') )
    conn.execute('INSERT INTO recipes (name, description) VALUES (?,?)',('salad','Salad with apple and banana') )
    conn.execute('INSERT INTO recipes_ingredients (id_r, id_i, value) VALUES (?,?,?)',(1,1,'100g') )
    conn.execute('INSERT INTO recipes_ingredients (id_r, id_i, value) VALUES (?,?,?)',(1,2,'200g') )
    conn.commit()
    # Zakończenie połączenia z bazą danych
    conn.close()
    
    return 'OK'

@app.route('/users', methods=['POST'])
def add_user():
    if 'username' in session and 'admin' in session and session['admin']:
        json = request.json
        username = json["username"]
        password = json["password"]
        admin = 0

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute('INSERT INTO users (username,password,admin) VALUES (?,?,?)',(username,password,admin) )
        con.commit()
        cur.execute('select * from users where username = ? and password = ?', (username, password))
        user = cur.fetchall(); 
        con.close()

        return jsonify(user)
    else:
        return 'Błąd'

@app.route('/users', methods=['GET'])
def get_users():
    if 'username' in session and 'admin' in session and session['admin']:
        con = sqlite3.connect(DATABASE)
        
        # Pobranie danych z tabeli
        cur = con.cursor()
        cur.execute("select * from users")
        users = cur.fetchall(); 

        return jsonify(users)
    else:
        return 'Error'

@app.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    try:
        json = request.json
        username = json["username"]
        password = json["password"]
    except:
        return 'Wrong login data'

    print(username, password)
    con = sqlite3.connect(DATABASE)
    
    # Pobranie danych z tabeli
    cur = con.cursor()
    cur.execute('select * from users where username = ? and password = ?', (username, password))
    user = cur.fetchall(); 

    if len(user) > 0:
        print(session)
        session['username'] = user[0][1]
        session['admin'] = user[0][3]
        print(session)
        return jsonify(user)
    else:
        return 'Wrong login or password' 

@app.route('/logout')
@cross_origin(supports_credentials=True)
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    return 'OK'

@app.route('/ingredients', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_ingredient():
    if 'username' in session and 'admin' in session and session['admin']:
        json = request.json
        name = json["name"]
        type = json["type"]

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute('INSERT INTO ingredients (name,type) VALUES (?,?)',(name,type) )
        con.commit()
        cur.execute('select * from ingredients where name = ? and type = ?', (name, type))
        ingredient = cur.fetchall(); 
        con.close()
        return jsonify(ingredient)
    else:
        return 'Błąd'

@app.route('/ingredients', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_ingredients():
        id_ingredient = 0
        id_ingredient = request.args.get("id")
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        if(id_ingredient==None):
        # Pobranie danych z tabeli
            cur.execute("select * from ingredients order by name")
        else:
            cur.execute("select * from ingredients where id_ingredient = ?", (id_ingredient,))
        ingredients = cur.fetchall(); 
        return jsonify(ingredients)

@app.route('/ingredients/<string:name>', methods=['GET'])
def get_ingredient_by_name(name):
        con = sqlite3.connect(DATABASE)
        
        # Pobranie danych z tabeli
        cur = con.cursor()
        cur.execute("select * from ingredients where name = ?",(name,))
        ingredient = cur.fetchall(); 

        return jsonify(ingredient)

@app.route('/ingredients', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_ingredient():
    if 'username' in session and 'admin' in session and session['admin']:
        json = request.json
        id = json["id"]
        name = json["name"]
        type = json["type"]
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("update ingredients set name=?, type=? where id_ingredient=?",(name,type,id))
        con.commit()
        con.close()
        return "OK"
    else:
        return "Błąd"

@app.route('/recipes', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_recepie():
    if 'username' in session and 'admin' in session and session['admin']:
        json = request.json
        name = json["name"]
        description = json["description"]
        ingredients = json["ingredients"]

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute('INSERT INTO recipes (name,description) VALUES (?,?)',(name,description) )
        con.commit()
        cur.execute('select * from recipes where name = ? and description = ?', (name,description))
        recipe = cur.fetchall(); 
        id_recipe = 0
        id_recipe = recipe[0][0]
        for i in ingredients:
            ingredient_name = ""
            ingredient_name = i[0]
            cur.execute('select * from ingredients where name = ?', (ingredient_name,))
            ingredient = cur.fetchall(); 
            print(i)
            print(ingredient)
            id_ingredient = 0
            id_ingredient = ingredient[0][0]
            ingredient_value = ""
            ingredient_value = i[1]
            print(id_ingredient)
            cur.execute('INSERT INTO recipes_ingredients (id_r,id_i,value) VALUES (?,?,?)',(id_recipe,int(id_ingredient), ingredient_value) )
            con.commit()
        print(id_recipe)
        cur.execute('select * from recipes_ingredients where id_r = ?', (id_recipe,))
        recipe_ingredients = cur.fetchall(); 
        con.close()

        return jsonify(recipe_ingredients)
    else:
        return 'Błąd'

@app.route('/recipes', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_recepies():
        id_recipe = 0
        id_recipe = request.args.get("id")
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        print(id_recipe)
        if(id_recipe==None):
            # Pobranie danych z tabeli
            cur.execute("select * from recipes order by name")
        else:
            cur.execute("select r.name, r.description, i.name, r_i.value from recipes r join recipes_ingredients r_i on r.id_recipe=r_i.id_r join ingredients i on r_i.id_i=i.id_ingredient where id_recipe = ?",(id_recipe,))
        recipes = cur.fetchall(); 
        return jsonify(recipes)

@app.route('/recipes', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_recipe_by_id():
    if 'username' in session and 'admin' in session and session['admin']:
        id_recipe = 0
        id_recipe = request.args.get("id")
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("delete from recipes where id_recipe=?",(id_recipe,))
        con.commit()
        cur.execute("delete from recipes_ingredients where id_r=?",(id_recipe,))
        con.commit()
        con.close()
        return "OK"
    else:
        return 'Błąd'


#Get all ingredients types (distinct) /tablica types
@app.route('/types', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_ingredients_types():
        types = ""
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("select i.type from ingredients i group by i.type")
        types = cur.fetchall(); 
        return jsonify(types)

#Get all recipes by type /tablica wszystkich recipes 
@app.route('/recipes/<string:type>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_recepies_by_type(type):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("select r.id_recipe, r.name, r.description from recipes r join recipes_ingredients r_i on r.id_recipe=r_i.id_r join ingredients i on r_i.id_i=i.id_ingredient where i.type = ? group by r.name",(type,))
        recipes = cur.fetchall(); 
        return jsonify(recipes)

if __name__ == "__main__":
    sess.init_app(app)
    app.config.from_object(__name__)
    app.debug = True
    app.run()