from flask import Flask, render_template, flash, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import sqlite3
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user

# Flask config:

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'

# App DB:

class DBManager():
    def __init__(self,dbName):
        self.dbName = dbName

    def query(self,sql1, sql2=''):
        con = sqlite3.connect(self.dbName)
        with con:
            cur = con.cursor()
            cur.execute(sql1,sql2)
            res = cur.fetchall()
        if con:
            con.close()

        return res

appdb = DBManager('app.db')
appkeys = ['app_id','name','description','color','defaultstatus','link']

# Login:

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, login, password, applist):
        self.id = id
        self.login = login
        self.password = password
        self.authenticated = False
        self.applist = applist

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    usentry = appdb.query("SELECT * from user where user_id = (?)", [user_id])
    if usentry is None:
        return None
    else:
        linkentry = appdb.query("SELECT * from link where user_id = (?)", [user_id])
        if len(linkentry) != 0:
            app_ids = [row[1] for row in linkentry]
        else:
            appentry = appdb.query("SELECT app_id from app where defaultstatus = (?)", ["Yes"])
            app_ids = [row[0] for row in appentry]
            for app_id in app_ids:
                appdb.query("INSERT OR REPLACE INTO link(user_id,app_id) VALUES(?,?)", [user_id, app_id])

    return User(*usentry[0],app_ids)

# Forms:

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

# Routes:

@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    global Us
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        entry = appdb.query("SELECT * FROM user where login = (?)", [form.login.data])
        if len(entry) == 0:
            flash(form.login.data + ' not found. Login Failed.')
        else:
            user = entry[0]
            Us = load_user(user[0])
            if form.login.data == Us.login and form.password.data == Us.password:
                login_user(Us)
                LoggedIn = list({form.login.data})[0]
                flash('Logged in ' + LoggedIn)
                return redirect(url_for('main'))
            else:
                flash('Login Failed.')

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():
    appdict = {}
    for aindx,ap in enumerate(Us.applist):
        appres = appdb.query("SELECT * FROM app where app_id = (?)", [ap])
        if len(appdict) == 0:
            for kindx,key in enumerate(appkeys):
                appdict[key] = [appres[0][kindx]]
        else:
            for kindx,key in enumerate(appkeys):
                appdict[key].append(appres[0][kindx])

    return render_template('main.html', title='Dashboard',appdict=appdict)

@app.route('/editapps', methods=['GET', 'POST'])
@login_required
def editapps():
    appdict = {}
    allapps = appdb.query("SELECT * FROM app","")
    for ap in allapps:
        if len(appdict) == 0:
            for kindx,key in enumerate(appkeys):
                appdict[key] = [ap[kindx]]
        else:
            for kindx,key in enumerate(appkeys):
                appdict[key].append(ap[kindx])

    return render_template('editapps.html', title='Add or Remove Apps',appdict=appdict)

@app.route('/add/<this_app_id>')
@login_required
def add(this_app_id):
    appdb.query("INSERT OR REPLACE INTO link(user_id,app_id) VALUES(?,?)", [Us.id, this_app_id])
    linkentry = appdb.query("SELECT * from link where user_id = (?)", [Us.id])
    if len(linkentry) != 0:
        Us.applist = [row[1] for row in linkentry]
    return redirect(url_for('main'))

@app.route('/remove/<this_app_id>')
@login_required
def remove(this_app_id):
    appdb.query("DELETE FROM link WHERE (user_id,app_id) = (?,?)", [Us.id, this_app_id])
    linkentry = appdb.query("SELECT * from link where user_id = (?)", [Us.id])
    if len(linkentry) != 0:
        Us.applist = [row[1] for row in linkentry]
    return redirect(url_for('main'))


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)
    