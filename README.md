# 🤖 AI WhatsApp Automation Platform

> Enterprise-grade, multi-tenant AI-powered WhatsApp Automation Platform for businesses providing specialist AI Agents, visual workflow automation, and custom LLM integrations.

---

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat-square&logo=python)](https://python.org)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0-lightgrey.svg?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![React 18](https://img.shields.io/badge/React-18-cyan.svg?style=flat-square&logo=react)](https://react.dev)
[![Celery 5](https://img.shields.io/badge/Celery-5.x-green.svg?style=flat-square&logo=celery)](https://docs.celeryq.dev)
[![Redis 7](https://img.shields.io/badge/Redis-7.x-red.svg?style=flat-square&logo=redis)](https://redis.io)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16--pgvector-blue.svg?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg?style=flat-square)](#)

---

## 🏗️ Architecture Overview

The platform uses a modular, multi-tenant architecture designed to handle high-throughput WhatsApp traffic. Inbound webhook payloads from Meta are validated, quickly acknowledged, and processed asynchronously using Celery background tasks.

```
                  ┌────────────────────────────────────────────────────────┐
                  │                   Clients / WhatsApp                   │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Meta WhatsApp Business API
                                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                Nginx WAF & Reverse Proxy               │
                  │              TLS Termination · Rate Limits             │
                  └───────────┬────────────────────────────────┬───────────┘
                              │                                │
                              ▼                                ▼
                  ┌──────────────────────┐         ┌───────────────────────┐
                  │    Flask App API     │         │    React Dashboard    │
                  │  (WSGI / Gunicorn)   │         │   (Vite + Tailwind)   │
                  └───────────┬──────────┘         └───────────────────────┘
                              │
                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                     Service Layer                      │
                  │   Auth · Conv · AI · Workflows · Tickets · Analytics   │
                  └─────┬────────────────────────────────────┬─────────────┘
                        │                                    │
                        ▼                                    ▼
       ┌──────────────────────────────┐        ┌───────────────────────────┐
       │   PostgreSQL + pgvector      │        │       Celery Workers      │
       │  (Encrypted Credentials &   │        │     (ai, workflows, default│
       │   Tenant-Isolated Tables)    │        │      processing queues)   │
       └──────────────────────────────┘        └─────────────┬─────────────┘
                                                             │
                                                             ▼
                                               ┌───────────────────────────┐
                                               │      Redis Cache / Broker │
                                               │ (Locks, Sessions, Queues) │
                                               └─────────────┬─────────────┘
                                                             │
                                                             ▼
                                               ┌───────────────────────────┐
                                               │     AI Provider Layer     │
                                               │ (Gemini 1.5/2.5 · Ollama) │
                                               └───────────────────────────┘
```

---

## 🔑 Core Innovations & Features

### 🔒 Transparent Database Encryption
- **AES-256-GCM Cryptography**: Encrypts and decrypts sensitive tenant credentials (like Meta `access_token`) transparently in PostgreSQL.
- **SQLAlchemy Decorator**: Utilizes the `EncryptedText` type decorator class mapping to cryptographically secure columns, protecting PII and access credentials at rest.

### ⚡ Async Webhook Ingestion & Processing
- **<5s Met Response SLA**: Validates incoming Meta HMAC-SHA256 signatures and immediately returns a `200 OK` to satisfy Meta webhook response window limitations.
- **Celery & Redis Pipelines**: Enqueues raw payloads into `process_inbound_webhook_task` for background normalization, DB persistence, and AI intent evaluation.

### 🧠 Intent Routing & Redis-Locked Sessions
- **Supervisor Orchestrator**: Runs LLM classification on the first inbound message to identify user intent (e.g., Support, Sales, Booking).
- **Sticky Sessions**: Caches active agent selection in Redis for 30 minutes. Subsequent messages bypass classification and route directly to the active specialist.

### 🧑‍💼 Human Handoff & Bypass Routing
- **Handoff Manager**: Supports escalating conversations to human agents (`HUMAN_HANDLING` or `ESCALATED` states).
- **Auto-Bypass**: The `AgentRouter` ignores AI processing for any active human-managed sessions to avoid system interference.

---

## 📁 Project Structure

```
Whatsapp-Bot/
├── backend/                        # Python Flask API Core
│   ├── app/
│   │   ├── api/v1/                 # API Endpoints & Blueprints
│   │   │   ├── auth/               # Multi-tenant auth & JWT endpoints
│   │   │   ├── whatsapp/           # Webhook receiver & account settings
│   │   │   ├── conversations/      # Chat logs & context endpoints
│   │   │   ├── agents/             # Specialist configuration
│   │   │   ├── workflows/          # Automation flow management
│   │   │   ├── tickets/            # Helpdesk support tickets
│   │   │   └── ...                 
│   │   ├── agents/                 # Specialist Agent implementations
│   │   │   ├── base_agent.py       # Abstract agent and tool invocation layer
│   │   │   ├── support_agent.py    # Support & ticketing agent
│   │   │   ├── lead_agent.py       # Lead capture & scoring agent
│   │   │   ├── sales_agent.py      # Recommendations agent
│   │   │   └── ...                 
│   │   ├── ai/
│   │   │   ├── providers/          # Gemini & Ollama unified interfaces
│   │   │   ├── orchestrator/       # Supervisor router & handoff controller
│   │   │   └── rag/                # pgvector search & embedding pipelines
│   │   ├── core/                   # Security, logging, exceptions config
│   │   ├── integrations/           # Client APIs (e.g. WhatsApp Cloud API)
│   │   ├── models/                 # SQLAlchemy schemas (PostgreSQL)
│   │   ├── services/               # Business logic core layer
│   │   ├── tasks/                  # Celery background tasks
│   │   └── workflows/              # Visual flow-automation runner
│   ├── tests/                      # Unit, Integration, and E2E PyTest suite
│   ├── migrations/                 # Alembic DB migration revisions
│   ├── requirements.txt            # Production dependencies
│   └── wsgi.py                     # Entry point for production servers
│
├── frontend/                       # React TypeScript Dashboard
│   ├── src/
│   │   ├── pages/                  # Route views (Dashboard, Conversations, Tickets)
│   │   ├── components/             # Tailwind & Headless UI components
│   │   ├── services/               # HTTP client integration
│   │   └── store/                  # Zustand state management
│   └── package.json
│
├── infra/                          # Infrastructure configurations
│   ├── nginx/                      # WAF, TLS, & rate-limiting configs
│   ├── docker/                     # Environment Dockerfiles
│   ├── k8s/                        # Kubernetes deployment files
│   └── monitoring/                 # Prometheus & Grafana analytics dashboards
└── Makefile                        # Standard developer tool CLI targets
```

---

## 🤖 AI Specialist Agents

The orchestrator dynamically routes requests to context-aware agents based on intent:

| Agent | Core Responsibility | Key Features |
| :--- | :--- | :--- |
| **Supervisor** | Classifies incoming intent | Session locking & Redis lookup |
| **Lead Agent** | Captures and scores business leads | Qualification forms & CRM hooks |
| **Support Agent** | Resolves user FAQs and issues | KB search & automatic ticket creation |
| **Sales Agent** | Provides product suggestions | Catalog browsing & purchase funnels |
| **Appointment** | Schedules/reschedules bookings | Google Calendar integration hooks |
| **Knowledge** | Handles deep search queries | RAG pipeline using pgvector |

---

## 🚀 Quick Start

### 📋 Prerequisites
Ensure your local environment meets these criteria:
- **Docker & Compose** installed
- **Python 3.12+** (if running locally without Docker)
- **Node.js 20+** (if running dashboard locally)

---

### 1. Configure Local Environment
Clone the repository and prepare your configuration variables:
```bash
git clone <repo-url>
cd Whatsapp-Bot
cp .env.example .env
# Open .env and fill in active credentials
```

### 2. Start Services via Docker (Recommended)
You can start all required services (Flask, React, Celery, PostgreSQL, Redis, PgAdmin) using a single command:
```bash
# Start all containers in the foreground
make dev-all

# Alternatively, start in detached background mode
make docker-up-dev
```

### 3. Run Migrations & Admin Seed
Prepare the database schema, import seed data, and register the default superadmin:
```bash
# Run migrations to head
make migrate

# Populate database with seeds (organizations, roles, default records)
make seed

# Register superadmin user
make create-admin
```

### 4. Direct Services Directory
Once initialized, access these endpoints:

| Application | Address / URL | Description |
| :--- | :--- | :--- |
| **Vite Dashboard** | [http://localhost:3000](http://localhost:3000) | Administration Portal |
| **Flask API Docs** | [http://localhost:5000/api/v1](http://localhost:5000/api/v1) | Backend REST Endpoints |
| **Flower Dashboard** | [http://localhost:5555](http://localhost:5555) | Celery Queue Monitor |
| **PgAdmin** | [http://localhost:8080](http://localhost:8080) | PostgreSQL Browser GUI |
| **MailHog** | [http://localhost:8025](http://localhost:8025) | Outgoing SMTP capture mail Server |

---

## ⚙️ Development CLI (Makefile Reference)

Use the predefined commands in the `Makefile` to run standard maintenance tasks:

```bash
# Install local dependencies
make install

# Start individual modules locally
make dev-backend      # Launches debug Flask app on port 5000
make dev-frontend     # Starts Vite react server on port 3000
make dev-worker       # Launches Celery worker listening on all queues

# Testing
make test             # Run full backend test suite with coverage
make test-unit        # Run unit tests only
make test-integration # Run integration tests only

# Quality & Security
make lint             # Check backend PEP8 & type compliance
make format           # Automatically format Python code (black/isort)
make security-scan    # Scan backend codebase for vulnerabilities (bandit)
make secrets-check    # Check codebase for leaked config credentials
make rotate-keys      # Rotates database encryption keys
```

---

## 🛡️ Security Posture
- **JWT Authentication**: Incorporates short-lived access tokens with secure refresh token rotation stored in local storage.
- **HMAC Signatures**: Every incoming Meta payload requires verification against `X-Hub-Signature-256` matching the configuration verify token.
- **Vulnerability Checks**: Static analysis via Ruff, Bandits, and Docker Trivy scans implemented in standard pipelines.

---

## 📄 License

Proprietary — All rights reserved. For development and authorization details, contact administrators.
