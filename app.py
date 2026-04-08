from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import timedelta

app = Flask(__name__)

# CHAVE FIXA: Isso impede que os usuários sejam deslogados quando o site reinicia
app.secret_key = 'uma_chave_muito_segura_e_permanente_123'
app.permanent_session_lifetime = timedelta(days=30) # Login dura 30 dias

USERS_FILE = 'usuarios.json'
ADMIN_EMAIL = 'cleitinhodacruzsilva4@gmail.com'

def carregar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def salvar_usuarios(dados):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    usuarios = carregar_usuarios()
    user_email = session.get('user')
    
    if not user_email:
        return redirect(url_for('login'))
    
    session.permanent = True # Ativa a duração de 30 dias
    user_info = usuarios.get(user_email)
    e_admin = (user_email == ADMIN_EMAIL)
    
    # Se o usuário não existir mais no banco (deletado), desloga ele
    if not user_info:
        session.clear()
        return redirect(url_for('login'))

    # Se não for admin e não tiver acesso, manda para pagamento
    if not e_admin and not user_info.get('acesso'):
        return render_template('pagamento.html')
    
    return render_template('index.html', 
                           user=user_email, 
                           e_admin=e_admin, 
                           lista_usuarios=usuarios if e_admin else None)

@app.route('/pedir_ativacao')
def pedir_ativacao():
    user_email = session.get('user')
    if user_email:
        usuarios = carregar_usuarios()
        if user_email in usuarios:
            usuarios[user_email]['pediu_liberacao'] = True 
            salvar_usuarios(usuarios)
    return jsonify({"status": "ok"})

@app.route('/liberar/<email>')
def liberar_acesso(email):
    if session.get('user') != ADMIN_EMAIL: return "Proibido", 403
    usuarios = carregar_usuarios()
    if email in usuarios:
        usuarios[email]['acesso'] = True
        usuarios[email]['pediu_liberacao'] = False
        salvar_usuarios(usuarios)
    return redirect(url_for('index'))

@app.route('/remover/<email>')
def remover_usuario(email):
    if session.get('user') != ADMIN_EMAIL: return "Proibido", 403
    usuarios = carregar_usuarios()
    if email in usuarios:
        del usuarios[email] # Remove de vez para não encher a lista
        salvar_usuarios(usuarios)
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuarios = carregar_usuarios()
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = {
                'senha': generate_password_hash(senha),
                'senha_limpa': senha,
                'acesso': False,
                'pediu_liberacao': False
            }
            salvar_usuarios(usuarios)
            session.permanent = True
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuarios = carregar_usuarios()
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email]['senha'], senha):
            session.permanent = True
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
