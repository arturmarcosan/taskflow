from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

DB_PATH = "tarefas.db"

# ─── Inicialização do Banco de Dados ───────────────────────────────────────────

def init_db():
    """Cria o banco de dados e a tabela se não existirem."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT    NOT NULL,
            descricao   TEXT,
            status      TEXT    NOT NULL DEFAULT 'pendente',
            prioridade  TEXT    NOT NULL DEFAULT 'media',
            criado_em   TEXT    NOT NULL,
            atualizado_em TEXT  NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    """Retorna uma conexão com row_factory para dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─── Rotas CRUD ────────────────────────────────────────────────────────────────

# CREATE – POST /tarefas
@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    dados = request.get_json()

    if not dados or not dados.get("titulo"):
        return jsonify({"erro": "O campo 'titulo' é obrigatório."}), 400

    agora = datetime.now().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tarefas (titulo, descricao, status, prioridade, criado_em, atualizado_em)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            dados["titulo"],
            dados.get("descricao", ""),
            dados.get("status", "pendente"),
            dados.get("prioridade", "media"),
            agora,
            agora,
        ),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return jsonify({"mensagem": "Tarefa criada com sucesso!", "id": novo_id}), 201


# READ ALL – GET /tarefas
@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    status_filtro    = request.args.get("status")
    prioridade_filtro = request.args.get("prioridade")

    conn   = get_db()
    cursor = conn.cursor()

    query  = "SELECT * FROM tarefas WHERE 1=1"
    params = []

    if status_filtro:
        query += " AND status = ?"
        params.append(status_filtro)
    if prioridade_filtro:
        query += " AND prioridade = ?"
        params.append(prioridade_filtro)

    query += " ORDER BY criado_em DESC"
    cursor.execute(query, params)
    tarefas = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(tarefas), 200


# READ ONE – GET /tarefas/<id>
@app.route("/tarefas/<int:id>", methods=["GET"])
def obter_tarefa(id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas WHERE id = ?", (id,))
    tarefa = cursor.fetchone()
    conn.close()

    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    return jsonify(dict(tarefa)), 200


# UPDATE – PUT /tarefas/<id>
@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado."}), 400

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tarefas WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    campos   = []
    valores  = []
    permitidos = ["titulo", "descricao", "status", "prioridade"]

    for campo in permitidos:
        if campo in dados:
            campos.append(f"{campo} = ?")
            valores.append(dados[campo])

    if not campos:
        conn.close()
        return jsonify({"erro": "Nenhum campo válido para atualizar."}), 400

    campos.append("atualizado_em = ?")
    valores.append(datetime.now().isoformat())
    valores.append(id)

    cursor.execute(f"UPDATE tarefas SET {', '.join(campos)} WHERE id = ?", valores)
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Tarefa atualizada com sucesso!"}), 200


# DELETE – DELETE /tarefas/<id>
@app.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tarefas WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    cursor.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Tarefa deletada com sucesso!"}), 200


# ─── Rota de Estatísticas (bônus) ──────────────────────────────────────────────
@app.route("/tarefas/stats", methods=["GET"])
def estatisticas():
    conn   = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM tarefas")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT status, COUNT(*) as qtd FROM tarefas GROUP BY status")
    por_status = {row["status"]: row["qtd"] for row in cursor.fetchall()}

    cursor.execute("SELECT prioridade, COUNT(*) as qtd FROM tarefas GROUP BY prioridade")
    por_prioridade = {row["prioridade"]: row["qtd"] for row in cursor.fetchall()}

    conn.close()
    return jsonify({"total": total, "por_status": por_status, "por_prioridade": por_prioridade}), 200


# ─── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("✅  Banco de dados inicializado.")
    print("🚀  Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
