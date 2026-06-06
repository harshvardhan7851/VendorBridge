# VendorBridge ERP

> **Procurement & Vendor Management ERP** — Production-ready skeleton built with FastAPI, React 18, PostgreSQL, and Docker.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [Docker Setup](#docker-setup)
4. [Alembic Workflow](#alembic-workflow)
5. [Team Development Workflow](#team-development-workflow)
6. [Git Branching Strategy](#git-branching-strategy)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │   Frontend   │───▶│   Backend    │───▶│ PostgreSQL│  │
│  │ React + Vite │    │   FastAPI    │    │   (pg16)  │  │
│  │  Port 5173   │    │  Port 8000   │    │ Port 5432 │  │
│  └──────────────┘    └──────────────┘    └───────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

| Layer      | Technology                         | Port  |
|------------|------------------------------------|-------|
| Frontend   | React 18 + TypeScript + Vite       | 5173  |
| Backend    | FastAPI + Python 3.11 + SQLAlchemy | 8000  |
| Database   | PostgreSQL 16                      | 5432  |

### Backend Architecture (FastAPI)

```
app/
├── core/          # Config, DB engine, security utilities
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic v2 request/response schemas
├── routers/       # FastAPI APIRouter endpoints
├── services/      # Business logic layer (service pattern)
├── middlewares/   # Auth, CORS, logging middleware
├── utils/         # Reusable helpers and utilities
└── templates/     # Jinja2 email templates
```

---

## Folder Structure

```
vendorbridge/
│
├── docker-compose.yml          # Orchestrates all services
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile              # Python 3.11 slim image
│   ├── requirements.txt        # All Python dependencies
│   ├── .env.example            # Environment variable template
│   ├── alembic.ini             # Alembic configuration
│   │
│   ├── alembic/
│   │   ├── env.py              # Alembic environment (async)
│   │   └── versions/           # Generated migration files (committed)
│   │
│   ├── app/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── config.py       # Settings via pydantic-settings
│   │   │   ├── database.py     # Async engine + session + Base
│   │   │   └── security.py     # JWT + password hashing stubs
│   │   ├── models/             # SQLAlchemy 2.0 ORM models
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── routers/            # FastAPI routers (endpoints)
│   │   ├── services/           # Service layer (business logic)
│   │   ├── middlewares/        # Auth + CORS middleware stubs
│   │   ├── utils/              # Helper utilities
│   │   └── templates/          # Email HTML templates
│   │
│   └── tests/
│       └── test_placeholder.py
│
└── frontend/
    ├── Dockerfile              # Node 20 + Vite dev server
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    │
    └── src/
        ├── main.tsx            # React entry point
        ├── App.tsx             # Root component + router
        ├── api/                # Axios API call functions
        ├── components/         # Reusable UI components
        ├── pages/              # Page-level components
        ├── layouts/            # Layout wrappers
        ├── hooks/              # Custom React hooks
        ├── contexts/           # React Context providers
        ├── routes/             # Route definitions + guards
        ├── types/              # TypeScript type definitions
        └── utils/              # Frontend utility helpers
```

---

## Docker Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- No local PostgreSQL or Node.js required

### Start the Project

```bash
# Clone the repository
git clone <repo-url>
cd vendorbridge

# Copy environment file
cp backend/.env.example backend/.env

# Build and start all services
docker compose up --build
```

### Service URLs

| Service  | URL                       |
|----------|---------------------------|
| Frontend | http://localhost:5173     |
| Backend  | http://localhost:8000     |
| API Docs | http://localhost:8000/docs |
| Redoc    | http://localhost:8000/redoc |

### Useful Commands

```bash
# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down

# Stop and remove volumes (CAUTION: deletes DB data)
docker compose down -v

# Rebuild a single service
docker compose up --build backend

# Access backend shell
docker compose exec backend bash

# Access database
docker compose exec postgres psql -U vendorbridge -d vendorbridge
```

---

## Alembic Workflow

Alembic handles all database migrations. All commands run **inside the backend container**.

### Initial Setup (first time only)

```bash
# Run after docker compose up --build
docker compose exec backend alembic upgrade head
```

### Create a New Migration

```bash
# Autogenerate migration from model changes
docker compose exec backend alembic revision --autogenerate -m "initial"

# Apply the migration
docker compose exec backend alembic upgrade head
```

### Other Migration Commands

```bash
# View migration history
docker compose exec backend alembic history

# Downgrade one step
docker compose exec backend alembic downgrade -1

# Downgrade to base (empty DB)
docker compose exec backend alembic downgrade base

# Show current revision
docker compose exec backend alembic current
```

### Migration Workflow for Teams

1. Pull the latest code (`git pull`)
2. Run `docker compose up --build` to get updated images
3. Run `docker compose exec backend alembic upgrade head` to apply new migrations
4. Make your model changes in `app/models/`
5. Run `docker compose exec backend alembic revision --autogenerate -m "your-description"`
6. Review the generated file in `alembic/versions/`
7. Commit the migration file with your code changes

---

## Team Development Workflow

### Adding a New Feature

1. **Branch** from `main`: `git checkout -b feature/your-feature`
2. **Backend**: Add model → schema → service → router
3. **Migrations**: Generate and review Alembic migration
4. **Frontend**: Add types → api → hooks → pages/components
5. **Test**: Run `docker compose up --build` to validate
6. **PR**: Open pull request against `main`

### Running Tests

```bash
# Backend tests
docker compose exec backend pytest tests/ -v

# Frontend type-checking
docker compose exec frontend npx tsc --noEmit
```

---

## Git Branching Strategy

```
main
├── feature/auth-vendor          # Authentication + Vendor management
├── feature/rfq-quotation        # RFQ + Quotation workflow
├── feature/approval-po-invoice  # Approval + Purchase Orders + Invoices
└── feature/frontend             # React UI implementation
```

| Branch                        | Purpose                                |
|-------------------------------|----------------------------------------|
| `main`                        | Production-ready, always deployable    |
| `feature/auth-vendor`         | Auth endpoints, JWT, Vendor CRUD       |
| `feature/rfq-quotation`       | RFQ creation, Quotation submission     |
| `feature/approval-po-invoice` | Approval workflows, PO generation      |
| `feature/frontend`            | All React UI pages and components      |

### Commit Convention

```
feat: add vendor registration endpoint
fix: correct JWT expiry calculation
chore: update alembic migration for vendor table
docs: update README with deployment steps
test: add unit tests for auth service
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the values:

| Variable                   | Description                         |
|----------------------------|-------------------------------------|
| `DATABASE_URL`             | PostgreSQL async connection string  |
| `SECRET_KEY`               | JWT signing secret (generate random)|
| `ALGORITHM`                | JWT algorithm (default: HS256)      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL in minutes             |
| `SMTP_HOST`                | Email server host                   |
| `SMTP_PORT`                | Email server port                   |
| `SMTP_USER`                | Email account username              |
| `SMTP_PASSWORD`            | Email account password              |
| `FRONTEND_URL`             | Frontend URL for CORS config        |

---

## License

MIT — See [LICENSE](LICENSE) file for details.
