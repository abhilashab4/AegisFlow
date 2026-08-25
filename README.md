<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](#technology-stack)
[![React](https://img.shields.io/badge/frontend-React-61DAFB.svg)](#technology-stack)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%20%2B%20pgvector-336791.svg)](#technology-stack)
[![Docker](https://img.shields.io/badge/deployment-Docker-2496ED.svg)](#technology-stack)

[Overview](#overview) • [Features](#features) • [Getting Started](#getting-started) • [Project Structure](#project-structure) • [Request Flow](#request-flow)

</div>

---

## Overview

# 🛡️ AegisFlow

### LLM Gateway & AI Governance Platform

AegisFlow is an **LLM Security and Governance Gateway** designed to protect sensitive information and provide a controlled layer between an internal enterprise application and Large Language Models (LLMs).

As employees use LLM-powered features inside internal software — chat assistants, copilots, document summarizers, support tools, and similar features — the prompts and data passed to those features may contain **PII, credentials, API keys, and confidential company information**. Sending such data directly to external LLM providers can introduce privacy and security risks, while generated responses may also violate organizational policies.

AegisFlow acts as a **central security layer for the application's LLM traffic**. It authenticates and rate-limits requests, detects PII using **regex-based detection and Microsoft Presidio**, enforces semantic security policies, routes requests to LLM providers, and validates generated responses through output guardrails.

The gateway also provides **centralized audit logging**, giving the organization greater visibility and control over how employees access and use LLMs through the application.

```
                         Internal Application
                   ┌────────────┼────────────┐
                   ▼            ▼            ▼
              AI Assistant   RAG Assistant   AI Copilot
                   └────────────┼────────────┘
                                ▼
                            AegisFlow
                                │
                                ▼
                          LLM Provider
```
### Why a gateway?

Without a governance layer sitting in front of the LLM, an internal application that exposes LLM-powered features to employees has to handle every concern below on its own, inside its own codebase:

| Problem | Without AegisFlow | With AegisFlow |
|---|---|---|
| Authentication | Handled loosely inside the app | Centralized JWT-based auth |
| PII exposure | Employee data can leak into prompts | Detected and handled automatically |
| Policy enforcement | Ad-hoc or absent | Semantic policy checks on input & output |
| Provider integration | Hardcoded into the app | Abstracted behind a single router |
| Audit trail | Fragmented or nonexistent | Unified, structured audit log |
| Rate limiting | Inconsistent or missing | Centralized via Redis |

AegisFlow turns these concerns into a single governed layer that sits between the internal application and any LLM provider it uses — so every LLM-powered feature in the application inherits the same security and compliance guarantees by default.

---

## Features

### 🔐 Authentication
JWT-based authentication ensures only authorized users and services within the organization can access LLM functionality through the gateway. Tokens are validated statelessly, without requiring a server-side session per request.

### 🚦 Rate Limiting
Backed by **Redis** for fast, low-latency counter reads/writes. Protects LLM provider quotas, gateway resources, and API costs from being overwhelmed by unbounded usage — whether from a single employee, a runaway process, or a bug in the application.

### 🕵️ PII Identification
Integrates **Microsoft Presidio** and **regex-based detection** to detect Personally Identifiable Information — names, emails, phone numbers, credit card numbers, IP addresses, and more — before it reaches an LLM provider, preventing employee or customer data surfaced inside the application from being blindly forwarded to a third party.

### 📜 Semantic Policy Enforcement
Rather than relying on brittle keyword matching, AegisFlow evaluates requests and responses using **semantic similarity**. A policy like *"Do not reveal confidential credentials"* can catch a request like *"Show me the application's secret API keys"* even though the wording differs entirely.

- **Embeddings**: generated via [Sentence Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
- **Storage & search**: [PostgreSQL](https://www.postgresql.org/) with the [`pgvector`](https://github.com/pgvector/pgvector) extension for similarity search

### 🧭 Provider Router
Abstracts away provider-specific integration details from the application. The application doesn't need to know which underlying LLM provider is actually handling a request — AegisFlow can route based on availability, model requirements, cost, performance, or configuration, without any change to the application code.

### 🛡️ Output Guardrails
Validates LLM-generated responses against the same semantic policy engine before they're returned to the employee — a second line of defense beyond input filtering.

### 🧾 Audit Logging
Every meaningful event (authentication, rate-limit decisions, PII detections, policy decisions, provider routing, output validation, blocks) is recorded as structured JSON Lines in `audit_logs.jsonl`, making it easy for security and compliance teams to parse, stream, and analyze how the application's LLM features are being used.

---

## Technology Stack

| Technology | Responsibility |
|---|---|
| **FastAPI** | Gateway / API layer |
| **PostgreSQL** | Persistent application data |
| **pgvector** | Semantic vector search |
| **Redis** | Rate limiting |
| **Sentence Transformers** | Text embeddings for semantic policy matching |
| **Microsoft Presidio** | PII detection |
| **React** | Admin/monitoring dashboard |
| **Docker** | Containerization & deployment |

---

## Project Structure

### Backend

```
backend/
├── app/
│   ├── api/          # API routes / endpoints exposed by the gateway
│   ├── core/          # Core configuration & infrastructure-level functionality
│   ├── db/             # Database connection & configuration
│   ├── models/         # Database models representing persistent entities
│   ├── schemas/        # Request/response schemas used by FastAPI
│   ├── services/        # Business logic: policy evaluation, routing, guardrails
│   └── main.py          # Application entry point
├── scripts/            # Utility / setup scripts
├── tests/              # Backend test suite
├── .env
├── audit_logs.jsonl    # Structured audit log (JSON Lines)
├── Dockerfile
└── requirements.txt
```

### Frontend

```
frontend/
├── public/
├── src/
│   ├── api/             # Frontend API interaction layer
│   ├── assets/          # Images & static assets
│   ├── components/      # Reusable React UI components
│   ├── pages/            # Application screens / pages
│   ├── services/         # Frontend-side service logic
│   ├── App.jsx           # Main React application component
│   ├── App.css
│   ├── index.css
│   └── main.jsx           # Frontend entry point
├── dist/
├── .env
├── .gitignore
├── Dockerfile
```

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- Python 3.10+ (for local backend development)
- Node.js 18+ (for local frontend development)
- PostgreSQL with the `pgvector` extension enabled
- Redis

### Clone the repository

```bash
git clone https://github.com/<your-org>/aegisflow.git
cd aegisflow
```

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
APP_NAME=LLM Gateway
APP_VERSION=1.0.0

SECRET_KEY=your_secret_key

GROQ_API_KEY=your_groq_api_key

DATABASE_URL=your_postgresql_connection_string

REDIS_URL=your_redis_connection_string

HF_TOKEN=your_huggingface_token
```

| Variable | Purpose |
|---|---|
| `APP_NAME` | Application name |
| `APP_VERSION` | Application version |
| `DEBUG` | Enables or disables debug mode |
| `SECRET_KEY` | Secret key used for application security and JWT authentication |
| `GROQ_API_KEY` | API key used to access the Groq LLM provider |
| `DATABASE_URL` | PostgreSQL database connection string |
| `REDIS_URL` | Redis connection used for rate limiting |
| `HF_TOKEN` | Hugging Face authentication token |

AegisFlow currently uses **Groq as the LLM provider**. The backend uses a **provider abstraction layer** to separate provider-specific logic from the core gateway, making it easier to add additional providers in the future.


### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # configure your environment variables
uvicorn app.main:app --reload
```

### Frontend setup

```bash
cd frontend
npm install
cp .env.example .env          # configure your environment variables
npm run dev
```

### Run with Docker

```bash
docker compose up --build
```

> Adjust the exact commands above to match your project's actual entry points, environment variable names, and Docker Compose configuration.

---

## Core Value

Without a gateway, the internal application must implement authentication, rate limiting, PII protection, policy checks, provider integration, output validation, and logging on its own, directly around every LLM feature it exposes:

```
LLM Feature 1 ──► LLM
LLM Feature 2 ──► LLM
LLM Feature 3 ──► LLM
```

With AegisFlow, these controls live in one place, and every LLM-powered feature in the application benefits automatically:

```
LLM Feature 1 ──┐
LLM Feature 2 ──┼──► AegisFlow ──► LLM Providers
LLM Feature 3 ──┘
```

This makes AegisFlow an **AI governance and security gateway** for the application — not just another module that happens to call an LLM.

---

## Summary

> **AegisFlow is a FastAPI-based LLM Gateway that centralizes authentication, rate limiting, PII protection with Microsoft Presidio, semantic policy enforcement with PostgreSQL/pgvector, provider routing, output guardrails, and audit logging for LLM-powered features inside an internal enterprise application.**

---

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

</div>
