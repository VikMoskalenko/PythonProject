
from datetime import datetime
from functools import wraps
import celery_tasks
from celery import Celery
from flask import Flask, request, render_template, redirect, session, flash
import sqlite3
from sqlalchemy.sql.functions import current_user, func
#from select import select
from database import init_db, db_session
#from models import User, Item
import model
from sqlalchemy import select


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
#     conn = sqlite3.connect('ProjectDB____.db')
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
    db_file = 'ProjectDB____.db'
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
class User(DbHandler):
    table_name = None
    id = None
    login = None
    password = None
    full_name = None
    def __init__(self, id, login, password, full_name):
        self.id = id
        self.login = login
        self.password = password
        self.full_name = full_name


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
            query = f'''SELECT fullname FROM users where login = ?'''
            print(query)
            db_project.execute(query, (session['user_id']))
            fullname = db_project.fetchone()['fullname']
        return render_template('user.html', fullname=fullname)
    if request.method == 'POST':
        return render_template('user.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = request.form.to_dict()
        print("Form Data Received:", form_data)
        init_db()
        user = model.User()

        user.login = form_data['login']
        user.password = form_data['password']
        user.fullname = form_data['fullname']
        user.nino = form_data['nino']
        user.contacts = form_data['contacts']
        user.photo = form_data['photo']
        db_session.add(user)
        db_session.commit()
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'GET':
         error_txt = "not valide"

         return render_template('login.html', error_txt=error_txt)
     elif request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        init_db()

       # user_data = db_connector.select('user', {'login': username, 'password': password})
        query = select(model.User).where(model.User.login==username)
        user_data = db_session.execute(query).first()
        if user_data:
             session['user_id'] = user_data[0].user_id
             return redirect ('/profile')

        else:
            return redirect('/login?error=User not found')


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
        init_db()
        #items_query = select(model.Item)
       # items = db_session.execute(items_query).scalars().all()
        items = db_session.query(model.Item, model.Contract).\
            outerjoin(model.Contract,
                    (model.Item.id == model.Contract.item_id) &
                    (func.date(datetime.date.today()) >= func.date(model.Contract.start_date)) &
                    (func.date(datetime.date.today()) <= func.date(model.Contract.end_date))).all()

        render_items = []
        for item in items:
            render_items.append(dict(name=item.Item.name, ))

        return render_template('items.html', items=items)
    if request.method == 'POST':
        if session.get('user_id') is None:
            return redirect('/login')
        else:
            init_db()
            current_user = db_session.scalar(select(model.User).where(model.User.login==session['user_id']))

            form_data = request.form.to_dict()
            form_data['owner_id'] = current_user.user_id
            new_item = model.Item(**form_data)
            db_session.add(new_item)
            db_session.commit()
                # query_args = request.form
                # query_args['user_id'] = current_user['user_id']
                # db_connector.insert('item', query_args)

            return redirect('/items')


@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def items(item_id):
    if request.method == 'GET':
       # item = db_connector.select('item', {'id': item_id})[0]
       item = db_session.execute(select(model.Item).where(model.Item.item_id == item_id)).scalar()
       return  render_template('item_detail.html', item=item_id, photo=item.photo,
                               name=item.name, description = item.description, price_hour=item.price_hour,
                               price_week=item.price_week, price_month=item.price_month, owner_id=item.owner_id,
                               current_user = session['user_id'])
       # item = db_connector.query(model.Item).get(item_id)
       # if item_id is None:
       #    return f"Item with ID {item_id} not found", 404
       #return render_template('items_id.html', item=item)
    # if request.method == 'DELETE':
    #     if session.get('user_id') is None:
    #         return redirect('/login')
    #     current_user = db_session.scalar(select(model.User).where(model.User.login==session['user_id']))
    #     item = db_session.query(model.Item).get(item_id)
    #     if item is None:
    #         return f"Item with ID {item_id} not found", 404
    #     if item.owner_id == current_user.user_id:
    #         return f"Item with ID {item_id} does not belong to {current_user.user_id} but you can see it :)"
    #     db_session.delete(item)
    #     db_session.commit()
    #     return f'DELETE{item_id}'
@app.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = db_session.execute(select(model.Item).filter_by(id=item_id)).scalar()
    if item:
        db_session.delete(item)
        db_session.commit()
        celery_tasks.send_email(item_id)
        return redirect('/items')
    return 'Item is not found', 404

@app.route('/leasers', methods=['GET'])
def all_leasers():
    if request.method == 'GET':
        #leaser = db_connector('contract', {})[0]
        leaser = db_session.query(model.Leaser).all()
        return render_template('leasers.html', leasers=leasers)



@app.route('/leasers/<int:leasers_id>', methods=['GET', 'POST', 'DELETE'])
def leasers(leasers_id):
    if request.method == 'GET':
        with DB_local('ProjectDB____.db') as db_project:
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
       with DB_local('ProjectDB____.db') as db_project:
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
        with DB_local('ProjectDB____.db') as db_project:
            db_project.execute("Delete from leaser where id = ?", (leasers_id))
        return redirect('/leasers')

        #return f'DELETE{leasers_id}'

@app.route('/contracts', methods=['GET', 'POST'])
def all_contracts():
    #init_db()
    if request.method == 'GET':
        init_db()
        #contract = db_session.execute(select(model.Contract).filter_by(contract_id=contract_id)).scalar()
        # Fetch contracts where the user is the taker
        my_contracts = db_session.execute(
            select(model.Contract).where(model.Contract.taker == session['user_id'])
        ).scalars().all()

        # Fetch contracts where the user is the leaser
        contracts_by_my_items = db_session.execute(
            select(model.Contract).where(model.Contract.leaser == session['user_id'])
        ).scalars().all()

        return render_template(
            'contracts.html',
            my_contracts=my_contracts,
            contracts_by_my_items=contracts_by_my_items
        )
    elif request.method == 'POST':
        contract_data = request.form.to_dict()
        new_cont = model.Contract(**contract_data)
        taker = session['user_id']
        leaser = db_session.execute(select(model.Item).filter_by(id=contract_data['leaser'])).scalar()
        new_cont.taker = taker
        new_cont.leaser = leaser
        #signed_date = str(contract_data['signed_date'])
        db_session.add(new_cont)


        # init_db()
        # form_data = request.form
        # item_id = form_data['item_id']
        # user_id = session.get('user_id')
        # item = db_session.query(model.Item).get(item_id)
        # user = db_session.query(model.User).filter(model.User.login==user_id).first()
        # # leaser = db_connector.select('item', {'id': item_id})[0]
        # # taker = db_connector.select('user', {'login': user_id})[0]
        # new_cont = {
        #     'text' : form_data['text'],
        #     'start_date' : form_data['start_date'],
        #     'end_date' : form_data['end_date'],
        #     'leaser': form_data['leaser'],
        #     'taker': form_data['taker'],
        #     'item': item_id,
        #     'status': 'pending'
        # }
        # db_session.add(new_cont)
        db_session.commit()
        return 'Contract created'
    return redirect('/contract')

# @app.route('/contracts', methods=['GET', 'POST'])
# def all_contracts():
#     init_db()
#     if request.method == 'GET':
#         cont = db_session.query(model.Contract).all()
#         return render_template('contracts.html', contracts=contracts)
#     elif request.method == 'POST':
#         init_db()
#         form_data = request.form
#         item_id = form_data['item_id']
#         user_id = session.get('user_id')
#         item = db_session.query(model.Item).get(item_id)
#         user = db_session.query(model.User).filter(model.User.login==user_id).first()
#         # leaser = db_connector.select('item', {'id': item_id})[0]
#         # taker = db_connector.select('user', {'login': user_id})[0]
#         new_cont = {
#             'text' : form_data['text'],
#             'start_date' : form_data['start_date'],
#             'end_date' : form_data['end_date'],
#             'leaser': form_data['leaser'],
#             'taker': form_data['taker'],
#             'item': item_id,
#             'status': 'pending'
#         }
#         db_session.add(new_cont)
#         db_session.commit()
#         return 'Contract created'

@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH', 'PUT'])
def contracts(contract_id):
    if request.method == 'GET':
        init_db()
        contract = db_session.query(model.Contract).get(contract_id)
        if contract is None:
            return "Contract not found", 404
        return render_template("contracts.html", contract=contract)
    if request.method == 'POST':
        return 'POST'
    # if request.method == 'PATCH':
    #     return 'PATCH'

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
        complain_txt = request.form.get('complain')
        user_id = session.get('user_id')

        if not user_id:
            flash("Please login first and then write a complaint")
            return redirect(request.referrer or '/')

        db_connector.insert('complain', {
            'user_id': user_id,
            'complain_text': complain_txt
        })

        flash("Your complaint has been submitted")
        return redirect('/')


    return render_template('complain.html')
@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'
@app.route('/add_task', methods=['GET'])
def set_task():

    celery_tasks.add.delay(1,2)
    return "task sent"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

#to do:
#sort out with databases and template to html files