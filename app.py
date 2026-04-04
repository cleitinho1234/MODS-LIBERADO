from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho' # Troque isso por qualquer frase

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# E-mails que mandam no site
ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']

# Bancos de dados temporários (Lembre-se: no Render Free, isso apaga ao reiniciar)
usuarios = {} # {email: senha_hash}
postagens = []

@app.route('/')
def index():
    user_email = session.get('user')
    e_admin = user_email in ADMINS
    return render_template('index.html', posts=postagens, user=user_email, e_admin=e_admin)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if email not in usuarios:
            usuarios[email] = generate_password_hash(senha)
            return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email], senha):
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

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
            postagens.insert(0, {'id': filename, 'video': filename, 'desc': desc})
            return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/deletar/<id_video>')
def deletar(id_video):
    if session.get('user') not in ADMINS:
        return "Acesso negado!", 403
    global postagens
    postagens = [p for p in postagens if p['id'] != id_video]
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
