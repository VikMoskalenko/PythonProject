from functools import wraps

from flask import Flask, request, render_template, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'fkfkfksirshp'
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
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id'not in session:
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper
@app.route('/')
def index():  # put application's code here
    return render_template('index.html')
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # if session.get('user_id') is None:
    #     return redirect('/login')
    if request.method == 'GET':
        with DB_local('Profile.db') as db_project:
            query = f'''SELECT fullname FROM user where login = ?'''
            print(query)
            db_project.execute(query, (session['user_id']))
            fullname = db_project.fetchone()['fullname']
        return render_template('user.html', fullname=fullname)
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
                 session['user_id'] = user['login']

                 return "Login successful, welcome"
             else:
                 return "Wrong username or password", 401


@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
@login_required
def logout():
    session.pop('user_id', None)
    return redirect('/login')
    # if request.method == 'GET':
    #     return 'GET'
    # if request.method == 'POST':
    #     return 'POST'
    # if request.method == 'DELETE':
    #     return 'DELETE'

@app.route('/items', methods=['GET', 'POST'])
def all_items():
    if request.method == 'GET':
          with DB_local('ProjectDB.db') as db_project:
                  db_project.execute("SELECT * FROM item")
                  items = db_project.fetchall()
          return render_template('items.html', items=items)
    if request.method == 'POST':
        if session.get('user_id') is None:
            return redirect('/login')
        else:
            with DB_local('ProjectDB.db') as db_project:
                user_login = session['user_id']
                db_project.execute('select id from user where login = ?', (user_login,))
                user_id = db_project.fetchone()['id']

                query_args = request.form
                query_args['owner_id'] = user_id

                db_project.execute('''INSERT INTO item (photo, name, description, price_hour, price_week, price_month, owner_id) 
                                   VALUES (:photo, :name, :description, :price_hour, :price_week, :price_month, :owner_id)''', query_args)
            return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def items(item_id):
    if request.method == 'GET':
        return f'GET{item_id}'
    if request.method == 'DELETE':
        if session.get('user_id') is None:
            return redirect('/login')
        return f'DELETE{item_id}'


@app.route('/leasers', methods=['GET'])
def all_leasers():
    if request.method == 'GET':
        with DB_local('ProjectDB.db') as db_project:
            db_project.execute("Select * from leaser")
            leasers = db_project.fetchall()
        return render_template('leasers.html', leasers=leasers)
        return f'GET'


@app.route('/leasers/<int:leasers_id>', methods=['GET', 'POST', 'DELETE'])
def leasers(leasers_id):
    if request.method == 'GET':
        with DB_local('ProjectDB.db') as db_project:
            db_project.execute("Select * from leaser where id = ?", (leasers_id))
            leaser = db_project.fetchone()
        if leaser:
            return render_template('leaser_detail.html', leaser=leaser)
        else:
            return "Leaser is not found", 404
       # return f'GET{leasers_id}'
    elif request.method == 'POST':
       if 'user_id' not in session:
           return redirect('/login')
       with DB_local('ProjectDB.db') as db_project:
           form_data = request.form
           db_project.execute(
               '''Update leaser SET name = ?, contact_info''',
               (form_data['name'],form_data['contact_info'], leasers_id)
           )
           return redirect(f'/leasers/{leasers_id}')
        #return f'POST{leasers_id}'
    if request.method == 'DELETE':
        if 'user_id' not in session:
            return redirect('/login')
        with DB_local('ProjectDB.db') as db_project:
            db_project.execute("Delete from leaser where id = ?", (leasers_id))
        return redirect('/leasers')

        #return f'DELETE{leasers_id}'

@app.route('/contracts', methods=['GET', 'POST'])
def all_contracts():
    if request.method == 'GET':
          with DB_local('ProjectDB.db') as db_project:
                  db_project.execute("SELECT * FROM contract")
                  contracts = db_project.fetchall()
          return render_template('contracts.html', contracts=contracts)
    if request.method == 'POST':
        query = """insert into contract (text, start_date, end_date, leaser, taker, item) values (?,?,?,?,?,?)"""
        with DB_local('ProjectDB.db') as db_project:
            db_project.execute('select id from user where login = ?', (session['user_id'],))
            my_id = db_project.fetchone()['id']
            taker_id = my_id

            item_id = request.form['item']
            #from form hidden field
            leaser_id = request.form['leaser']

            #or by item from db
            db_project.execute("select * from item where id = ?", (item_id,))
            leaser_id = db_project.fetchone()['owner_id']
            contract_status = "pending"
            query_args = (request.form['text'], request.form['start_date'], request.form['end_date'],leaser_id, taker_id, item_id, contract_status)
            insert_query = """insert into contract (text, start_date, end_date, leaser, taker, item, status) values(?,?,?,?,?,?,?)"""
            db_project.execute(query, query_args)
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
        return render_template('Search.html')
    if request.method == 'POST':
       # return 'POST'
        query = request.form['query']
        if not query:
            flash("Please enter a search info")
            return redirect('/search')
        with DB_local('ProjectDB.db') as db_project:
            search_query = "Select * from items where name like ? or description like ?"
            db_project.execute(search_query, (query,))
            results = db_project.fetchall()
        return render_template ('search_res.html', results=results, query=query)
@app.route('/complain', methods=['POST'])
def complain():
    if request.method == 'POST':
        #return 'POST'
        complain_txt = request.form.get('complain')
        user_id = session['user_id']

        if not user_id :
            flash("Please login first and then write a complain")
            return redirect(request.referrer or '/')

        with DB_local('ProjectDB.db') as db_project:
            db_project.execute("Insert into complain (user_id, complain_text) Values(?,?)", (user_id,complain_txt))

            flash("Your complaint has been submitted")
            return('/')

@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'

if __name__ == '__main__':
    app.run()

