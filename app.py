from flask import Flask, request, session, render_template_string, redirect, flash, render_template, url_for
import mysql.connector
import re
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import math
app = Flask(__name__)
app.secret_key = 'senha_ultra_secreta'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='HELP_APP'
    )
    
@app.route('/')
@app.route('/index')
@app.route('/inicio')
def home():
    return render_template('index.html')

@app.route('/servicos')
def servicos():
    return render_template('Serviços.html') 

@app.route('/orcamento')
def orcamento():
    return render_template('Orçamento.html')

@app.route('/historico_consulta')
def historico_consulta():
    return render_template('HC.html')

@app.route('/criarconta')
def criarconta():
    return render_template('Cadastro.html')

@app.route('/cadastro')  
def cadastro():
    return render_template('Cadastro.html')

@app.route('/cadastro2')  
def cadastro2():
    return render_template('Cadastro_2.html')

@app.route('/sobre_nos')
def sobre_nos():
    return render_template('Sobre-nós_ofl.html')

@app.route('/termos')
def termos():
    return render_template('Termos de uso.html')

@app.route('/avaliacoes')
def avaliacoes():
    return render_template('Avaliações.html')

@app.route('/autonomo')
def autonomo():
    return render_template('Autonomo.html')

@app.route('/Adress')
def adress():
    return render_template('Adress.html')

@app.route('/mobile')
def mobile():
    return render_template('Aplicativo_mobile.html')

@app.route('/prestador')
def prestador():
    return render_template('Prestador.html')

@app.route('/denuncia')
def denuncia():
    return render_template('Denunciar.html')

@app.route('/atividade')
def atividade():
    return render_template('Atividade.html')

@app.route('/configuracao')
def configuracao():
    return render_template('Configurações.html')


@app.route('/perfil')
def perfil():
    return render_template('Perfil.html')

@app.route('/contratar')
def contratar():
    return render_template('Contratar.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/notificacao')
def notificacao():
    return render_template('Notificações.html')

@app.route('/help_pro')
def help_pro():
    return render_template('Help,pro.html')

@app.route('/historico')
def historico():
    return render_template('Histórico de serviço.html')

@app.route('/pedreiro')
def pedreiro():
    return render_template('pedreiro.html')

@app.route('/informatica')
def informatica():
    return render_template('Informatica.html')

@app.route('/eletricista')
def eletricista():
    return render_template('eletricista.html')

@app.route('/mecanico')
def mecanico():
    return render_template('Mecanico.html')

@app.route('/encanador')
def encanador():
    return render_template('Encanador.html')

@app.route('/limpeza')
def limpeza():
    return render_template('Limpeza.html')

@app.route('/politica')
def politica():
    return render_template('Politica de privacidade.html')

@app.route('/cliente')
def cliente():
    return render_template('Cliente.html')

@app.route('/empresa')
def empresa():
    return render_template('Empresa.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    senha = request.form['senha']
    
    print(f"Dados recebidos: Name={name}, Email={email}")

    # Validação de dados
    if not name or not email or not senha:
        flash('Todos os campos são obrigatórios!')
        return redirect('/')

    senha_hash = generate_password_hash(senha)
    print("Senha criptografada com sucesso")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO USUARIO (NOME_COMPLETO, EMAIL, SENHA) VALUES (%s, %s, %s)', (name, email, senha_hash))
        conn.commit()
        print("Dados inseridos com sucesso no banco")
    except mysql.connector.Error as err:
        flash(f'Erro ao cadastrar usuário: {err}')
        conn.rollback()
        print(f"Erro no banco de dados: {err}")
        return redirect('/')
    finally:
        cursor.close()
        conn.close()

    flash(f"Usuário {name} cadastrado com sucesso!")
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Use get para evitar KeyError
        senha = request.form.get('senha')

        if not email or not senha:
            flash('Email e senha são obrigatórios.')
            return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USUARIO WHERE EMAIL = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], senha):  # Verifique a senha
            session['user_id'] = user[0]  
            flash(f"Bem-vindo, {user[1]}!")
            return redirect(url_for('home'))
        else:
            flash('Email ou senha incorretos.')
            return redirect(url_for('login'))

    return render_template('login.html')  

@app.route('/login_submit', methods=['POST'])
def login_submit():
    
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        flash('Email e senha são obrigatórios.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM USUARIO WHERE EMAIL = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user[3], senha):
        session['user_id'] = user[0]
        flash(f"Bem-vindo, {user[1]}!")
        return redirect(url_for('home'))
    else:
        flash('Email ou senha incorretos.')
        return redirect(url_for('login'))

@app.route('/add_catalogo')
def add_catalogo():
    return render_template('add_item.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu com sucesso.')
    return redirect('/login')

if __name__ == '__main__':
    'criar_db()'
    app.run(debug=True)
