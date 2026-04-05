from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']
usuarios = {} # Estrutura: {email: {'senha': hash, 'nome': nome}}
postagens = [] 

@app.route('/')
def index():
    user_email = session.get('user')
    user_info = usuarios.get(user_email) if user_email else None
    e_admin = user_email in ADMINS
    return render_template('index.html', posts=postagens, user=user_email, user_info=user_info, e_admin=e_admin)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = {'senha': generate_password_hash(senha), 'nome': email.split('@')[0]}
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/salvar_nome', methods=['POST'])
def salvar_nome():
    user_email = session.get('user')
    novo_nome = request.form.get('novo_nome').strip()
    if not user_email or not novo_nome:
        return redirect(url_for('index'))
    
    # Verifica se o nome já existe para outra pessoa
    for email, info in usuarios.items():
        if info.get('nome') == novo_nome and email != user_email:
            return "Este nome já está em uso! <a href='/'>Voltar</a>"
    
    usuarios[user_email]['nome'] = novo_nome
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email]['senha'], senha):
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS: return "Negado", 403
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        desc = request.form.get('descricao')
        filename = secure_filename(arquivo.filename) if arquivo else None
        if filename: arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        postagens.insert(0, {
            'id': str(uuid.uuid4()), 
            'arquivo': filename, 
            'desc': desc, 
            'tipo': 'video' if filename and filename.endswith('.mp4') else 'foto' if filename else 'texto',
            'likes': [], 
            'comentarios': []
        })
        return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/comentar/<id_post>', methods=['POST'])
def comentar(id_post):
    user_email = session.get('user')
    if not user_email: return redirect(url_for('login'))
    
    texto = request.form.get('conteudo')
    parent_id = request.form.get('parent_id') # Se for uma resposta
    nome_usuario = usuarios[user_email]['nome']
    
    comentario_novo = {
        'id': str(uuid.uuid4()),
        'autor': nome_usuario,
        'texto': texto,
        'respostas': []
    }

    for p in postagens:
        if p['id'] == id_post:
            if not parent_id:
                p['comentarios'].append(comentario_novo)
            else:
                for c in p['comentarios']:
                    if c['id'] == parent_id:
                        comentario_novo['texto'] = f"@{c['autor']} {texto}"
                        c['respostas'].append(comentario_novo)
    return redirect(url_for('index'))

@app.route('/curtir/<id_post>')
def curtir(id_post):
    user = session.get('user')
    if not user: return jsonify({"erro": "login"}), 401
    for p in postagens:
        if p['id'] == id_post:
            if user not in p['likes']: p['likes'].append(user)
            else: p['likes'].remove(user)
            return jsonify({"novo_total": len(p['likes'])})
    return jsonify({"erro": "404"}), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
