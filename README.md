# Log Monitoring & Incident Detection System

A backend service for log analysis, automated incident detection, and event correlation.

## Overview

This project processes raw application logs, matches them against predefined patterns, and automatically creates or updates incidents.

It builds structured context around events and provides insights into system behavior.

Designed as a backend foundation for observability and incident management systems.

## Key Features

### Log Processing Pipeline

* Pattern-based log analysis
* Field extraction (log level, status code, IP address, etc.)

### Incident Management

* Automatic incident creation
* Event grouping into incidents
* Severity and status management

### Context Enrichment

* Event context generation
* Incident context aggregation
* Confidence scoring and explanation

### API Functionality

* RESTful endpoints
* File upload for batch log processing

### Access Control

* JWT authentication
* Role-based permissions (viewer / engineer / admin)

## Tech Stack

 FastAPI
 SQLAlchemy
 Uvicorn
 PostgreSQL / SQLite
 Alembic
 Pytest
 Docker

## Getting Started

Clone repository:

```bash
git clone https://github.com/zxcwasher/LogInsight.git
cd LogInsight
```

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn main:app --reload
```

Swagger documentation:

`YOUR_SWAGGER_LINK_HERE`

## Authentication

Obtain JWT token:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
-H "Content-Type: application/json" \
-d '{
  "username": "your_username",
  "password": "your_password"
}'
```

## Example Request

```bash
curl -X POST http://127.0.0.1:8000/logs/process \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <token>" \
-d '{
  "raw_log": "ERROR Failed login attempt from 192.168.1.10",
  "source": "test",
  "host": "localhost"
}'
```

## API Endpoints

### Logs

* `POST /logs/process` — process a single log
* `POST /logs/upload` — upload log file

### Incidents

* `GET /incident/` — list incidents
* `GET /incident/{id}` — get incident details
* `PUT /incident/{id}/status`
* `PUT /incident/{id}/severity`

### Events

* `GET /incident/{id}/events`

### Comments

* `POST /comment/incident/{id}/comment`
* `GET /comment/incident/{id}/comment`

### Analytics

* `GET /analytics/summary`

## Security Notes

* Do not expose real JWT tokens in the repository
* Use environment variables for secrets
* Add `.env` and `.venv` to `.gitignore`

## Future Improvements

* Real-time log streaming
* Alerting system (email / Telegram / Slack)
* Machine learning anomaly detection
* Frontend dashboard
