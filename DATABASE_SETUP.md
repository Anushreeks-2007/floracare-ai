# FloraCare AI - Database Setup Guide

## Overview
FloraCare AI now uses PostgreSQL with SQLAlchemy ORM for:
- User authentication (registration, login, JWT tokens)
- Photo upload history tracking
- Prediction logging for model analytics
- User feedback collection for model improvement

## Local setup

### 1. Start PostgreSQL
```bash
docker-compose up -d postgres
```

### 2. Create environment file
```bash
cp .env.example .env
```

### 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run backend
```bash
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. API examples
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /api/history/photos`
- `GET /api/history/predictions`
- `GET /api/history/feedback`
- `POST /api/history/feedback`

## Security notes
- Use a strong JWT secret in production.
- Never commit real database credentials into the repo.
- Store .env only on local machine or deployment secret manager.
