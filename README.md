# MasterArt AI Sales Platform

Production-ready backend + Telegram sales bot for MasterArt advertising agency.

## Features

- Guided order intake in Telegram (name, phone, service, material, size, quantity, urgency, design, delivery).
- Professional price estimation with transparent breakdown:
  - service rate,
  - material multiplier,
  - setup fee,
  - design fee,
  - delivery fee,
  - bulk discount,
  - urgency coefficient.
- Lead storage in PostgreSQL.
- AI summary for managers (OpenAI, with safe fallback).
- Tiered smart commercial proposals (`Basic/Pro/Premium`) per lead.
- AI creative copy generation for ads (`/api/creative-copy`, bot command `/creative`).
- AI mini-app at `/app`: Idea -> AI Brief -> Concepts -> Tradeoff -> Confirm.
- Manager notification in Telegram.
- Protected admin endpoints with `x-api-key`.
- Basic analytics endpoint (`/api/stats`).

## Architecture

- `app/main.py` - FastAPI app, lifespan, logging, global error handler.
- `app/api/routes.py` - REST API.
- `app/services/pricing.py` - pricing engine.
- `app/services/ai_assistant.py` - AI lead summarization.
- `app/bot/main.py` - Telegram bot workflow.
- `app/models.py` - SQLAlchemy models.
- `docker-compose.yml` - PostgreSQL + Redis.

## Environment

Copy `.env.example` to `.env` and set real values:

- `DATABASE_URL`
- `REDIS_URL`
- `INTERNAL_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_MANAGER_CHAT_ID`
- `OPENAI_API_KEY` (optional, but recommended)

## Run locally

1. Start infra:
```bash
docker compose up -d
```

2. Install app:
```bash
pip install -e .[dev]
```

3. Run API:
```bash
uvicorn app.main:app --reload
```

4. Run bot in second terminal:
```bash
python -m app.bot.main
```

## API

Public:
- `GET /api/healthz`
- `POST /api/estimate`
- `POST /api/proposals`
- `POST /api/creative-copy`
- `POST /api/intake/parse`
- `POST /api/concepts`
- `POST /api/tradeoff`
- `POST /api/deal/confirm`

Protected (`x-api-key` required):
- `POST /api/leads`
- `GET /api/leads?limit=50&offset=0`
- `GET /api/leads/{lead_id}`
- `GET /api/stats`

## Production checklist

1. Replace `create_all` with Alembic migrations.
2. Put API behind Nginx and TLS.
3. Store secrets in Vault/SSM, not plain `.env`.
4. Add Sentry and metrics.
5. Configure backups for PostgreSQL.
6. Add Redis-based FSM storage for bot horizontal scaling.
7. Add CRM integration (`amoCRM` / `Bitrix24`) via worker queue.
