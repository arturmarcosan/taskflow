# 🧭 Passo a Passo — TaskFlow

Guia completo para instalar, rodar e publicar o projeto no GitHub.

---

## PARTE 1 — Configuração Local

### Passo 1 · Instalar o Python

1. Acesse **https://www.python.org/downloads/**
2. Baixe a versão **3.8 ou superior**
3. No instalador Windows, **marque a opção "Add Python to PATH"** antes de instalar
4. Verifique a instalação abrindo o terminal e digitando:

```bash
python --version
# deve aparecer: Python 3.x.x
```

---

### Passo 2 · Baixar o Projeto

Extraia o arquivo `.zip` do projeto para uma pasta de sua preferência.  
A estrutura deve ficar assim:

```
taskflow/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   └── index.html
└── README.md
```

---

### Passo 3 · Criar o Ambiente Virtual (recomendado)

Abra o terminal **dentro da pasta `backend`**:

```bash
cd taskflow/backend
```

Crie o ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

> ✅ Quando ativado, o terminal mostrará `(venv)` no início da linha.

---

### Passo 4 · Instalar as Dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

Isso instalará:
- `flask` — servidor web
- `flask-cors` — permite o frontend se comunicar com o backend

---

### Passo 5 · Iniciar o Backend

Ainda na pasta `backend`, execute:

```bash
python app.py
```

Saída esperada no terminal:

```
✅  Banco de dados inicializado.
🚀  Servidor rodando em http://localhost:5000
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

> O arquivo `tarefas.db` será criado automaticamente na primeira execução.

---

### Passo 6 · Abrir o Frontend

Sem fechar o terminal do backend, abra o arquivo `frontend/index.html` no seu navegador.

> **Windows:** clique duas vezes no arquivo  
> **Linux/macOS:** `open frontend/index.html` ou arraste para o navegador

A interface do TaskFlow estará funcionando e conectada ao backend.

---

### ✅ Testando o CRUD manualmente

Você pode testar a API diretamente pelo terminal com o comando `curl`:

```bash
# Criar uma tarefa (CREATE)
curl -X POST http://localhost:5000/tarefas \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Minha primeira tarefa","prioridade":"alta"}'

# Listar todas (READ)
curl http://localhost:5000/tarefas

# Atualizar status (UPDATE)
curl -X PUT http://localhost:5000/tarefas/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"concluida"}'

# Excluir (DELETE)
curl -X DELETE http://localhost:5000/tarefas/1
```

---

## PARTE 2 — Publicando no GitHub

### Passo 7 · Instalar o Git

1. Acesse **https://git-scm.com/downloads** e instale para seu sistema
2. Verifique:

```bash
git --version
# deve aparecer: git version x.x.x
```

3. Configure seu nome e e-mail (apenas na primeira vez):

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

---

### Passo 8 · Criar o Repositório no GitHub

1. Acesse **https://github.com** e faça login (ou crie uma conta)
2. Clique no botão **"New"** (ou o `+` no canto superior direito → "New repository")
3. Preencha:
   - **Repository name:** `taskflow`
   - **Description:** `Aplicação Web CRUD com Python Flask e SQLite`
   - Marque **"Public"**
   - **NÃO** marque "Add a README file" (já temos um)
4. Clique em **"Create repository"**

---

### Passo 9 · Inicializar o Git Local

No terminal, navegue até a **pasta raiz do projeto** (`taskflow/`):

```bash
cd taskflow
```

Inicialize o repositório Git:

```bash
git init
```

---

### Passo 10 · Fazer o Primeiro Commit

```bash
# Adiciona todos os arquivos ao "stage"
git add .

# Cria o primeiro commit
git commit -m "feat: projeto inicial TaskFlow — CRUD com Flask e SQLite"
```

---

### Passo 11 · Conectar ao GitHub e Fazer o Push

Copie a URL do seu repositório no GitHub (aparece na tela após criar — algo como `https://github.com/SEU_USUARIO/taskflow.git`) e execute:

```bash
# Conecta o repositório local ao GitHub
git remote add origin https://github.com/SEU_USUARIO/taskflow.git

# Define a branch principal
git branch -M main

# Envia o código para o GitHub
git push -u origin main
```

> ⚠️ **Atenção:** O GitHub **não aceita mais senha** para autenticação via terminal desde 2021.  
> Quando solicitado, informe seu **usuário** e um **token de acesso pessoal (PAT)** no lugar da senha.  
>
> Para gerar seu token:  
> **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token**  
> Marque a permissão `repo` e copie o token gerado (ele só aparece uma vez).

---

### Passo 12 · Verificar no GitHub

Acesse `https://github.com/SEU_USUARIO/taskflow` — o projeto estará publicado com o README formatado!

---

## PARTE 3 — Fluxo de Versionamento

Para cada nova alteração no projeto, siga este ciclo:

```bash
# 1. Ver o que mudou
git status

# 2. Adicionar as mudanças
git add .

# 3. Criar um commit descritivo
git commit -m "tipo: descrição breve da mudança"

# 4. Enviar para o GitHub
git push
```

### Tipos de commit (boas práticas)

| Tipo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Alteração em documentação |
| `style:` | Mudança visual/CSS |
| `refactor:` | Refatoração de código |
| `chore:` | Ajustes gerais |

### Exemplos

```bash
git commit -m "feat: adiciona filtro por data de criação"
git commit -m "fix: corrige erro ao deletar tarefa inexistente"
git commit -m "docs: atualiza README com instruções de instalação"
git commit -m "style: melhora responsividade do formulário"
```

---

## Resumo dos Comandos

```bash
# ── Configuração inicial ───────────────────────────────────
python -m venv venv               # cria ambiente virtual
venv\Scripts\activate             # ativa (Windows)
source venv/bin/activate          # ativa (Linux/macOS)
pip install -r requirements.txt   # instala dependências

# ── Rodar o projeto ────────────────────────────────────────
python app.py                     # inicia o backend

# ── Git básico ─────────────────────────────────────────────
git init                          # inicializa repositório
git add .                         # prepara arquivos
git commit -m "mensagem"          # salva versão
git push                          # envia ao GitHub
git status                        # mostra o que mudou
git log --oneline                 # histórico de commits
```
