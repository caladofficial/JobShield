# JobShield - Verified Job Intelligence Platform

A production-quality job post aggregation, verification, fraud-risk analysis, and outreach platform built with a source adapter architecture.

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Sources   │────▶│  Adapters    │────▶│  Normalization   │
│ (ATS, RSS,  │     │ (Greenhouse, │     │    Engine        │
│  Manual)    │     │  Lever, RSS) │     │                  │
└─────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Dashboard  │◀───│    API       │◀───│  Verification    │
│  (Next.js)  │     │  (FastAPI)   │     │  Pipeline        │
└─────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Outreach   │◀───│   Workers    │◀───│  Background Jobs │
│  (Email)    │     │  (Celery)    │     │  (Redis Queue)   │
└─────────────┘     └──────────────┘     └──────────────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Primary database (via Supabase)
- **Redis** - Queue broker and caching
- **Celery** - Distributed task queue
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic** - Data validation
- **Alembic** - Database migrations

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component primitives
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **TanStack Table** - Data tables
- **React Hook Form + Zod** - Form handling

### Infrastructure
- **Docker Compose** - Local development
- **Vercel** - Frontend hosting
- **Railway/Render** - Backend hosting
- **Supabase** - PostgreSQL database

## Features

### Source Adapter Architecture
- **Greenhouse Adapter** - Official API integration
- **Lever Adapter** - Official API integration
- **RSS Adapter** - Generic feed parsing
- **Manual URL Adapter** - User-submitted job URLs
- Extensible for new sources

### Verification Pipeline (7 Stages)
1. **Source Validation** - Verify source authenticity
2. **Employer Verification** - Domain, DNS, MX, website checks
3. **Uploader Verification** - Recruiter identity and history
4. **Content Analysis** - Job description quality and structure
5. **Contact Extraction** - Email, phone, URL validation
6. **Risk Analysis** - Scam pattern detection
7. **Final Confidence** - Weighted scoring

### Contact Extraction
- Email regex + syntax validation + domain classification
- Phone number parsing via `libphonenumber`
- Corporate vs free-mail classification

### Risk Engine
- Configurable scam pattern detection
- Weighted signal scoring
- Risk levels: Low, Medium, High, Unknown

### Dashboard
- Real-time verification metrics
- Interactive charts (Recharts)
- Advanced filtering and sorting
- Job detail pages with verification evidence

### Export System
- Excel (XLSX) with formatting
- Background job processing
- Secure download links with expiry

### Outreach System
- Campaign management
- Template variables
- Rate limiting and deduplication
- Gmail/Microsoft Graph/SMTP providers
- Unsubscribe handling

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.11+ (for backend development)

### Local Development

1. **Clone and start services:**
```bash
docker-compose up -d
```

2. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

3. **Default credentials (demo mode):**
- Any email/password combination works

### Environment Configuration

Create `.env` files from examples:

**Backend (.env):**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/jobshield
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=true
DEMO_MODE=true
CORS_ORIGINS=["http://localhost:3000"]
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXTAUTH_SECRET=your-nextauth-secret
NEXT_PUBLIC_DEMO_MODE=true
```

## Project Structure

```
jobshield/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   │   ├── source_adapters/
│   │   │   ├── normalization.py
│   │   │   ├── verification.py
│   │   │   └── email_providers.py
│   │   ├── workers/         # Celery tasks
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   │   ├── (dashboard)/ # Protected dashboard routes
│   │   │   ├── api/         # API routes
│   │   │   └── login/
│   │   ├── components/
│   │   │   ├── ui/          # Base UI components
│   │   │   └── dashboard/   # Dashboard-specific components
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   ├── tailwind.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Jobs
- `GET /api/v1/jobs` - List jobs with filters
- `POST /api/v1/jobs/scan` - Scan job from URL
- `GET /api/v1/jobs/{id}` - Get job details
- `POST /api/v1/jobs/{id}/reverify` - Re-run verification
- `DELETE /api/v1/jobs/{id}` - Delete job

### Sources
- `GET /api/v1/sources` - List available sources
- `GET /api/v1/sources/connections` - User's connections
- `POST /api/v1/sources/connections` - Create connection
- `POST /api/v1/sources/connections/{id}/sync` - Sync jobs
- `POST /api/v1/sources/connections/{id}/health` - Health check

### Verification
- `GET /api/v1/verification/job/{id}` - Get verification results
- `GET /api/v1/verification/job/{id}/signals` - Get verification signals
- `GET /api/v1/verification/job/{id}/risk-events` - Get risk events
- `POST /api/v1/verification/job/{id}` - Trigger verification

### Contacts
- `GET /api/v1/contacts/job/{id}` - Get job contacts
- `GET /api/v1/contacts` - List all contacts
- `GET /api/v1/contacts/stats/summary` - Contact statistics

### Exports
- `POST /api/v1/exports` - Create export job
- `GET /api/v1/exports` - List exports
- `GET /api/v1/exports/{id}/download` - Download export file

### Outreach
- `GET /api/v1/outreach/campaigns` - List campaigns
- `POST /api/v1/outreach/campaigns` - Create campaign
- `POST /api/v1/outreach/campaigns/{id}/send` - Send campaign
- `POST /api/v1/outreach/campaigns/{id}/send-test` - Send test email

### Analytics
- `GET /api/v1/analytics/overview` - Dashboard data
- `GET /api/v1/analytics/sources` - Source performance
- `GET /api/v1/analytics/risk` - Risk signals

### Admin (requires admin role)
- `GET /api/v1/admin/health` - System health
- `GET /api/v1/admin/sources` - All source connections
- `GET /api/v1/admin/verification` - Verification stats
- `GET /api/v1/admin/queue` - Celery queue status

## Deployment

### Free-Tier Cloud Deployment

1. **Database**: Supabase (PostgreSQL)
2. **Backend**: Railway or Render (FastAPI + Celery workers)
3. **Frontend**: Vercel (Next.js)
4. **Redis**: Railway/Render Redis or Upstash

### Environment Variables for Production

**Backend:**
```env
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
SECRET_KEY=secure-random-key
DEBUG=false
DEMO_MODE=false
CORS_ORIGINS=["https://your-domain.vercel.app"]
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
MICROSOFT_CLIENT_ID=...
MICROSOFT_TENANT_ID=...
```

**Frontend:**
```env
NEXT_PUBLIC_API_URL=https://your-api.railway.app/api/v1
NEXTAUTH_SECRET=secure-random-key
NEXT_PUBLIC_DEMO_MODE=false
```

## Security Features

- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Rate limiting (SlowAPI)
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React auto-escaping)
- Secure headers
- Encrypted credential storage
- Audit logging

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

JobShield is designed for legitimate job verification and aggregation through authorized sources only. It does not implement scraping, CAPTCHA bypass, or any techniques that violate source terms of service. Always ensure you have proper authorization before accessing job data from any platform.