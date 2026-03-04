# HackItAll Architecture & Tech Stack Documentation

This document serves as the core reference for the HackItAll platform, detailing the system architecture, the technology stack, and the core database models. It specifically highlights the AI Web Scalper pipeline, bridging local development environments with production-ready AWS deployments.

## 1. Complete Tech Stack

The platform is designed as a modern, decoupled monolithic application.

### Frontend (Client Tier)
*   **Framework:** React (Vite)
*   **Routing:** React Router DOM
*   **Styling:** Custom CSS with Glassmorphism / Cyberpunk themes (`Pages.css`)
*   **HTTP Client:** Axios with JWT Interceptors (`api.js`)

### Backend (Server Tier)
*   **Framework:** FastAPI (Python 3.10+)
*   **Application Server:** Uvicorn
*   **ORM:** SQLAlchemy (with Pydantic validation)
*   **Database:** SQLite (Local/Dev) -> PostgreSQL (AWS RDS Production)

### AI Web Scalper Engine (Data Acquisition)
*   **Headless Browser Engine:** Playwright `sync_api` (Renders Heavy JS sites)
*   **DOM Parsing:** BeautifulSoup4 (Strips HTML into clean text)
*   **Structure Extraction:** local Ollama (Llama-3 8B) OR AWS Bedrock (Claude 3 Haiku)
*   **Validation:** Pydantic `OpportunityExtraction` Object
*   **Deployment Vector:** Docker container based on `mcr.microsoft.com/playwright/python`

---

## 2. System Architecture (The "Two-Mode" Scraper Engine)

The core innovation of HackItAll is its scalable, dynamic opportunity aggregation pipeline.

### The Ingestion Flow
1.  **Trigger:** A user submits a URL via the `Tracked.jsx` React Interface, hitting `POST /api/opportunities/scrape`.
2.  **Dispatcher (`scraper/dispatcher.py`):**
    *   **Tier 1 (Known Domains):** If URL matches `*\.devpost\.com`, it routes to the `DevpostScraper` (Fast HTML parsing).
    *   **Tier 2 (Unknown Domains):** If a random URL (e.g. college site), it routes to `UniversalLocalScraper`.
3.  **Tier-2 Execution (`scraper/playwright_engine.py`):** Playwright loads the URL, waits for Network Idle, strips noisy HTML, and extracts pure OpenGraph metadata and clean Body text.
4.  **The AI Transformation Layer:**
    *   **Local Mode (`AI_PROVIDER=ollama`):** Connects to `http://localhost:11434` to invoke the local Llama-3 model for free inference.
    *   **AWS Mode (`AI_PROVIDER=bedrock`):** Connects to `boto3.client('bedrock-runtime')` executing an Anthropic Claude model.
    *   *Note: Both models output the exact same Pydantic-validated JSON Schema.*
5.  **Persistence:** The validated JSON is written to the SQLite/PostgreSQL `Opportunity` table.

### Dockerized Deployment Strategy
To guarantee parity between local testing and AWS production, the backend is containerized.
Because Playwright requires complex native C++ libraries (fonts, video codecs, OS rendering engines), we package the FastAPI server into a Microsoft Playwright Ubuntu Docker Image.
*   **Build:** `docker build -t hackitall-api .`
*   **AWS Deploy Pipeline:** Push Docker Image to ECR -> Deploy to AWS App Runner / ECS Fargate -> Point ECS to AWS RDS PostgreSQL.

---

## 3. Database Schema Structures

Here are the core internal models defined via SQLAlchemy in `models/`.

### Table: `users`
Core authentication and access control.
*   `id` (String UUID, Primary Key)
*   `email` (String 120, Unique, Indexed)
*   `hashed_password` (String 255)
*   `role` (String 20 - e.g., 'user', 'admin')
*   `created_at`, `updated_at` (DateTime)

### Table: `profiles`
The comprehensive user persona driving the Recommendation Engine.
*   `user_id` (String UUID, Foreign Key -> `users.id`)
*   `full_name` (String 100)
*   `bio` (Text)
*   `education_level` (String 50 - e.g., 'undergraduate', 'masters')
*   `skills` (Text - JSON Array storing Python, React, etc.)
*   `interests` (Text - JSON Array storing AI, Web3, FinTech)

### Table: `opportunities`
The master record of all Hackathons, Internships, and Scholarships. Populated by the AI Scalper.
*   `id` (String UUID, Primary Key)
*   `title` (String 255)
*   `description` (Text)
*   `type` (String 50 - e.g., 'hackathon')
*   `deadline` (DateTime, Indexed - crucial for chronological sorting)
*   `application_link` (String 500)
*   `image_url` (String 1000 - Scraped from OpenGraph metadata)
*   `tags` (Text - JSON Array - Scraped by AI)
*   `required_skills` (Text - JSON Array - Scraped by AI)
*   `eligibility` (String 50)
*   `status` (String 20 - e.g., 'active', 'archived', Indexed)
*   `tracked_count` (Integer, Indexed - Drives the "Trending" algorithm)

### Table: `tracked_opportunities`
Associative table linking Users to the Opportunities they want to save/monitor.
*   `id` (String UUID, Primary Key)
*   `user_id` (String UUID, Foreign Key -> `users.id`)
*   `opportunity_id` (String UUID, Foreign Key -> `opportunities.id`)

### Table: `participation_history`
Tracks user interaction and status with specific events (Winning, Attending, Submitted).
*   `id` (String UUID, Primary Key)
*   `user_id` (String UUID, Foreign Key -> `users.id`)
*   `opportunity_id` (String UUID, Foreign Key -> `opportunities.id`)
*   `status` (String 50 - e.g., 'interested', 'applied', 'participating', 'winner')
*   `notes` (Text, Nullable)

---
*Generated for persistent context reference.*
