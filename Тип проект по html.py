from flask import Flask, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import request
from flask import render_template
import sqlite3
import json
from flask import render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class DB:
    def __init__(self):
        conn = sqlite3.connect('data_users_base.db')
        self.conn = conn
 
    def get_connection(self):
        return self.conn
 
    def __del__(self):
        self.conn.close()
        
class UserModel:
    def __init__(self, connection):
        self.connection = connection
        
    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()    
 
    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()
    
    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?", (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)    
 
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class registerForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    birth = StringField('Дата рождения', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
 
@app.route('/')
@app.route('/website', methods=['GET', 'POST'])
def website():
    with open("book.json", encoding="utf8") as f:
        books_list = json.loads(f.read())
    return render_template('website.html', books=books_list)  

@app.route('/form_auth', methods=['GET', 'POST'])
def form_auth():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/form_success')
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/form_register', methods=['GET', 'POST'])
def form_register():
    form = registerForm()
    if form.validate_on_submit():
        return redirect('/form_successreg')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/form_menu')
def form_menu():
    return render_template('menu.html')

@app.route('/form_successreg')
def form_successreg():
    db = DB()
    form = registerForm()
    user_name = form.username.data
    password = form.password.data
    user_model = UserModel(db.get_connection())
    exists = user_model.insert(user_name, password)
    return redirect("/index")

@app.route('/form_success')
def form_success():
    db = DB()
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data    
    user_model = UserModel(db.get_connection())
    exists = user_model.exists(user_name, password)
    if (exists[0]):
        session['username'] = user_name
        session['user_id'] = exists[1]
    return redirect("/index")

@app.route('/index')
def index():
    if "username" not in session:
        return redirect('/form_auth')
    return redirect('/form_cab')

@app.route('/search', methods=['GET', 'POST'])
def search():
    with open("book.json", encoding="utf8") as f:
        books_list = json.loads(f.read())    
    if request.method == 'GET':    
        return render_template('search.html')
    elif request.method == 'POST':
        return render_template('book.html', book=request.form["name"], books=books_list, flag=False)
    
@app.route('/form_cab')
def cab():
    return '''<h1>Hi</h1>'''

@app.route('/genre', methods=['GET', 'POST'])
def genre():
    with open("book.json", encoding="utf8") as f:
        books_list = json.loads(f.read())        
    if request.method == 'GET':    
        return render_template('genre.html')
    elif request.method == 'POST':
        return render_template('genre2.html', genre=request.form["genre"], books=books_list)
    

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')