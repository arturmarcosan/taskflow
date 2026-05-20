# 📋 TaskFlow — Gerenciador de Tarefas

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/Licença-MIT-green?style=for-the-badge)

**Aplicação Web Full Stack com operações CRUD completas**  
Backend em Python · Banco de Dados SQLite · Frontend em HTML/CSS/JS

</div>

---

## 📌 Sobre o Projeto

O **TaskFlow** é uma aplicação web de gerenciamento de tarefas desenvolvida como projeto acadêmico para a disciplina de Desenvolvimento Web / Banco de Dados.

A aplicação demonstra na prática as quatro operações fundamentais de banco de dados:

| Operação | Descrição | Endpoint |
|---|---|---|
| 🟢 **Create** | Criação de novas tarefas | `POST /tarefas` |
| 🔵 **Read** | Listagem e busca de tarefas | `GET /tarefas` · `GET /tarefas/<id>` |
| 🟡 **Update** | Edição de tarefas existentes | `PUT /tarefas/<id>` |
| 🔴 **Delete** | Remoção de tarefas | `DELETE /tarefas/<id>` |

---

## 🗂️ Estrutura do Projeto

```
taskflow/
│
├── 📁 backend/
│   ├── 🐍 app.py              # API REST — rotas CRUD
│   ├── 📄 requirements.txt    # Dependências Python
│   └── 🗄️  tarefas.db         # Banco SQLite (gerado automaticamente)
│
├── 📁 frontend/
│   └── 🌐 index.html          # Interface Web (HTML + CSS + JS)
│
└── 📖 README.md
```

---

## 🛠️ Tecnologias

### Backend
- **[Python 3](https://www.python.org/)** — Linguagem principal
- **[Flask](https://flask.palletsprojects.com/)** — Microframework web para a API REST
- **[Flask-CORS](https://flask-cors.readthedocs.io/)** — Libera requisições cross-origin do frontend
- **[SQLite3](https://docs.python.org/3/library/sqlite3.html)** — Banco de dados relacional embutido no Python (sem instalação)

### Frontend
- **HTML5** — Estrutura da página
- **CSS3** — Estilização (variáveis CSS, animações, responsividade)
- **JavaScript (ES6+)** — Lógica e chamadas à API via `fetch()`

### Comunicação
- **API REST** — Comunicação via JSON entre frontend e backend

---

## 🚀 Como Executar

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/taskflow.git
cd taskflow
```

### 2. Configure o ambiente Python

```bash
cd backend

# Crie um ambiente virtual
python -m venv venv

# Ative — Windows:
venv\Scripts\activate
# Ative — Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Inicie o servidor

```bash
python app.py
```

Você verá:
```
✅  Banco de dados inicializado.
🚀  Servidor rodando em http://localhost:5000
```

### 4. Abra o frontend

Abra o arquivo `frontend/index.html` diretamente no navegador.

> ⚠️ O backend precisa estar rodando para o frontend funcionar.

---

## 📡 Documentação da API

### Base URL
```
http://localhost:5000
```

### `POST /tarefas` — Criar tarefa

**Body:**
```json
{
  "titulo": "Estudar para a prova",
  "descricao": "Revisar capítulos 3 e 4",
  "status": "pendente",
  "prioridade": "alta"
}
```
**Resposta `201`:** `{ "mensagem": "Tarefa criada com sucesso!", "id": 1 }`

### `GET /tarefas` — Listar tarefas
Parâmetros opcionais: `?status=pendente` · `?prioridade=alta`

### `GET /tarefas/<id>` — Buscar por ID

### `PUT /tarefas/<id>` — Atualizar tarefa
Envie apenas os campos a alterar: `{ "status": "concluida" }`

### `DELETE /tarefas/<id>` — Excluir tarefa

### `GET /tarefas/stats` — Estatísticas *(bônus)*

---

## 🗄️ Banco de Dados

```sql
CREATE TABLE tarefas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo        TEXT    NOT NULL,
    descricao     TEXT,
    status        TEXT    NOT NULL DEFAULT 'pendente',
    prioridade    TEXT    NOT NULL DEFAULT 'media',
    criado_em     TEXT    NOT NULL,
    atualizado_em TEXT    NOT NULL
);
```

| Campo | Valores aceitos |
|---|---|
| `status` | `pendente` · `em andamento` · `concluida` |
| `prioridade` | `baixa` · `media` · `alta` |

---

## 📁 Histórico de Versões

### v1.0.0 — Lançamento inicial
- ✅ API REST completa com CRUD
- ✅ Banco de dados SQLite com inicialização automática
- ✅ Interface web responsiva
- ✅ Filtros por status e prioridade
- ✅ Dashboard de estatísticas
- ✅ Suporte a CORS

---

## 📝 Licença

Este projeto está sob a licença MIT.

---

<div align="center">
Feito com ❤️ para fins acadêmicos
</div>
