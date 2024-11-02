from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'GET':
         return render_template('login.html')
     if request.method == 'POST':
        return 'POST'
   #username = request.form['username']
  # password = request.form['password']
   #message = request.form['message']

#to do logic with inserting values

#return redirect('/index')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

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
#   with db_local('name') as db_cur:
#   db_cur.execute("SELECT * FROM item")
#   items = db_cur.fetchall()
# return render template('')
        return 'GET'
    if request.method == 'POST':
        return 'POST'

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
        return 'GET'
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

