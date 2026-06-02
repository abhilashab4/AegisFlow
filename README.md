# AegisFlow

AegisFlow is a secure middleware platform that sits between enterprise applications and Large Language Models (LLMs). It provides authentication, authorization, governance, auditing, rate limiting, cost tracking, and safety controls before requests reach AI providers.

The project is designed to demonstrate how organizations can securely integrate Generative AI into their systems while maintaining compliance, visibility, and operational control.

---

## Features

### Authentication & Authorization
- User Registration and Login
- JWT-based Authentication
- Role-Based Access Control (RBAC)
- Endpoint and Task-Level Permissions

### AI Governance
- Task-Based Model Routing
- Provider Routing Layer
- PII Detection and Sanitization
- Output Guardrails
- Streaming Response Validation

### Monitoring & Compliance
- Audit Logging
- Usage Tracking
- Cost Estimation
- Redis-Based Rate Limiting

### AI Integration
- Groq Integration
- Streaming Response Support
- Provider Abstraction Layer for Multi-LLM Support

---

## Architecture

```text
Client
   |
   v
Enterprise AI Gateway
   |
   +-- Authentication
   +-- RBAC
   +-- Rate Limiting
   +-- PII Filtering
   +-- Model Routing
   +-- Provider Routing
   +-- Output Validation
   +-- Audit Logging
   +-- Cost Tracking
   |
   v
LLM Provider
```

---

## Request Flow

```text
User Request
      |
      v
JWT Authentication
      |
      v
Rate Limiting
      |
      v
PII Validation
      |
      v
RBAC Authorization
      |
      v
Model Selection
      |
      v
Provider Routing
      |
      v
LLM Response
      |
      v
Output Guardrails
      |
      v
Audit & Usage Tracking
      |
      v
Final Response
```

---

## Tech Stack

### Backend
- FastAPI
- Python
- AsyncIO

### Database
- PostgreSQL

### Caching & Rate Limiting
- Redis

### Authentication
- JWT
- Passlib (bcrypt)

### AI Provider
- Groq

---

## Project Structure

```text
app/
│
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── services/
│   ├── audits/
│   ├── cost/
│   ├── guardrails/
│   ├── pii/
│   ├── providers/
│   ├── rate_limit/
│   ├── rbac/
│   └── streaming/
│
└── main.py
```

---

## API Endpoints

### Authentication

```http
POST /auth/register
POST /auth/login
```

### AI Gateway

```http
POST /ai/generate
POST /ai/generate-stream
```

---

## Current Capabilities

- JWT Authentication
- PostgreSQL User Management
- Role-Based Access Control
- Task-Based AI Routing
- Groq Integration
- Streaming AI Responses
- PII Filtering
- Output Guardrails
- Audit Logging
- Usage Tracking
- Cost Tracking
- Redis Rate Limiting

---

## Planned Enhancements

- Multi-Provider Support (OpenAI, Claude)
- Provider Failover & Fallback
- Budget Enforcement
- Department-Level Governance
- Provider Health Monitoring
- Analytics APIs
- Admin Dashboard

---

## Motivation

Modern organizations need more than direct access to AI models. They require a control layer that can enforce policies, track usage, protect sensitive information, and provide visibility into AI operations.

This project aims to build that control layer while exploring real-world concepts such as AI governance, security, observability, and scalable backend architecture.

---

## Author
Abhilash A B
GitHub: https://github.com/abhilashab4
