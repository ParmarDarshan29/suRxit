# suRxit Backend API

AI-powered medication safety dashboard backend built with FastAPI.

## Features

- 🔐 **JWT Authentication** - Secure user authentication and authorization
- 💊 **Prescription Analysis** - AI-powered drug interaction detection
- 🤖 **Medical Chatbot** - MedLM integration for Q&A
- ⚡ **Real-time Alerts** - WebSocket/SSE for live safety notifications
- 📊 **Patient Management** - Comprehensive patient data handling
- 🗄️ **Database Integration** - SQLAlchemy with SQLite/PostgreSQL support
- 📁 **File Processing** - OCR for prescription image analysis
- 🔄 **Background Tasks** - Celery for async processing

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Initialize Database

```bash
# Create database tables
python database.py
```

### 3. Run Development Server

```bash
# Start FastAPI server
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration  
- `POST /api/auth/logout` - User logout
- `GET /api/auth/verify` - Verify JWT token

### Prescription Analysis
- `POST /api/analyze/prescription` - Analyze prescription for interactions
- `GET /api/drugs/{drug_name}` - Get drug information

### Patient Management
- `GET /api/patient/dashboard/{patient_id}` - Get patient dashboard

### Chat & AI
- `POST /api/chat/session` - Chat with medical AI assistant

### Real-time Features
- `GET /api/alerts/stream` - SSE stream for real-time alerts

## Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@example.com", "password": "password"}'

# Analyze prescription (replace TOKEN with login response token)
curl -X POST http://localhost:8000/api/analyze/prescription \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Lisinopril 10mg daily, Metformin 500mg twice daily"}'
```

## Default Test Accounts

- **Doctor**: `doctor@example.com` / `password`
- **Admin**: `admin@surxit.com` / `admin123`

## Configuration

Key environment variables:

```env
# Database
DATABASE_URL=sqlite:///./surxit.db

# JWT Security
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Services
OPENAI_API_KEY=your-openai-key
```

## Production Deployment

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### With Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Architecture

```
├── main.py              # FastAPI application entry point
├── auth.py              # Authentication & authorization
├── models.py            # Pydantic data models
├── database.py          # SQLAlchemy database setup
├── ai_service.py        # AI/ML integration services
├── requirements.txt     # Python dependencies
└── .env.example        # Environment configuration template
```

## Development

### Add New Endpoints

1. Define Pydantic models in `models.py`
2. Add route handlers in `main.py`
3. Update authentication as needed in `auth.py`
4. Test with FastAPI automatic docs at `/docs`

### Database Migrations

```bash
# Install alembic
pip install alembic

# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.