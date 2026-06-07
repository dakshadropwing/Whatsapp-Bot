# 🤖 AI WhatsApp Automation Platform

> Enterprise-grade, multi-tenant AI-powered WhatsApp Automation Platform for companies providing AI Agents, Automation, and ML services.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Clients / WhatsApp                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │  WhatsApp Business Cloud API
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Nginx (TLS Termination)                     │
│                     Rate Limiting · CORS                        │
└──────┬────────────────────────────────────────────┬────────────┘
       │                                            │
       ▼                                            ▼
┌──────────────┐                         ┌──────────────────────┐
│  Flask API   │                         │   React Dashboard    │
│  (Gunicorn)  │                         │   (Vite + Tailwind)  │
└──────┬───────┘                         └──────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Service Layer                            │
│  Auth · Conversation · AI · Workflow · Ticket · Analytics       │
└──────┬────────────────────────────┬────────────────────────────┘
       │                            │
       ▼                            ▼
┌──────────────┐           ┌────────────────────────────────────┐
│  PostgreSQL  │           │            Celery Workers           │
│  + pgvector  │           │   AI Tasks · Workflows · Notifs    │
└──────────────┘           └──────────────┬─────────────────────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │    Redis     │
                                   │  Broker/Cache│
                                   └──────────────┘
                                          │
                                          ▼
                            ┌─────────────────────────────┐
                            │       AI Provider Layer      │
                            │     Gemini · Ollama          │
                            └─────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7

### 1. Clone & Configure
```bash
git clone <repo-url>
cd Whatsapp-Bot
cp .env.example .env
# Fill in all required values in .env
```

### 2. Start with Docker (Recommended)
```bash
make dev-all
# OR
docker compose -f docker-compose.dev.yml up --build
```

### 3. Run Migrations & Seed
```bash
make migrate
make seed
make create-admin
```

### 4. Access
| Service       | URL                          |
|---------------|------------------------------|
| Dashboard     | http://localhost:3000        |
| API           | http://localhost:5000/api/v1 |
| Flower (Celery)| http://localhost:5555       |
| PgAdmin       | http://localhost:8080        |
| MailHog       | http://localhost:8025        |

---

## 📁 Project Structure

```
Whatsapp-Bot/
├── backend/                    # Python Flask API
│   ├── app/
│   │   ├── api/v1/             # REST API blueprints
│   │   │   ├── auth/           # Authentication endpoints
│   │   │   ├── whatsapp/       # Webhook receiver
│   │   │   ├── conversations/  # Conversation management
│   │   │   ├── agents/         # AI agent configuration
│   │   │   ├── workflows/      # Workflow builder
│   │   │   ├── tickets/        # Support tickets
│   │   │   └── ...             # 12 more modules
│   │   ├── agents/             # AI specialist agents
│   │   │   ├── base_agent.py   # Abstract base
│   │   │   ├── support_agent.py
│   │   │   ├── lead_agent.py
│   │   │   ├── sales_agent.py
│   │   │   └── ...
│   │   ├── ai/
│   │   │   ├── providers/      # LLM provider abstraction
│   │   │   ├── base_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   └── provider_factory.py
│   │   │   ├── orchestrator/   # Supervisor + routing
│   │   │   ├── rag/            # Retrieval-Augmented Generation
│   │   │   ├── tools/          # Function-calling tools
│   │   │   ├── memory/         # Conversation memory
│   │   │   └── embeddings/     # Vector embeddings
│   │   ├── core/
│   │   │   ├── config/         # Settings (Pydantic)
│   │   │   ├── security/       # Encryption, JWT, PII
│   │   │   ├── logging/        # Structured logging
│   │   │   └── exceptions/     # Error handlers
│   │   ├── integrations/
│   │   │   └── whatsapp/       # WA Cloud API client + webhook
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── services/           # Business logic
│   │   ├── repositories/       # Data access layer
│   │   ├── schemas/            # Pydantic/Marshmallow schemas
│   │   ├── tasks/              # Celery background tasks
│   │   ├── workflows/          # Workflow engine
│   │   └── middleware/         # Auth, rate limit, tenant
│   ├── tests/                  # Unit, integration, e2e
│   ├── migrations/             # Alembic migrations
│   ├── scripts/                # Admin CLI scripts
│   ├── requirements.txt
│   ├── Dockerfile
│   └── wsgi.py
│
├── frontend/                   # React + TypeScript dashboard
│   ├── src/
│   │   ├── pages/              # 16 dashboard pages
│   │   ├── components/         # Reusable UI components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API clients
│   │   ├── store/              # Zustand state management
│   │   ├── types/              # TypeScript types
│   │   └── styles/             # Global CSS
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── infra/
│   ├── nginx/                  # Nginx config (TLS, rate limiting)
│   ├── docker/                 # Service-specific Dockerfiles
│   ├── k8s/                    # Kubernetes manifests
│   ├── terraform/              # IaC (AWS/GCP)
│   └── monitoring/             # Prometheus + Grafana
│
├── prompts/                    # Agent system prompts & templates
├── docs/                       # Architecture, API, deployment docs
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.dev.yml      # Development stack
├── docker-compose.prod.yml     # Production stack
├── Makefile                    # All dev commands
└── .env.example                # Environment variables template
```

---

## 🤖 AI Agents

| Agent | Responsibility |
|-------|---------------|
| **Supervisor** | Classifies intent, routes to specialist agents |
| **Lead Agent** | Lead capture, qualification, scoring |
| **Support Agent** | Customer support, KB search, ticket creation |
| **Sales Agent** | Sales conversations, product recommendations |
| **Appointment Agent** | Booking, rescheduling, reminders |
| **Project Agent** | Project status, updates, task management |
| **HR Agent** | Employee queries, leave, onboarding |
| **Knowledge Agent** | RAG-based knowledge retrieval |

---

## 🔑 Key Features

- **Multi-tenant** — full organization isolation
- **Multi-LLM** — Gemini, Ollama via unified interface
- **RAG-ready** — pgvector + embedding pipeline built-in
- **Tool-calling** — agents can call external APIs
- **Human handoff** — seamless escalation to human agents
- **Workflow engine** — visual no-code automation builder
- **End-to-end encryption** — AES-256-GCM on all PII
- **Audit logs** — complete immutable audit trail
- **Rate limiting** — per-tenant + per-endpoint limits

---

## 🛡️ Security

- JWT authentication with refresh token rotation
- AES-256-GCM field-level encryption for PII
- HMAC-SHA256 webhook signature verification
- Role-based access control (RBAC)
- Nginx WAF rules + rate limiting
- Trivy vulnerability scanning in CI

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask 3, SQLAlchemy 2 |
| Database | PostgreSQL 16 + pgvector |
| Cache/Queue | Redis 7 + Celery 5 |
| AI | Google Gemini 1.5, Ollama (local LLMs) |
| Frontend | React 18, TypeScript, TailwindCSS, Vite |
| WhatsApp | Meta Business Cloud API v19 |
| Encryption | Python cryptography (OpenSSL AES-256-GCM) |
| Infra | Docker, Nginx, Gunicorn, GitHub Actions |

---

## 📄 License

Proprietary — All rights reserved.
