from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os 

load_dotenv()

app = Flask(__name__)
app.secret_key = "segrede_super_seguro"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="joao120150",
    database="loja_cliente"
)

cursor = db.cursor(dictionary=True)

# Rota inicial
@app.route("/")
def index():
    if "cliente_id" in session:
        return redirect(url_for("pagina_home"))  # redireciona para a nova tela principal
    return redirect(url_for("login"))

# Cadastro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        cursor.execute("INSERT INTO clientes (nome, email, senha_hash) VALUES (%s, %s, %s)", (nome, email, senha))
        db.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        cursor.execute("SELECT * FROM clientes WHERE email = %s", (email,))
        cliente = cursor.fetchone()
        if cliente and check_password_hash(cliente["senha_hash"], senha):
            session["cliente_id"] = cliente["id"]
            session["cliente_nome"] = cliente["nome"]
            return redirect(url_for("pagina_home"))  # redireciona para a nova tela principal
        return "Login inválido"
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# NOVA tela inicial após login
@app.route("/home")
def pagina_home():  # <- renomeada para evitar conflito com '/'
    if "cliente_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", nome=session["cliente_nome"])

# Produtos
@app.route("/produtos")
def produtos():
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    return render_template("produtos.html", produtos=produtos)

# Carrinho
@app.route("/carrinho")
def carrinho():
    return render_template("carrinho.html")

# Pedidos
@app.route("/pedidos")
def pedidos():
    if "cliente_id" not in session:
        return redirect(url_for("login"))
    cursor.execute("""
        SELECT p.id, p.data_pedido, p.status, SUM(i.quantidade * pr.preco) AS total
        FROM pedidos p
        JOIN itens_pedido i ON p.id = i.pedido_id
        JOIN produtos pr ON i.produto_id = pr.id
        WHERE p.cliente_id = %s
        GROUP BY p.id, p.data_pedido, p.status
        ORDER BY p.data_pedido DESC
    """, (session["cliente_id"],))
    pedidos = cursor.fetchall()
    return render_template("pedidos.html", pedidos=pedidos)

# Criar pedido
@app.route("/criar_pedido", methods=["POST"])
def criar_pedido():
    data = request.json
    itens = data["itens"]
    cliente_id = session["cliente_id"]

    cursor.execute("INSERT INTO pedidos (cliente_id, data_pedido) VALUES (%s, %s)", (cliente_id, datetime.now()))
    pedido_id = cursor.lastrowid

    for item in itens:
        cursor.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade) VALUES (%s, %s, %s)",
                       (pedido_id, item["produto_id"], item["quantidade"]))
    db.commit()
    return jsonify({"success": True, "pedido_id": pedido_id})

if __name__ == "__main__":
    app.run(debug=True)
