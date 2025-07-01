from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_wtf import CSRFProtect
from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired
from db import get_db_connection

csrf = CSRFProtect()

auth_bp = Blueprint('auth', __name__)


class LoginForm(Form):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM Users WHERE username=%s', (form.username.data,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], form.password.data):
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
