# EventSync API

API REST desenvolvida em FastAPI para gerenciamento de eventos e inscrições.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **MongoDB** - Banco de dados NoSQL
- **Motor** - Driver assíncrono do MongoDB
- **Pydantic** - Validação de dados
- **JWT** - Autenticação com tokens
- **Bcrypt** - Hash de senhas
- **SlowAPI** - Rate limiting

## 📁 Estrutura do Projeto

```
EventSyncBackEnd/
├── config/
│   ├── database.py          # Configuração do MongoDB
│   └── settings.py          # Configurações gerais
├── schemas/
│   ├── user_schema.py       # Modelos de usuário
│   ├── event_schema.py      # Modelos de evento
│   ├── registration_schema.py  # Modelos de inscrição
│   └── common_schema.py     # Modelos comuns
├── repositories/
│   ├── user_repository.py      # Operações de BD - usuários
│   ├── event_repository.py     # Operações de BD - eventos
│   └── registration_repository.py  # Operações de BD - inscrições
├── services/
│   ├── auth_service.py      # Lógica de autenticação
│   ├── event_service.py     # Lógica de eventos
│   ├── registration_service.py  # Lógica de inscrições
│   └── user_service.py      # Lógica de usuários
├── routers/
│   ├── auth_router.py       # Endpoints de autenticação
│   ├── event_router.py      # Endpoints de eventos
│   ├── registration_router.py  # Endpoints de inscrições
│   └── user_router.py       # Endpoints de usuários
├── middlewares/
│   ├── auth_middleware.py   # Middleware de autenticação
│   └── rate_limit.py        # Middleware de rate limiting
├── utils/
│   ├── auth.py              # Funções de autenticação
│   └── exceptions.py        # Exceções customizadas
├── main.py                  # Aplicação principal
├── requirements.txt         # Dependências
└── .env.example            # Exemplo de variáveis de ambiente
```

## 🛠️ Instalação

1. **Instale as dependências**
```bash
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente**
```bash
cp .env .env
```

Edite o arquivo `.env` com suas configurações do MongoDB:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=eventsync
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=3001
ALLOWED_ORIGINS=http://localhost:3000
```

3. **Execute a aplicação**
```bash
uvicorn main:app --reload --port 3001
```

A API estará disponível em: `http://localhost:3001`

## 📚 Documentação da API

Após iniciar a aplicação, acesse:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## 🔐 Endpoints Principais

### Autenticação
- `POST /auth/register` - Registrar usuário
- `POST /auth/login` - Login

### Eventos
- `GET /events` - Listar eventos
- `GET /events/{id}` - Detalhes do evento
- `GET /events/userEvents` - Eventos do usuário (autenticado)
- `POST /events/{id}/register` - Inscrever em evento (autenticado)

### Inscrições
- `POST /registrations/{id}/cancel` - Cancelar inscrição (autenticado)

### Usuários
- `POST /users/{id}/friend-request` - Enviar solicitação de amizade (autenticado)

## 🔑 Autenticação

Use JWT no header: `Authorization: Bearer {token}`
