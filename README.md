#  CrediGestor API

> **Sistema de Gestão de Vendas a Prazo e Notas Promissórias**

O **CrediGestor API** é uma solução robusta de Backend desenvolvida para facilitar a administração de vendas parceladas (crediário). Ele automatiza a geração de promissórias, controla pagamentos, calcula juros, gera relatórios de inadimplência e fornece um dashboard analítico para tomada de decisão.

Construído com **FastAPI** para alta performance, **PostgreSQL** para integridade de dados e **Docker** para fácil implantação.

---

### 🌐 Acesso ao Sistema (Deploy)

O sistema está implantado e rodando em produção. Acesse através do link:
👉 **[https://credigestor-api.vercel.app/](https://credigestor-api.vercel.app/)**

---

## Funcionalidades Principais

### Autenticação e Segurança
* **Login JWT**: Autenticação segura via JSON Web Tokens.
* **Controle de Acesso (RBAC)**: Diferenciação entre perfis de **Administrador** (acesso total) e **Vendedor** (operacional).

### Gestão de Clientes
* Cadastro completo de clientes com validação de CPF.
* Histórico de compras e pagamentos.

### Vendas e Promissórias
* **Geração Automática**: Ao criar uma venda parcelada, o sistema gera automaticamente as notas promissórias correspondentes.
* **Cálculo de Parcelas**: Divisão automática do valor financiado.
* **Gestão de Status**: Acompanhamento de parcelas (Pendente, Paga, Atrasada).

### Financeiro
* **Baixa de Pagamentos**: Registro de pagamentos parciais ou totais de uma promissória.
* **Recibos**: Geração de dados para emissão de comprovantes.
* **Cálculo de Juros**: (Configurável) Aplicação de regras de juros para atrasos.

### Dashboard e Relatórios
* **Dashboard em Tempo Real**: Métricas de "Total a Receber", "Inadimplência", "Vendas do Mês".
* **Relatório de Inadimplência**: Listagem de clientes com parcelas atrasadas, filtrável por período.
* **Exportação de Dados**: Download de listagens em formato **CSV** (Clientes, Vendas, Promissórias).

### Sistema
* **Backup Automático**: Endpoint para administradores baixarem backup completo do banco de dados (ZIP).
* **Configurações Dinâmicas**: Ajuste de taxas e parâmetros do sistema via API.

---

## Stack Tecnológico

* **Linguagem**: Python 3.12
* **Framework Web**: FastAPI
* **Banco de Dados**: PostgreSQL
* **ORM**: SQLAlchemy (interação com banco)
* **Validação**: Pydantic v2
* **Testes**: Pytest (Cobertura de Testes Unitários e Integração)
* **Infraestrutura**: Docker & Docker Compose

---

## Configuração e Instalação

### 1. Pré-requisitos
* Docker e Docker Compose instalados.
* Git.

### 2. Clonar o Repositório
git clone [https://github.com/seu-usuario/credigestor-api.git](https://github.com/seu-usuario/credigestor-api.git)
cd credigestor-api

### 3. Configurar Variáveis de ambiente 
cp .env.example .env

### 4. executando com docker:
subir os serviços: docker-compose up --build -d

### 5. cobertura de testes unitários
pytest --cov=app tests/unit/






