from flask import Flask, render_template
from flask_wtf import CSRFProtect
from db import close_db
from modules.auth import auth_bp, csrf
from modules.specialista import specialista_bp
from modules.utente import utente_bp
from modules.afferenza import afferenza_bp
from modules.sede import sede_bp
from modules.provvedimento import provvedimento_bp
from modules.users_table import users_table_bp
from modules.utils import login_required
from modules.extras import extras_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
csrf.init_app(app)
app.teardown_appcontext(close_db)


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(specialista_bp)
app.register_blueprint(utente_bp)
app.register_blueprint(afferenza_bp)
app.register_blueprint(sede_bp)
app.register_blueprint(provvedimento_bp)
app.register_blueprint(users_table_bp)
app.register_blueprint(extras_bp)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
