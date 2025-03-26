# sistema.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-exemplo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------- MODELOS -------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)

class OrdemServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(30), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    servico = db.Column(db.String(100), nullable=False)
    relato = db.Column(db.Text, nullable=False)

# ------------------------- ROTAS -------------------------
@app.route('/')
def index():
    if 'usuario_id' in session:
        ordens = OrdemServico.query.all()
        return render_template('dashboard.html', ordens=ordens)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome=nome).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('index'))
        return render_template('login.html', erro='Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

@app.route('/nova', methods=['GET', 'POST'])
def nova_os():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nova = OrdemServico(
            cliente=request.form['cliente'],
            contato=request.form['contato'],
            marca=request.form['marca'],
            servico=request.form['servico'],
            relato=request.form['relato']
        )
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('nova_os.html')

# ------------------------- EXECUTAR -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(nome='admin').first():
            hash_senha = generate_password_hash('root')
            admin = Usuario(nome='admin', senha_hash=hash_senha)
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
