from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'secreta'  # Definindo uma chave secreta para gerenciar sessões

# Conexão com o MongoDB
client = MongoClient("mongodb+srv://micael:aspirine@cluster0.cfzpz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.TrabUniforplatweb

# Rota para a landing page
@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/contatos')
def contatos():
    return render_template('contatos.html')

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        # Lógica de autenticação
        user = db.usuario.find_one({'email': email})
        
        if user and check_password_hash(user['senha'], senha):  # Verificando a senha com check_password_hash
            session['user_id'] = str(user['_id'])  # Salva o ID do usuário na sessão
            session['role'] = user['role']  # Salva o papel (role) do usuário na sessão
            return redirect(url_for('dashboard'))
        
        return 'Credenciais inválidas'  # Se a senha estiver incorreta
        
    return render_template('login.html')

# Rota para a página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        # Hash da senha
        hashed_password = generate_password_hash(senha)
        
        # Verificar se o email já existe
        if db.usuario.find_one({'email': email}):
            return 'Email já cadastrado'
        
        # Inserir novo usuário
        new_user = {
            'nome': nome,
            'email': email,
            'senha': hashed_password,
            'role': 'user'  # Todo novo usuário será um "user" comum
        }
        db.usuario.insert_one(new_user)
        
        return redirect(url_for('login'))
    return render_template('cadastro.html')

# Rota para o painel administrativo (dashboard)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:  # Verifica se o usuário está logado
        return redirect(url_for('login'))
    
    user = db.usuario.find_one({'_id': ObjectId(session['user_id'])})
    
    if user['role'] == 'admin':
        users = db.usuario.find()  # Administrador pode ver todos os usuários
    else:
        users = [user]  # Usuário comum só vê a própria conta
    
    return render_template('dashboard.html', users=users)

# Rota para editar um usuário
@app.route('/editar_usuario/<user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    if 'user_id' not in session:  # Verifica se o usuário está logado
        return redirect(url_for('login'))
    
    user = db.usuario.find_one({'_id': ObjectId(user_id)})
    logged_user = db.usuario.find_one({'_id': ObjectId(session['user_id'])})

    # Verifica se o usuário logado é o dono da conta ou um administrador
    if logged_user['role'] == 'user' and logged_user['_id'] != ObjectId(user_id):
        return 'Você não tem permissão para editar esse usuário.'
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        # Hash da senha
        hashed_password = generate_password_hash(senha) if senha else user['senha']
        
        # Atualiza os dados no banco de dados
        db.usuario.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'nome': nome, 'email': email, 'senha': hashed_password}}
        )
        
        return redirect(url_for('dashboard'))
    
    return render_template('editar_usuario.html', user=user)

# Rota para excluir um usuário
@app.route('/excluir_usuario/<user_id>', methods=['GET'])
def excluir_usuario(user_id):
    if 'user_id' not in session:  # Verifica se o usuário está logado
        return redirect(url_for('login'))
    
    logged_user = db.usuario.find_one({'_id': ObjectId(session['user_id'])})
    
    if logged_user['role'] == 'user' and logged_user['_id'] != ObjectId(user_id):
        return 'Você não tem permissão para excluir esse usuário.'
    
    # Exclui o usuário
    db.usuario.delete_one({'_id': ObjectId(user_id)})
    
    # Deslogar o usuário após excluir a conta
    session.pop('user_id', None)  # Remove o ID do usuário da sessão
    session.pop('role', None)  # Remove o papel do usuário da sessão
    
    return redirect(url_for('login'))  # Redireciona para a página de login

# Rota para deslogar o usuário
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove o ID do usuário da sessão
    session.pop('role', None)  # Remove o papel do usuário da sessão
    return redirect(url_for('login'))  # Redireciona para a página de login

if __name__ == '__main__':
    app.run(debug=True)
