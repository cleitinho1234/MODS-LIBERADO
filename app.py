from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensões permitidas
IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
VIDEO_EXT = {'.mp4', '.mov', '.avi', '.webm'}

ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']
usuarios = {} 
postagens = [] 

@app.route('/')
def index():
    user_email = session.get('user')
    e_admin = user_email in ADMINS
    return render_template('index.html', posts=postagens, user=user_email, e_admin=e_admin)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = generate_password_hash(senha)
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email], senha):
            session['user'] = email
            return redirect(url_for('index'))
        return "Erro no login! <a href='/login'>Tente de novo</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS:
        return "Acesso negado!", 403
    
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        desc = request.form.get('descricao')
        tipo = 'texto'
        filename = None

        if arquivo and arquivo.filename != '':
            filename = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ext = os.path.splitext(filename)[1].lower()
            if ext in IMAGE_EXT:
                tipo = 'foto'
            elif ext in VIDEO_EXT:
                tipo = 'video'

        postagens.insert(0, {
            'id': filename if filename else str(len(postagens)), 
            'arquivo': filename, 
            'desc': desc, 
            'tipo': tipo,
            'likes': [], 
            'comentarios': []
        })
        return redirect(url_for('index'))
    return render_template('postar.html')

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

@app.route('/comentar/<id_post>', methods=['POST'])
def comentar(id_post):
    user = session.get('user')
    if not user: return redirect(url_for('login'))
    texto = request.form.get('conteudo')
    if texto:
        for p in postagens:
            if p['id'] == id_post:
                p['comentarios'].append({'autor': user, 'texto': texto})
    return redirect(url_for('index'))

@app.route('/deletar/<id_post>')
def deletar(id_post):
    if session.get('user') not in ADMINS: return "Negado", 403
    global postagens
    postagens = [p for p in postagens if p['id'] != id_post]
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
