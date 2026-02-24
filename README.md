# Opportunity Access Platform

An AI-powered platform designed to improve equitable access to educational and professional opportunities for students, with a focus on first-generation and underserved learners.

## Features

- **Personalized Recommendations**: AI-powered matching of opportunities to student profiles
- **Deadline Tracking**: Automated reminders for application deadlines
- **Multi-Channel Notifications**: Email and SMS notifications
- **Low-Bandwidth Mode**: Optimized for limited connectivity
- **Educational Content**: Guidance for first-generation students
- **Comprehensive Search**: Filter by type, deadline, eligibility

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL (or SQLite for development)
- Redis (optional, for caching)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run property-based tests only:
```bash
pytest -k property
```

## Project Structure

```
.
├── models/          # Database models
├── services/        # Business logic services
├── api/            # API endpoints
├── tests/          # Test suite
├── config.py       # Configuration
├── database.py     # Database setup
├── main.py         # Application entry point
└── requirements.txt
```

## Development

This project uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for database ORM
- **Pytest** for unit testing
- **Hypothesis** for property-based testing
- **Bcrypt** for password hashing

## License

MIT
