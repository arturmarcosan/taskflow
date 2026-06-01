# =============================================================================
# TaskFlow — API REST com Flask, PostgreSQL e Autenticacao por Sessao
# =============================================================================

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "taskflow_secret_2025"  # Chave para sessoes
CORS(app, supports_credentials=True)     # Credentials necessario para sessoes

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://taskflow_db_d8ds_user:BZsJ14BsxYNSbBSJo0o4oJcBx9ZJwMEZ@dpg-d8ed4pgjs32c738c8p9g-a/taskflow_db_d8ds"
)

# ─── Auxiliares ───────────────────────────────────────────────────────────────

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def hash_senha(senha):
    """Criptografa a senha com SHA-256."""
    return hashlib.sha256(senha.encode()).hexdigest()

def usuario_logado():
    """Retorna o ID do usuario logado ou None."""
    return session.get("usuario_id")

def init_db():
    """Cria as tabelas necessarias."""
    conn = get_db()
    cursor = conn.cursor()

    # Tabela de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id         SERIAL PRIMARY KEY,
            nome       TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            senha      TEXT NOT NULL,
            criado_em  TEXT NOT NULL
        )
    """)

    # Tabela de tarefas (com usuario_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id            SERIAL PRIMARY KEY,
            usuario_id    INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            titulo        TEXT NOT NULL,
            descricao     TEXT DEFAULT '',
            status        TEXT NOT NULL DEFAULT 'pendente',
            prioridade    TEXT NOT NULL DEFAULT 'media',
            criado_em     TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ─── AUTH ─────────────────────────────────────────────────────────────────────

@app.route("/auth/cadastro", methods=["POST"])
def cadastro():
    dados = request.get_json()
    if not dados or not all(k in dados for k in ["nome", "email", "senha"]):
        return jsonify({"erro": "Nome, email e senha sao obrigatorios."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (dados["email"],))
    if cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({"erro": "Email ja cadastrado."}), 409

    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, criado_em) VALUES (%s, %s, %s, %s) RETURNING id",
        (dados["nome"], dados["email"], hash_senha(dados["senha"]), datetime.now().isoformat())
    )
    novo_id = cursor.fetchone()["id"]
    conn.commit(); cursor.close(); conn.close()

    session["usuario_id"] = novo_id
    session["usuario_nome"] = dados["nome"]
    return jsonify({"mensagem": "Cadastro realizado!", "nome": dados["nome"]}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados or not all(k in dados for k in ["email", "senha"]):
        return jsonify({"erro": "Email e senha sao obrigatorios."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s",
                   (dados["email"], hash_senha(dados["senha"])))
    usuario = cursor.fetchone()
    cursor.close(); conn.close()

    if not usuario:
        return jsonify({"erro": "Email ou senha incorretos."}), 401

    session["usuario_id"]   = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    return jsonify({"mensagem": "Login realizado!", "nome": usuario["nome"]}), 200


@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensagem": "Logout realizado!"}), 200


@app.route("/auth/me", methods=["GET"])
def me():
    uid = usuario_logado()
    if not uid:
        return jsonify({"erro": "Nao autenticado."}), 401
    return jsonify({"usuario_id": uid, "nome": session.get("usuario_nome")}), 200

# ─── CRUD TAREFAS ─────────────────────────────────────────────────────────────

@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    uid = usuario_logado()
    if not uid: return jsonify({"erro": "Nao autenticado."}), 401

    dados = request.get_json()
    if not dados or not dados.get("titulo"):
        return jsonify({"erro": "Titulo e obrigatorio."}), 400

    agora = datetime.now().isoformat()
    conn = get_db(); cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tarefas (usuario_id, titulo, descricao, status, prioridade, criado_em, atualizado_em)
           VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
        (uid, dados["titulo"], dados.get("descricao",""),
         dados.get("status","pendente"), dados.get("prioridade","media"), agora, agora)
    )
    novo_id = cursor.fetchone()["id"]
    conn.commit(); cursor.close(); conn.close()
    return jsonify({"mensagem": "Tarefa criada!", "id": novo_id}), 201


@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    uid = usuario_logado()
    if not uid: return jsonify({"erro": "Nao autenticado."}), 401

    status_f = request.args.get("status")
    prio_f   = request.args.get("prioridade")

    conn = get_db(); cursor = conn.cursor()
    query  = "SELECT * FROM tarefas WHERE usuario_id = %s"
    params = [uid]
    if status_f: query += " AND status = %s"; params.append(status_f)
    if prio_f:   query += " AND prioridade = %s"; params.append(prio_f)
    query += " ORDER BY criado_em DESC"
    cursor.execute(query, params)
    tarefas = [dict(t) for t in cursor.fetchall()]
    cursor.close(); conn.close()
    return jsonify(tarefas), 200


@app.route("/tarefas/<int:id>", methods=["GET"])
def obter_tarefa(id):
    uid = usuario_logado()
    if not uid: return jsonify({"erro": "Nao autenticado."}), 401
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas WHERE id = %s AND usuario_id = %s", (id, uid))
    tarefa = cursor.fetchone()
    cursor.close(); conn.close()
    if not tarefa: return jsonify({"erro": "Tarefa nao encontrada."}), 404
    return jsonify(dict(tarefa)), 200


@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    uid = usuario_logado()
    if not uid: return jsonify({"erro": "Nao autenticado."}), 401

    dados = request.get_json()
    if not dados: return jsonify({"erro": "Nenhum dado enviado."}), 400

    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id FROM tarefas WHERE id = %s AND usuario_id = %s", (id, uid))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({"erro": "Tarefa nao encontrada."}), 404

    campos = []; valores = []
    for campo in ["titulo", "descricao", "status", "prioridade"]:
        if campo in dados:
            campos.append(f"{campo} = %s"); valores.append(dados[campo])

    if not campos:
        cursor.close(); conn.close()
        return jsonify({"erro": "Nenhum campo valido."}), 400

    campos.append("atualizado_em = %s"); valores.append(datetime.now().isoformat())
    valores.append(id); valores.append(uid)
    cursor.execute(f"UPDATE tarefas SET {', '.join(campos)} WHERE id = %s AND usuario_id = %s", valores)
    conn.commit(); cursor.close(); conn.close()
    return jsonify({"mensagem": "Tarefa atualizada!"}), 200


@app.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    uid = usuario_logado()
    if not uid: return jsonify({"erro": "Nao autenticado."}), 401
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id FROM tarefas WHERE id = %s AND usuario_id = %s", (id, uid))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({"erro": "Tarefa nao encontrada."}), 404
    cursor.execute("DELETE FROM tarefas WHERE id = %s AND usuario_id = %s", (id, uid))
    conn.commit(); cursor.close(); conn.close()
    return jsonify({"mensagem": "Tarefa deletada!"}), 200


@app.route("/tarefas/stats", methods=["GET"])
def estatisticas():
    uid = usuario_logado()
    if not uid: return jsonify({"erro": "Nao autenticado."}), 401
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tarefas WHERE usuario_id = %s", (uid,))
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT status, COUNT(*) as qtd FROM tarefas WHERE usuario_id = %s GROUP BY status", (uid,))
    por_status = {r["status"]: r["qtd"] for r in cursor.fetchall()}
    cursor.execute("SELECT prioridade, COUNT(*) as qtd FROM tarefas WHERE usuario_id = %s GROUP BY prioridade", (uid,))
    por_prioridade = {r["prioridade"]: r["qtd"] for r in cursor.fetchall()}
    cursor.close(); conn.close()
    return jsonify({"total": total, "por_status": por_status, "por_prioridade": por_prioridade}), 200


# ─── ROTA PARA O n8n ──────────────────────────────────────────────────────────
# O n8n chama essa rota para buscar todos os usuarios e suas tarefas pendentes
# e envia o email personalizado para cada um

@app.route("/n8n/alertas", methods=["GET"])
def alertas_n8n():
    """Retorna lista de usuarios com tarefas pendentes para o n8n disparar emails."""
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("""
        SELECT u.nome, u.email, COUNT(t.id) as total_pendentes
        FROM usuarios u
        JOIN tarefas t ON t.usuario_id = u.id
        WHERE t.status != 'concluida'
        GROUP BY u.id, u.nome, u.email
        HAVING COUNT(t.id) > 0
    """)
    dados = [dict(r) for r in cursor.fetchall()]
    cursor.close(); conn.close()
    return jsonify(dados), 200


# ─── INIT ─────────────────────────────────────────────────────────────────────

init_db()

if __name__ == "__main__":
    print("Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
