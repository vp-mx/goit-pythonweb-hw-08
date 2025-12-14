# ContactHub API

REST API for managing personal and business contacts with PostgreSQL database backend.

## Features

- **CRUD operations** for contacts (Create, Read, Update, Delete)
- **Search contacts** by first name, last name, or email
- **Birthday tracking** - get contacts with upcoming birthdays (next 7 days)
- **PostgreSQL database** with SQLAlchemy ORM
- **Pydantic validation** for request/response data
- **Auto-generated API documentation** (Swagger UI)

## Requirements

- Python 3.11+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

### 1. Install uv (if not installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the repository

```bash
git clone <repository-url>
cd goit-pythonweb-hw-08
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Configure environment variables

Create `.env` file from example:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=contacthub_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 5. Set up the database

Make sure PostgreSQL is running and create the database:

```bash
createdb contacthub_db
```

Run migrations:

```bash
uv run alembic upgrade head
```

## Running the Application

### Development mode (with auto-reload)

```bash
uv run fastapi dev src/main.py
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once the application is running, visit:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### Contacts

- `POST /contacts/` - Create a new contact
- `GET /contacts/` - Get all contacts (with pagination)
- `GET /contacts/{contact_id}` - Get contact by ID
- `PUT /contacts/{contact_id}` - Update contact
- `DELETE /contacts/{contact_id}` - Delete contact

### Search

- `GET /contacts/search/?query=<search_term>` - Search contacts (min 3 characters)
- `GET /contacts/birthdays/` - Get contacts with birthdays in next 7 days

## Example Usage


### Search contacts

```bash
curl "http://127.0.0.1:8000/contacts/search/?query=john"
```

### Create new migration

```bash
uv run alembic revision --autogenerate -m "description"
```

### Apply migrations

```bash
uv run alembic upgrade head
```
