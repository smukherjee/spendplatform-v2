# SpendPlatform v2 - Enterprise Spend Management Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)

A modern, enterprise-grade spend management platform built with FastAPI, React, and PostgreSQL. Features include user management, client administration, invoice processing, and comprehensive audit trails.

## 🚀 Quick Start for New Developers

### Prerequisites

- **Python 3.11+** (with pip)
- **Node.js 18+** (with npm)
- **PostgreSQL 15+**
- **Git**
- **Docker** (optional, for containerized development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd spendplatform-v2

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies (if frontend exists)
cd frontend && npm install && cd ..
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb spendplatform

# Set environment variables
export DATABASE_URL="postgresql://your_user:your_password@localhost:5432/spendplatform"
export SECRET_KEY="your-secret-key-here"

# Run database migrations
cd backend
alembic upgrade head

# Seed database with sample data
cd src
python seed_database.py
cd ../..
```

### 3. Start Development Server

```bash
# Method 1: Full-stack development (recommended)
./start_dev.sh              # Opens backend and frontend in separate terminals

# Method 2: Individual services
./start_backend.sh           # Backend only (FastAPI)
./start_frontend.sh          # Frontend only (React)

# Method 3: Traditional FastAPI development
cd backend/src
source ../../.venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:3000 (if running)

## 📁 Project Structure

```
spendplatform-v2/
├── backend/                    # FastAPI backend application
│   ├── src/                   # Source code
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── database.py       # Database connection
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routers/          # API route handlers
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── utils.py          # Utility functions
│   │   └── deployment_config.py  # Environment-aware config
│   ├── requirements.txt      # Python dependencies
│   ├── alembic/             # Database migrations
│   └── alembic.ini          # Alembic configuration
├── frontend/                   # React frontend (if exists)
├── docs/                      # Project documentation
├── scripts/                   # Development scripts
├── deployment/                # Deployment configurations
├── .venv/                     # Python virtual environment
├── start_server.sh           # Quick start script
└── README.md                 # This file
```

## 🛠️ Development Workflows

### Daily Development

```bash
# Full-stack development (recommended)
./start_dev.sh               # Opens both services in separate terminals

# Individual services  
./start_backend.sh           # Backend only
./start_frontend.sh          # Frontend only
```

### Database Management

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Reset database with sample data
cd src
python seed_database.py
```

### Testing

```bash
# Run tests (if configured)
cd backend
source ../.venv/bin/activate
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/spendplatform

# Security
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Development
DEBUG=true
DEPLOYMENT_MODE=development
LOG_LEVEL=INFO

# CORS (for frontend integration)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Database Configuration

The application uses PostgreSQL with SQLAlchemy. Key models include:
- **Users**: User accounts with authentication
- **Clients**: Multi-tenant client management
- **Roles**: Role-based access control
- **Invoices**: Invoice processing and management
- **Audit Logs**: Comprehensive activity tracking

## 🚀 Deployment Options

### Development Deployment

```bash
# Start backend server
./start_backend.sh

# Start frontend server (if you have one)
./start_frontend.sh
```

### Production Deployment

#### Single Server (Small/Medium Load)
```bash
# Setup deployment infrastructure
./setup_flexible_deployment.sh

# Deploy to single server
./deployment/scripts/deploy-single.sh
```

#### Multi-Server (High Load)
```bash
# Deploy across multiple servers
./deployment/scripts/deploy-multi.sh <api_server_ip> <web_server_ip>
```

## 🔐 Authentication & Authorization

The platform uses JWT-based authentication with role-based access control:

- **superadmin**: Full system access
- **client_admin**: Client-level administration
- **user**: Standard user access

### Login Process
```bash
# Get access token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Use token in subsequent requests
curl -H "Authorization: Bearer <your_token>" \
  "http://localhost:8000/api/v1/users"
```

## 📊 Key Features

### User Management
- User creation, update, and deletion
- Role assignment and management
- Client-based user scoping
- Comprehensive audit trails

### Client Management
- Multi-tenant architecture
- Client-specific data isolation
- Client administrator roles
- Business unit and region support

### Invoice Processing
- Invoice creation and management
- Item-level detail tracking
- Category and subcategory organization
- Supplier management integration

### Security Features
- JWT authentication
- Role-based access control
- Screen-level permissions
- Password hashing with Argon2
- Comprehensive audit logging

## 🧪 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```bash
# Authentication
POST /token                    # Login and get JWT token

# Users
GET  /api/v1/users            # List users
POST /api/v1/users            # Create user
PUT  /api/v1/users/{id}       # Update user
DELETE /api/v1/users/{id}     # Delete user

# Clients
GET  /api/v1/clients          # List clients
POST /api/v1/clients          # Create client

# Health & Monitoring
GET  /health                  # Health check
GET  /api/v1/config          # Configuration info
GET  /api/v1/services/discovery  # Service discovery
```

## 🛠️ Development Tools

### Enhanced Development Environment

If you want a more advanced development setup:

```bash
# Setup enhanced development tools
./setup_dev_environment.sh

# Available commands after setup:
npm run dev                    # Start full development environment
npm run test                   # Run all tests
npm run lint                   # Check code quality
npm run format                 # Auto-format code
npm run db:reset              # Reset database with sample data
npm run db:shell              # Access database shell
```

### VS Code Integration

The project includes VS Code configuration for:
- Python debugging
- Auto-formatting on save
- Integrated testing
- Database connection tools

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready -d spendplatform

# Check connection string
echo $DATABASE_URL

# Reset database
dropdb spendplatform && createdb spendplatform
cd backend && alembic upgrade head
```

#### Import Errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"

# Verify you're in the correct directory
cd backend/src
python -c "import main; print('Import successful')"
```

#### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python -m uvicorn main:app --reload --port 8001
```

### Getting Help

1. **Check the logs**: Look for error messages in the terminal
2. **Verify environment**: Ensure all environment variables are set
3. **Database state**: Check if migrations are up to date
4. **Dependencies**: Ensure all Python packages are installed

## 📚 Additional Documentation

- **[Development Experience Guide](DEVELOPMENT_EXPERIENCE_ANALYSIS.md)**: Detailed development workflow and best practices
- **[Deployment Guide](DEPLOYMENT_OPTIMIZATION_GUIDE.md)**: Production deployment strategies
- **[Flexible Architecture](FLEXIBLE_DEPLOYMENT_ARCHITECTURE.md)**: Scaling from single to multi-server

## 🤝 Contributing

1. **Code Style**: Use Black for Python formatting, follow PEP 8
2. **Testing**: Write tests for new features
3. **Documentation**: Update README and API docs for changes
4. **Commits**: Use meaningful commit messages
5. **Database**: Create migrations for schema changes

## 📝 Development Checklist for New Features

- [ ] Create/update database models if needed
- [ ] Write Pydantic schemas for request/response
- [ ] Implement API endpoints in routers
- [ ] Add authentication/authorization checks
- [ ] Write unit tests
- [ ] Update API documentation
- [ ] Test with sample data
- [ ] Verify audit logging works

## 🏗️ Architecture Notes

The application is designed for flexible deployment:
- **Development**: Single process, SQLite or local PostgreSQL
- **Production**: Multi-server with load balancing
- **Scaling**: Horizontal scaling with shared database
- **Configuration**: Environment-aware settings

The codebase follows modern Python and FastAPI best practices with clear separation of concerns, comprehensive error handling, and production-ready logging and monitoring.

---

**Need help?** Check the troubleshooting section above or refer to the detailed documentation in the `docs/` directory.