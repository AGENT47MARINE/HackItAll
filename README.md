# Opportunity Access Platform

An AI-powered platform that helps students—especially first-generation and underserved learners—discover, track, and successfully apply to hackathons, scholarships, internships, and skill programs.

## Features

- **AI-Powered Recommendations**: Personalized opportunity suggestions based on interests, skills, education level, and participation history
- **Smart Search & Filters**: Search opportunities by type, deadline, eligibility, and keywords
- **Application Tracking**: Save opportunities and track application status with deadline reminders
- **Push Notifications**: Deadline reminders via email, SMS, and mobile push notifications
- **Educational Content**: Beginner-friendly guides explaining hackathons, scholarships, and application processes
- **Low-Bandwidth Mode**: Lightweight pages and email/SMS alerts for limited-connectivity environments
- **Multi-Platform**: Backend API, web application, and mobile apps (iOS & Android)

## Project Structure

```
opportunity-access-platform/
├── api/                    # API endpoints
├── models/                 # Database models
├── services/              # Business logic services
├── tests/                 # Test suite (179+ tests)
├── mobile/                # React Native mobile app (iOS & Android)
├── web/                   # React web application
├── docs/                  # API documentation
├── .kiro/specs/          # Feature specifications
├── main.py               # FastAPI application entry point
├── database.py           # Database configuration
├── config.py             # Application configuration
└── requirements.txt      # Python dependencies
```

## Universal AI Scraper (Tier-2 Architecture)

The platform features a high-fidelity "Tier-2" scraper designed to extract opportunity data from any website without custom code for each domain.

### Core Principles
- **Visual-First Rendering**: Uses **Playwright** with Stealth Mode to execute JavaScript, scroll for lazy-loaded content, and see the page exactly as a human would.
- **Semantic Intelligence**: Instead of fragile CSS selectors, it uses **Ollama** (Local LLM) to understand the page content.
- **Intelligent Chunking**: Processes large DOMs by stripping "noise" (ads, footers, nav) and segmenting surviving text into semantic blocks for the LLM.
- **Structured Extraction**: Maps raw website text to a rigorous JSON schema, ensuring all opportunities are captured with high precision (deadlines, prizes, eligibility).
- **Graceful Fallback**: Automatically switches to stealth mode or standard requests if browser-based fetching is blocked.


## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy with SQLite (easily switchable to PostgreSQL)
- **Authentication**: Clerk authentication with bcrypt password hashing
- **Testing**: pytest with 179+ comprehensive tests
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Mobile App
- **Framework**: React Native with Expo
- **Navigation**: React Navigation
- **State Management**: React Hooks
- **API Client**: Axios
- **Push Notifications**: Expo Notifications
- **Platforms**: iOS and Android

### Web App
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **API Client**: Axios
- **Styling**: CSS Modules

## Quick Start

### Backend API

1. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the API server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Mobile App

1. Install dependencies:
```bash
cd mobile
npm install
```

2. Start Expo development server:
```bash
npm start
```

3. Run on device:
- Scan QR code with Expo Go app (iOS/Android)
- Or press `i` for iOS simulator, `a` for Android emulator

See [mobile/README.md](mobile/README.md) for detailed instructions.

### Web Application

1. Install dependencies:
```bash
cd web
npm install
```

2. Start development server:
```bash
npm run dev
```

The web app will be available at `http://localhost:3000`

See [web/README.md](web/README.md) for detailed instructions.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Profile Management
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `DELETE /api/profile` - Delete account

### Opportunities
- `GET /api/opportunities` - Search and filter opportunities
- `GET /api/opportunities/:id` - Get opportunity details
- `GET /api/recommendations` - Get personalized recommendations
- `POST /api/admin/opportunities` - Create opportunity (admin)
- `PUT /api/admin/opportunities/:id` - Update opportunity (admin)

### Tracking
- `POST /api/tracked` - Save opportunity to tracker
- `GET /api/tracked` - Get tracked opportunities
- `DELETE /api/tracked/:id` - Remove tracked opportunity
- `POST /api/participation` - Add participation history
- `PUT /api/participation/:id` - Update participation status
- `GET /api/participation` - Get participation history

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Current test coverage: 179+ tests covering all core functionality

## Development Workflow

This project was built using spec-driven development. The complete specification is available in `.kiro/specs/opportunity-access-platform/`:
- `requirements.md` - Feature requirements and acceptance criteria
- `design.md` - System design and architecture
- `tasks.md` - Implementation task list

## Configuration

### Backend Configuration

Edit `config.py` or set environment variables:
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Secret key for password hashing
- `DEBUG` - Debug mode (default: True)

### Mobile App Configuration

Edit `mobile/src/services/apiService.js`:
```javascript
const API_BASE_URL = 'http://YOUR_IP:8000/api';
```

For physical device testing, replace `localhost` with your computer's IP address.

### Web App Configuration

The web app uses Vite's proxy in development. For production, configure your web server to proxy `/api` requests to the backend.

## Deployment

### Backend
- Deploy to any Python hosting service (Heroku, AWS, Google Cloud, etc.)
- Use PostgreSQL for production database
- Set environment variables for configuration
- Enable HTTPS

### Mobile App
- Build with Expo EAS: `eas build --platform all`
- Submit to App Store and Google Play
- Configure push notification credentials

### Web App
- Build: `npm run build`
- Deploy `dist` folder to static hosting (Netlify, Vercel, etc.)
- Configure redirects for client-side routing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

MIT

## Support

For issues and questions:
- Check the documentation in `/docs`
- Review the API docs at `/docs` endpoint
- Open an issue on GitHub
