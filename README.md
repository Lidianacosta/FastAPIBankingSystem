# FastAPI Banking System 🏦

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=Lidianacosta_FastAPIBankingSystem)](https://sonarcloud.io/summary/new_code?id=Lidianacosta_FastAPIBankingSystem)

Um sistema bancário RESTful completo desenvolvido com **FastAPI**, focado em abstrair a alta performance de requisições assíncronas para o gerenciamento de clientes, contas correntes e transações financeiras garantindo uma segurança robusta via autenticação JWT.

## 🌐 Demo & Aplicação Frontend

Para uma experiência completa com interface gráfica, acesse:

- **Aplicação Live (Demo):** [frontend-banking-system.vercel.app](https://frontend-banking-system.vercel.app)
- **Repositório Frontend:** [Lidianacosta/FrontendBankingSystem](https://github.com/Lidianacosta/FrontendBankingSystem)

## 🚀 Funcionalidades Principais

- **Autenticação e Perfis de Usuário**:
  - Segurança de ponta com geração de token JWT OAuth2.
  - Bloqueio de novos cadastros públicos: a criação de usuário gerente é feita exclusivamente via linha de comando (CLI) garantindo proteção do sistema.
  - Perfil restrito onde o usuário pode visualizar e atualizar seus próprios dados de forma isolada.
- **Gestão de Acerto (Clientes e Contas)**:
  - Cadastro interligado: a criação do `IndividualClient` já provisiona automaticamente a base `Client`.
  - Controle rígido de duplicação: validação por CPF único para evitar redundâncias na base.
  - Contas Correntes segmentadas com trava de limite dinâmico e limite diário de saque.
  - Cascata Inteligente: a exclusão de clientes ou contas afaga todos os registros órfãos garantindo a limpeza do banco.
- **Transações Financeiras (Deposits & Withdrawals)**:
  - Registro imutável de transações financeiras acoplados diretamente ao saldo.
  - Regra de Saque Seguro: Todo saque desconta o saldo final da conta, necessitando de um usuário ativo/autenticado.
- **Ambiente Moderno**:
  - Banco de Dados assíncrono mantido via **AIOSQLite**.
  - Migrações dinâmicas auto-referenciadas utilizando **Alembic** e **SQLModel**.

## 🛠 Tecnologias Utilizadas

- [**Python 3.12+**](https://www.python.org/): Linguagem base do projeto.
- [**FastAPI**](https://fastapi.tiangolo.com/): Framework web assíncrono de alta performance.
- [**SQLModel**](https://sqlmodel.tiangolo.com/): ORM moderno unindo o melhor do SQLAlchemy e do Pydantic.
- [**Alembic**](https://alembic.sqlalchemy.org/): Ferramenta para gerenciar migrações de banco de dados.
- [**PyJWT & PwdLib**](https://pyjwt.readthedocs.io/): Para segurança de senhas via Argon2 e tokens de longa duração.
- [**uv**](https://github.com/astral-sh/uv): Gerenciamento eficiente e ultrarrápido de dependências do Python.

**Painel Swagger Interativo**
_Acesse diretamente via `/docs` para visualizar todas as rotas e realizar testes rápidos da sua API com OAuth2 integrado nas requisições._

**Coleção Insomnia Pronta**
_No diretório `docs/`, está disponível a collection [`insomnia_collection.yaml`](docs/insomnia_collection.yaml) contendo todas as requisições, variáveis de ambientes isoladas e scripts para captar os IDs das respostas e alimentar as sub-requisições (Evitando copiar e colar o `client_id` na mão em cada teste)!_

---

Este projeto utiliza `uv` para gerenciamento de dependências, garantindo instalações extremamente rápidas.

### Pré-requisitos

- Python 3.12+ instalado.
- [uv](https://github.com/astral-sh/uv) instalado no sistema operacional.

### Passo a Passo

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/Lidianacosta/FastAPIBankingSystem.git
   cd FastAPIBankingSystem
   ```

2. **Crie e ative o ambiente virtual:**

   ```bash
   # Sincroniza e baixa todos os pacotes em milissegundos
   uv sync
   ```

3. **Configure as variáveis de ambiente:**

   ```bash
   cp .env.example .env
   # Edite o .env caso queira mudar a secret ou configurações de banco
   ```

4. **Aplique as migrações (Criação das Tabelas):**

   ```bash
   uv run alembic upgrade head
   ```

5. **Crie um superusuário (Via Linha de Comando de Segurança):**

   ```bash
   uv run python -m src.commands.create_user
   ```

6. **Inicie o servidor localmente:**

   ```bash
   uv run fastapi dev src/main.py
   ```

Acesse a documentação interativa em `http://127.0.0.1:8000/docs` para autenticar o usuário que você acabou de criar e gerenciar todo o banco!

## 📸 Visão do Sistema (API)

Por ser uma aplicação de backend puramente REST, a visualização gráfica acontece diretamente pelas documentações interativas geradas.

![](./docs/imgs/Screenshot%20from%202026-04-01%2015-15-28.png)
![](./docs/imgs/Screenshot%20from%202026-04-01%2015-15-35.png)
![](./docs/imgs/Screenshot%20from%202026-04-01%2015-15-46.png)
