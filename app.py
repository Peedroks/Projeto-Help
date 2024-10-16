from flask import Flask, request, session, render_template_string, redirect, flash, render_template
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
        database='Projeto_vanessa'
    )
    
def criar_db():
    conn = get_db_connection()
    cursor = conn.cursor()

 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        senha VARCHAR(255) NOT NULL
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS regiao (
        id_regiao INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL UNIQUE
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS catalogo (
        id_cat INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        categoria VARCHAR(255) NOT NULL,
        id_regiao INT,
        FOREIGN KEY (id_regiao) REFERENCES regiao(id_regiao)
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    
@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    senha = request.form['senha']

    # Validação de dados
    if not name or not email or not senha:
        flash('Todos os campos são obrigatórios!')
        return redirect('/')

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        flash('Formato de e-mail inválido!')
        return redirect('/')

    if len(senha) < 6:
        flash('A senha deve ter pelo menos 6 caracteres.')
        return redirect('/')

    senha_hash = generate_password_hash(senha)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Projeto_vanessa"
    )

    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email, senha) VALUES (%s, %s, %s)', (name, email, senha_hash))
    conn.commit()
    cursor.close()
    conn.close()

    return f"Usuário {name} cadastrado com sucesso!"

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
    email = request.form['email']
    senha = request.form['senha']

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Projeto_vanessa"
    )

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user[3], senha):
        session['user_id'] = user[0]
        return redirect('/home')
    else:
        flash('Email ou senha incorretos.')
        return redirect('/login')


@app.route('/add_catalogo')
def add_catalogo():
    return render_template('add_item.html')

@app.route('/adicionar_item', methods=['POST'])
def adicionar_item():
    if request.method == 'POST':
        nome = request.form['name']  # Mantenha a referência ao formulário
        categoria = request.form['categoria']
        cep = request.form['cep']

        if not nome or not categoria or not cep:
            flash('Todos os campos são obrigatórios!')
            return redirect('/add_catalogo')

        adicionar_endereco_catalogo(nome, categoria, cep)
        flash('Item adicionado com sucesso!')
        return redirect('/add_catalogo')

    return render_template('add_item.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu com sucesso.')
    return redirect('/login')

@app.route('/criarconta')
def criarconta():
    return render_template('form.html')

@app.route('/home')
def home():
    return render_template('Home.html')

"""@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='Projeto_vanessa'
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM catalogo WHERE nome LIKE %s OR categoria LIKE %s", ('%' + query + '%', '%' + query + '%'))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('search_results.html', results=results, query=query)

    return redirect('/home')
"""
def buscar_endereco_por_cep(cep):
    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    
    if response.status_code == 200:
        endereco = response.json()
        if "erro" not in endereco:
            return endereco
        else:
            print(f"CEP não encontrado: {cep}")
            return "CEP não encontrado."
    print(f"Erro ao conectar à API com status: {response.status_code}")
    return "Erro ao conectar à API."

    
def adicionar_endereco_catalogo(nome, categoria, cep):
    endereco = buscar_endereco_por_cep(cep)
    
    if isinstance(endereco, dict):
        cidade = endereco['localidade']
        estado = endereco['uf']
        regiao_nome = f"{cidade}, {estado}"
        
        latitude, longitude = obter_coordenadas_por_cep(cep)
        if latitude is None or longitude is None:  # Verifica se as coordenadas são válidas
            flash("Não foi possível obter as coordenadas geográficas para este CEP.")
            return  
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id_regiao FROM regiao WHERE nome = %s', (regiao_nome,))
        regiao = cursor.fetchone()

        if not regiao:
            cursor.execute('INSERT INTO regiao (nome) VALUES (%s)', (regiao_nome,))
            conn.commit()
            regiao_id = cursor.lastrowid
        else:
            regiao_id = regiao[0]

        cursor.execute('INSERT INTO catalogo (name, categoria, id_regiao, latitude, longitude) VALUES (%s, %s, %s, %s, %s)', 
                       (nome, categoria, regiao_id, latitude, longitude))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        flash(endereco) 


def obter_coordenadas_por_cep(cep):
    api_key = 'AIzaSyCuFxK7ExQ8hTUqMPhB3f7m0VIJT-mZ1FA'  
    response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={cep}&key={api_key}")
    if response.status_code == 200:
        resultado = response.json()
        if resultado['results']:
            localizacao = resultado['results'][0]['geometry']['location']
            return localizacao['lat'], localizacao['lng']
    return None, None 


@app.route('/buscar_por_cep', methods=['POST'])
def buscar_por_cep():
    servico = request.form['query']
    cep = request.form['cep']

    endereco = buscar_endereco_por_cep(cep)
    
    if isinstance(endereco, dict):
        latitude_usuario, longitude_usuario = obter_coordenadas_por_cep(cep)

        if latitude_usuario is None or longitude_usuario is None:  
            flash('Não foi possível obter as coordenadas do usuário.')
            return redirect('/home')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''SELECT nome, categoria, latitude, longitude FROM catalogo WHERE categoria LIKE %s''', ('%' + servico + '%',))
        resultados = cursor.fetchall()

        servicos_distancias = []
        for resultado in resultados:
            nome, categoria, lat_servico, lon_servico = resultado
            
            if lat_servico is None or lon_servico is None:  
                continue  
            
            distancia = calcular_distancia(latitude_usuario, longitude_usuario, lat_servico, lon_servico)
            servicos_distancias.append((nome, categoria, distancia))
        
        servicos_distancias.sort(key=lambda x: x[2])

        cursor.close()
        conn.close()

        return render_template('search_results_cep.html', resultados=servicos_distancias)
    else:
        flash('CEP inválido.')
        return redirect('/home')



def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # Raio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
if __name__ == '__main__':
    criar_db()
    app.run(debug=True)
