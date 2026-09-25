link Web Directa 
https://voting-api-yvpr.onrender.com/docs?utm_source=chatgpt.com#/Votes/voting_statistics_votes_statistics_get

# Voting System API

API RESTful desarrollada con Python, FastAPI, SQLAlchemy y PostgreSQL para gestionar votantes, candidatos y votos.

## Requisitos

- Python 3.11+
- Docker Desktop
- Git

## 1. Clonar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd voting_api
```

## 2. Crear entorno virtual

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Crear PostgreSQL

```bash
docker compose up -d
```

Copiar `.env.example` como `.env`.

## 5. Ejecutar API

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

- http://127.0.0.1:8000
- Documentación Swagger: http://127.0.0.1:8000/docs
- Documentación ReDoc: http://127.0.0.1:8000/redoc

## Endpoints

### Votantes

- `POST /voters`
- `GET /voters`
- `GET /voters/{id}`
- `DELETE /voters/{id}`

### Candidatos

- `POST /candidates`
- `GET /candidates`
- `GET /candidates/{id}`
- `DELETE /candidates/{id}`

### Votos

- `POST /votes`
- `GET /votes`
- `GET /votes/statistics`

## Ejemplos con curl

### Crear candidato

```bash
curl -X POST "http://127.0.0.1:8000/candidates" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Ana Perez\",\"party\":\"Partido A\"}"
```

### Crear votante

```bash
curl -X POST "http://127.0.0.1:8000/voters" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Carlos Gomez\",\"email\":\"carlos@example.com\"}"
```

### Emitir voto

```bash
curl -X POST "http://127.0.0.1:8000/votes" ^
  -H "Content-Type: application/json" ^
  -d "{\"voter_id\":1,\"candidate_id\":1}"
```

### Ver estadísticas

```bash
curl "http://127.0.0.1:8000/votes/statistics"
```

## Reglas de negocio

1. El email del votante es único.
2. Una persona no puede existir simultáneamente como votante y candidato.
3. Un votante solo puede votar una vez.
4. Al votar se actualiza `has_voted`.
5. Al votar se incrementa `Candidate.votes`.
6. La base de datos tiene una restricción `UNIQUE` sobre `Vote.voter_id` como protección adicional contra votos duplicados.
7. No se elimina un votante que ya votó.
8. No se elimina un candidato que ya tiene votos, evitando alterar las estadísticas históricas.

## Capturas solicitadas

Para la entrega, abrir `/docs`, ejecutar las peticiones y tomar capturas de:

1. Creación de votantes.
2. Creación de candidatos.
3. Emisión de votos.
4. `/votes/statistics`.
5. Error al intentar votar dos veces.

## Nota

La prueba permite SQL (MySQL/PostgreSQL) o NoSQL (MongoDB). Este proyecto usa PostgreSQL.
