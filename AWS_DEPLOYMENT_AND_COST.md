# AWS Deployment & Cost Estimation for HackItAll

This document details the expected cost and architectural setup for deploying the HackItAll platform on AWS to support 100 users per month. It takes into account the web application, backend API, PostgreSQL database, Redis cache, and the AI-driven scraping infrastructure.

## Deployment Architecture

For 100 users/month, the platform is low-traffic but computationally intense in specific areas (Playwright scraping and local/remote LLM inference).

*   **Frontend (React/Vite):** Hosted statically on Amazon S3 and served via Amazon CloudFront (CDN).
*   **Backend (FastAPI):** Containerized via Docker and deployed using **AWS App Runner** or **ECS Fargate**. App Runner is recommended for simplicity and auto-scaling.
*   **Database (PostgreSQL):** Amazon RDS for PostgreSQL (`db.t4g.micro` instance).
*   **Cache (Redis):** Amazon ElastiCache for Redis (`cache.t4g.micro` node).
*   **AI/LLM (Ollama):** Running a 4B parameter model locally (like `gemma3:4b`) inside a container is expensive (requires memory and potentially a GPU). For 100 users, it is highly recommended to offload LLM extraction to **Amazon Bedrock** (using an equivalent model like Anthropic Claude Haiku or Titan) to save on fixed compute costs.
*   **Authentication:** Handled by Clerk (external service, Free Tier covers <10,000 MAU).

## Monthly Cost Estimation (100 Users/Month)

*Note: All prices are estimates based on US-East-1 region pricing and are subject to change.*

| Component | Service | Specification / Usage | Estimated Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Frontend Hosting** | S3 + CloudFront | < 5 GB bandwidth, minimal storage | ~$1.00 - $2.00 |
| **Backend API** | AWS App Runner | 1 vCPU, 2 GB RAM (provisioned instance) | ~$15.00 |
| **Database** | Amazon RDS (PostgreSQL) | `db.t4g.micro` (Single-AZ), 20GB gp3 storage | ~$13.50 |
| **Caching** | Amazon ElastiCache (Redis) | `cache.t4g.micro` | ~$11.50 |
| **AI Inference** | Amazon Bedrock / External | Pay-per-token (Haiku or similar) for daily batch scraping | ~$2.00 - $5.00 |
| **Networking** | VPC, EIP, NAT (if needed) | Assuming basic public/private subnets | ~$0.00 (within Free Tier/basic setup) |
| **Total Estimated Cost** | | | **~$43.00 - $47.00 / month** |

### Potential Savings / Free Tier
If you are deploying this on a new AWS account, you are eligible for the **AWS Free Tier**:
*   **RDS:** 750 hours/month of `db.t3.micro` or `db.t4g.micro` (Free for 12 months).
*   **ElastiCache:** 750 hours/month of `cache.t2.micro` or `cache.t3.micro` (Free for 12 months).
*   **CloudFront:** 1 TB of data transfer out (Free forever).

**Cost with Free Tier:** ~$15.00 - $20.00 / month (primarily App Runner compute and AI API usage).

## Deployment Checklist

1.  **Configure Clerk:** Ensure your production Clerk publishable and secret keys are securely stored in AWS Secrets Manager or App Runner environment variables.
2.  **Migrate SQLite to RDS:** Change `DATABASE_URL` in your production environment to point to your new RDS instance. The SQLAlchemy models will automatically initialize the tables.
3.  **Optimize AI Scraping:** Re-evaluate running Ollama/Playwright in the same container. Playwright requires a lot of memory, and Ollama requires heavily multi-threaded CPU or GPU. Switch `AI_PROVIDER` to `bedrock` or `openai` to drastically cut App Runner compute requirements.
4.  **Update CORS:** Ensure the `ALLOWED_ORIGINS` environment variable in your backend explicitly includes your final CloudFront domain (e.g., `https://hackitall.com`).