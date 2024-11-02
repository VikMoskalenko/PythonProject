from flask import Flask, request, render_template, redirect
import sqlite3
app = Flask(__name__)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DB_local():
    def __init__(self, filename):
         self.conn = sqlite3.connect(filename)
         self.conn.row_factory = dict_factory
         self.cur = self.conn.cursor()
    def __enter__(self):
        return self.cur
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

# a1 = open('hfhf')
# a1.read()
# a1.write()
# a1.close()
#
# with open('hfhf') as a1:
#     a1.read()
#     a1.write()
#
#
# def open_DB(db_name):
#     conn = sqlite3.connect('ProjectDB.db')
#     cur = conn.cursor()
#     return cur
@app.route('/')
def index():  # put application's code here
    return render_template('index.html')
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        return render_template('user.html')
    if request.method == 'POST':
        return 'post'
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        with DB_local('ProjectDB.db') as db_project:
            form_data = request.form
            db_project.execute('''INSERT INTO user
                (login, password, nino, fullname, photo, contacts) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                (form_data['login'], form_data['password'],
                 form_data['nino'], form_data['fullname'],
                 form_data['photo'], form_data['contacts']))

        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'GET':
         return render_template('login.html')
     elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with DB_local('ProjectDB.db') as db_project:
             db_project.execute('''SELECT * FROM user where login = ? AND password = ? ''',
                                (username, password))
             user = db_project.fetchone()
             if user:
                 return "Login successful, welcome"
             else:
                 return "Wrong username or password", 401


@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/items', methods=['GET', 'POST'])
def all_items():
    if request.method == 'GET':
          with DB_local('ProjectDB.db') as db_project:
                  db_project.execute("SELECT * FROM item")
                  items = db_project.fetchall()
          return render_template('items.html', items=items)
    if request.method == 'POST':
            with DB_local('ProjectDB.db') as db_project:
                db_project.execute('''INSERT INTO item (photo, name, description, price_hour, price_week, price_month) 
                                   VALUES (:photo, :name, :description, :price_hour, :price_week, :price_month)''', request.form)
            return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def items(item_id):
    if request.method == 'GET':
        return f'GET{item_id}'
    if request.method == 'DELETE':
        return f'DELETE{item_id}'


@app.route('/leasers', methods=['GET'])
def all_leasers():
    if request.method == 'GET':
        return f'GET'


@app.route('/leasers/<leasers_id>', methods=['GET', 'POST', 'DELETE'])
def leasers(leasers_id):
    if request.method == 'GET':
        return f'GET{leasers_id}'
    if request.method == 'POST':
        return f'POST{leasers_id}'
    if request.method == 'DELETE':
        return f'DELETE{leasers_id}'

@app.route('/contracts', methods=['GET', 'POST'])
def all_contracts():
    if request.method == 'GET':
          with DB_local('ProjectDB.db') as db_project:
                  db_project.execute("SELECT * FROM contract")
                  contracts = db_project.fetchall()
          return render_template('contracts.html', contracts=contracts)
    if request.method == 'POST':
        return 'POST'

@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH', 'PUT'])
def contracts(contract_id):
    if request.method == 'GET':
        return f'GET{contract_id}'
    if request.method == 'POST':
        return 'POST'
    if request.method == 'PATCH':
        return 'PATCH'

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'
@app.route('/complain', methods=['POST'])
def complain():
    if request.method == 'POST':
        return 'POST'

@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'

if __name__ == '__main__':
    app.run()

