# HackItAll - Architecture Review & Backend Improvements

## Summary of Repository Architecture
The repository is structured around a FastAPI backend, a React web frontend, and an Expo-based React Native mobile app.

The backend modules include:
- `api/`: Endpoint controllers orchestrating requests and responses.
- `services/`: Business logic, integrations (NLP, scraping, caching), and operations.
- `models/`: SQLAlchemy ORM definitions modeling entities like `Opportunity`, `User`, and `TrackedOpportunity`.
- `middleware/`: Cross-cutting concerns like rate-limiting and error handling.
- `utils/`: Reusable formatting or shared logic.

Authentication is strictly delegated to Clerk (JWT-based).

## Identified Architectural Issues
1. **Service Layer Bleed:** Endpoint controllers in `api/tracking.py` and `api/opportunity.py` directly handled SQLAlchemy `db.add()` and `db.commit()` logic alongside web scraping orchestration.
2. **Synchronous Heavy Computations:** The `/admin/scrape-batch` endpoint blocked the event loop and web requests until multiple websites were fully scraped.
3. **Missing Caching:** The frequently hit `/opportunities` search endpoint lacked a caching layer despite `CacheService` being present in the repository.
4. **Inefficient Queries:** The `RecommendationEngine` performed N+1 queries when evaluating participation history and reconstructing opportunities from cache.
5. **Rigid Ranking:** Opportunities were always sorted by deadline (implicitly) without a modular way to rank by popularity or relevance.

## Implementation Plan & Code Modifications

### 1. Service Layer Standardization
- **`api/tracking.py`**: Refactored `scrape_and_track_opportunity` to delegate logic to `TrackerService.scrape_and_track_opportunity()`.
- **`api/opportunity.py`**: Refactored `scrape_opportunity` to use `OpportunityService.scrape_and_create_opportunity()`.

### 2. Query Optimization
- **`services/recommendation_service.py`**: Used SQLAlchemy `joinedload` and `with_entities` in `_get_participation_history` to retrieve user history and associated opportunity types in a single query. Optimized cache hit reconstruction to use a batch `.filter(Opportunity.id.in_(...))` rather than iterative loop queries.

### 3. Opportunity Ranking Engine
- **Added `services/ranking_service.py`**: Created a modular `RankingService` that accepts an array of opportunities and sorts them based on `relevance` (calculated by overlapping `tags`/`required_skills` with `user_interests`), `deadline`, or `popularity` (`tracked_count`).
- **Updated `search_opportunities`**: Integrated ranking capability into `OpportunityService.search_opportunities` and exposed `sort_by` as a query parameter in `/api/opportunities`.

### 4. Caching Layer
- **`api/opportunity.py`**: Applied the existing Redis-based `CacheService` to `/opportunities` and `/opportunities/trending` endpoints. Keys are generated deterministically based on filter dictionaries.

### 5. Background Processing
- **Skipped**: Refactoring `/admin/scrape-batch` to use `fastapi.BackgroundTasks` would change the response schema (from returning actual scrape counts to a generic "started" message), which violates the strict constraint to **not break existing API routes**. Therefore, heavy API routes were kept synchronous to maintain contract compatibility with the frontend. Scheduled jobs in `scheduler_service.py` continue to run asynchronously in the background.

## New Modules Added
- `services/ranking_service.py`
- `tests/test_ranking_service.py`

## Instructions for Running and Testing

### 1. Running the Project
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
The API is available at `http://localhost:8000`.

### 2. Testing
Ensure you are in your active Python environment.
```bash
pytest tests/
```
All tests, including the new `test_ranking_service.py`, should execute and pass.