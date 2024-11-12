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

class DbHandler:
    db_file = 'ProjectDB.db'
    def select(self, table_name, filter_dict=None, join_table=None, join_conditions=None):
        if filter_dict is None:
            filter_dict={}
        with DB_local(self.db_file) as db_project:
            query = f'SELECT * FROM {table_name} '
            if join_table is not None:
                query += f'JOIN {join_table} as right_table ON'
               # ["user_id = item.owner", "item.id = contract.item"]
                {table_name+"user_id": join_table+"item"}
                join_conditions_list = []
                for left_field, right_field in join_conditions.items():
                    join_conditions_list.append(f'{table_name}.{left_field}=right_table.{right_field})')
                query += 'AND '.join(join_conditions_list)

            if filter_dict:
                query += ' WHERE '
                items = []
                for key, value in filter_dict.items():
                    items.append(f'{key}=?')
                query += 'AND  '.join(items)
            db_project.execute(query, tuple(value for value in filter_dict.values()))
            return db_project.fetchall()

    def insert(self, table_name, data_dict):
        with DB_local(self.db_file) as db_project:
            query = f'Insert INTO {table_name}'
            query += ','.join(data_dict.keys())
            query += ' VALUES ('
            query += ','.join([f':{items}' for items in data_dict.values()])
            query += ')'
            #insert into table name a1,a2 values ?,?,
            db_project.execute(query, data_dict.values)

db_connector = DbHandler()

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
    if request.method == 'POST':
        form_data = request.form
        db_connector.insert('user', form_data)

        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'GET':
         return render_template('login.html')
     elif request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user_data = db_connector.select('user', {'login': username, 'password': password})
        if user_data:
             session['user_id'] = user_data[0]['login']
             return "Login successful, welcome " + user_data[0]['user_id']
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
        items = db_connector.select('item')
        return render_template('items.html', items=items)
    if request.method == 'POST':
        if session.get('user_id') is None:
            return redirect('/login')
        else:
            user_id = db_connector.select('user', {'login': session['user_id']})[0]['id']
            query_args = request.form
            query_args['owner_id'] = user_id
            db_connector.insert('item', query_args)

            return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def items(item_id):
    if request.method == 'GET':
        item = db_connector.select('item', {'id': item_id})[0]
        return render_template('items_id.html', item=item)
    if request.method == 'DELETE':
        if session.get('user_id') is None:
            return redirect('/login')
        return f'DELETE{item_id}'


@app.route('/leasers', methods=['GET'])
def all_leasers():
    if request.method == 'GET':
        leaser = db_connector('contract', {})[0]
        # with DB_local('ProjectDB.db') as db_project:
        #     db_project.execute("Select * from leaser")
        #     leasers = db_project.fetchall()
        return render_template('leasers.html', leasers=leasers)



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
        contr = db_connector.select('contract')
        return render_template('contracts.html', contracts=contracts)
    elif request.method == 'POST':
        form_data = request.form
        item_id = form_data['item_id']
        user_id = session.get('user_id')
        leaser = db_connector.select('item', {'id': item_id})[0]
        taker = db_connector.select('user', {'login': user_id})[0]
        new_cont = {
            'text' : form_data['text'],
            'start_date' : form_data['start_date'],
            'end_date' : form_data['end_date'],
            'leaser': form_data['leaser'],
            'taker': form_data['taker'],
            'item': item_id,
            'status': 'pending'
        }
        db_connector.insert('contract', new_cont)
        return 'Contract created'
        # query = """insert into contract (text, start_date, end_date, leaser, taker, item) values (?,?,?,?,?,?)"""
        # with DB_local('ProjectDB.db') as db_project:
        #     db_project.execute('select id from user where login = ?', (session['user_id'],))
           # my_id = db_project.fetchone()['id']
          #  taker_id = my_id

           # item_id = request.form['item']
            #from form hidden field
          #  leaser_id = request.form['leaser']

            #or by item from db
        # db_connector.select('item', {item_id})
        #     db_project.execute("select * from item where id = ?", (item_id,))
        #     leaser_id = db_project.fetchone()['owner_id']
        #     contract_status = "pending"
        #     query_args = (request.form['text'], request.form['start_date'], request.form['end_date'],leaser_id, taker_id, item_id, contract_status)
        #     insert_query = """insert into contract (text, start_date, end_date, leaser, taker, item, status) values(?,?,?,?,?,?,?)"""
        #     db_project.execute(query, query_args)
        # return 'POST'

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
        search_res = db_connector.select('item', filter_dict={'query': query})

        return render_template ('search_res.html', results=search_res, query=query)
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

#to do:
#sort out with databases and template to html files