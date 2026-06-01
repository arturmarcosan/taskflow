# =============================================================================
# TaskFlow — API REST com Flask e PostgreSQL
# Disciplina: Desenvolvimento Web / Banco de Dados
# Descrição: Backend com operações CRUD completas para gerenciamento de tarefas
# =============================================================================

from flask import Flask, request, jsonify   # Flask: framework web
from flask_cors import CORS                 # CORS: permite requisições do frontend
import psycopg2                             # Driver de conexão com PostgreSQL
import psycopg2.extras                      # Extras: RealDictCursor (retorna dicts)
import os                                   # OS: leitura de variáveis de ambiente
from datetime import datetime               # Datetime: registro de datas

# ─── Configuração da Aplicação ─────────────────────────────────────────────────

app = Flask(__name__)   # Cria a instância do servidor Flask
CORS(app)               # Habilita CORS para o frontend poder se comunicar

# URL de conexão com o banco PostgreSQL (definida como variável de ambiente)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://taskflow_db_d8ds_user:BZsJ14BsxYNSbBSJo0o4oJcBx9ZJwMEZ@dpg-d8ed4pgjs32c738c8p9g-a/taskflow_db_d8ds"
)

# ─── Funções Auxiliares ────────────────────────────────────────────────────────

def get_db():
    """
    Cria e retorna uma conexão com o banco de dados PostgreSQL.
    RealDictCursor faz cada linha retornar como dicionário Python.
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    """
    Inicializa o banco de dados criando a tabela 'tarefas' se não existir.
    Chamada automaticamente ao iniciar o servidor.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id            SERIAL PRIMARY KEY,           -- ID auto-incremento
            titulo        TEXT    NOT NULL,             -- Título obrigatório
            descricao     TEXT    DEFAULT '',           -- Descrição opcional
            status        TEXT    NOT NULL DEFAULT 'pendente',    -- Estado da tarefa
            prioridade    TEXT    NOT NULL DEFAULT 'media',       -- Nível de urgência
            criado_em     TEXT    NOT NULL,             -- Data de criação
            atualizado_em TEXT    NOT NULL              -- Data da última edição
        )
    """)
    conn.commit()   # Confirma a criação da tabela
    cursor.close()
    conn.close()

# ─── ROTAS CRUD ────────────────────────────────────────────────────────────────

# =============================================================================
# CREATE — Criar nova tarefa
# Método: POST | Rota: /tarefas
# Body: { "titulo": "...", "descricao": "...", "status": "...", "prioridade": "..." }
# =============================================================================
@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    dados = request.get_json()  # Lê o JSON enviado pelo frontend

    # Validação: título é obrigatório
    if not dados or not dados.get("titulo"):
        return jsonify({"erro": "O campo 'titulo' é obrigatório."}), 400

    agora = datetime.now().isoformat()  # Timestamp atual

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tarefas (titulo, descricao, status, prioridade, criado_em, atualizado_em)
           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
        (
            dados["titulo"],
            dados.get("descricao", ""),
            dados.get("status", "pendente"),
            dados.get("prioridade", "media"),
            agora,
            agora,
        ),
    )
    novo_id = cursor.fetchone()["id"]   # Recupera o ID gerado
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Tarefa criada com sucesso!", "id": novo_id}), 201


# =============================================================================
# READ ALL — Listar todas as tarefas
# Método: GET | Rota: /tarefas
# Query params opcionais: ?status=pendente&prioridade=alta
# =============================================================================
@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    # Lê filtros opcionais da URL
    status_filtro     = request.args.get("status")
    prioridade_filtro = request.args.get("prioridade")

    conn = get_db()
    cursor = conn.cursor()

    # Constrói a query dinamicamente com base nos filtros
    query  = "SELECT * FROM tarefas WHERE 1=1"
    params = []

    if status_filtro:
        query += " AND status = %s"
        params.append(status_filtro)

    if prioridade_filtro:
        query += " AND prioridade = %s"
        params.append(prioridade_filtro)

    query += " ORDER BY criado_em DESC"  # Mais recentes primeiro
    cursor.execute(query, params)
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([dict(t) for t in tarefas]), 200


# =============================================================================
# READ ONE — Buscar tarefa por ID
# Método: GET | Rota: /tarefas/<id>
# =============================================================================
@app.route("/tarefas/<int:id>", methods=["GET"])
def obter_tarefa(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas WHERE id = %s", (id,))
    tarefa = cursor.fetchone()
    cursor.close()
    conn.close()

    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    return jsonify(dict(tarefa)), 200


# =============================================================================
# UPDATE — Atualizar tarefa existente
# Método: PUT | Rota: /tarefas/<id>
# Body: campos que deseja alterar (parcial ou completo)
# =============================================================================
@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado."}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Verifica se a tarefa existe antes de atualizar
    cursor.execute("SELECT id FROM tarefas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    # Monta o UPDATE dinamicamente com os campos enviados
    campos  = []
    valores = []
    for campo in ["titulo", "descricao", "status", "prioridade"]:
        if campo in dados:
            campos.append(f"{campo} = %s")
            valores.append(dados[campo])

    if not campos:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Nenhum campo válido para atualizar."}), 400

    # Sempre atualiza o campo de data de modificação
    campos.append("atualizado_em = %s")
    valores.append(datetime.now().isoformat())
    valores.append(id)

    cursor.execute(f"UPDATE tarefas SET {', '.join(campos)} WHERE id = %s", valores)
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Tarefa atualizada com sucesso!"}), 200


# =============================================================================
# DELETE — Remover tarefa
# Método: DELETE | Rota: /tarefas/<id>
# =============================================================================
@app.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    conn = get_db()
    cursor = conn.cursor()

    # Verifica se existe antes de deletar
    cursor.execute("SELECT id FROM tarefas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    cursor.execute("DELETE FROM tarefas WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Tarefa deletada com sucesso!"}), 200


# =============================================================================
# STATS — Estatísticas do banco (rota bônus)
# Método: GET | Rota: /tarefas/stats
# =============================================================================
@app.route("/tarefas/stats", methods=["GET"])
def estatisticas():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM tarefas")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT status, COUNT(*) as qtd FROM tarefas GROUP BY status")
    por_status = {row["status"]: row["qtd"] for row in cursor.fetchall()}

    cursor.execute("SELECT prioridade, COUNT(*) as qtd FROM tarefas GROUP BY prioridade")
    por_prioridade = {row["prioridade"]: row["qtd"] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return jsonify({"total": total, "por_status": por_status, "por_prioridade": por_prioridade}), 200


# =============================================================================
# PENDENTES — Rota para integração com n8n (alertas por email)
# Método: GET | Rota: /tarefas/pendentes
# =============================================================================
@app.route("/tarefas/pendentes", methods=["GET"])
def tarefas_pendentes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas WHERE status != 'concluida' ORDER BY prioridade DESC")
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(t) for t in tarefas]), 200


# ─── Inicialização ─────────────────────────────────────────────────────────────

# Cria a tabela ao iniciar o servidor (seguro repetir — usa IF NOT EXISTS)
init_db()

if __name__ == "__main__":
    print("✅  Banco de dados PostgreSQL inicializado.")
    print("🚀  Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)

