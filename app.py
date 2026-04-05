from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']
usuarios = {} 
postagens = [] # Aqui cada postagem agora terá 'likes' e 'comentarios'

@app.route('/')
def index():
    user_email = session.get('user')
    e_admin = user_email in ADMINS
    return render_template('index.html', posts=postagens, user=user_email, e_admin=e_admin)

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS:
        return "Acesso negado!", 403
    if request.method == 'POST':
        video = request.files.get('video')
        desc = request.form.get('descricao')
        if video:
            filename = video.filename
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Criamos o post com contadores zerados
            postagens.insert(0, {
                'id': filename, 
                'video': filename, 
                'desc': desc, 
                'likes': 0, 
                'comentarios': []
            })
            return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/curtir/<id_video>')
def curtir(id_video):
    if not session.get('user'):
        return redirect(url_for('login'))
    for p in postagens:
        if p['id'] == id_video:
            p['likes'] += 1
    return redirect(url_for('index'))

@app.route('/comentar/<id_video>', methods=['POST'])
def comentar(id_video):
    if not session.get('user'):
        return redirect(url_for('login'))
    texto = request.form.get('conteudo')
    user = session.get('user')
    if texto:
        for p in postagens:
            if p['id'] == id_video:
                p['comentarios'].append({'autor': user, 'texto': texto})
    return redirect(url_for('index'))

# ... (Mantenha as rotas de login, cadastro, logout e deletar que já funcionam)
