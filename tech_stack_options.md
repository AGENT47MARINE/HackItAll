# Opportunity Access Platform (HackItAll) - Tech Stack & Open Source / AWS Options

This document outlines the current technology stack for the Opportunity Access Platform and provides comprehensive recommendations for open-source alternatives and AWS cloud services suitable for scaling the project.

## 1. Current Technology Stack
- **Backend Framework**: Python / FastAPI
- **Database**: SQLite (via SQLAlchemy)
- **Web Frontend**: React 18, Vite, CSS Modules
- **Mobile Frontend**: React Native, Expo
- **Authentication**: JWT & bcrypt

---

## 2. Recommended Open Source Options

To ensure the platform is robust, cost-effective, and highly scalable, you can adopt the following open-source technologies:

### Database & Storage
- **PostgreSQL**: The best open-source relational database to replace SQLite for production. Excellent for spatial data, JSON, and high concurrency.
- **Redis**: Open-source in-memory data store for caching recommendations, rate-limiting the API, and managing background task queues.
- **MinIO**: High-performance, S3-compatible object storage. If you need to host profile pictures or resume uploads on self-hosted infrastructure before moving to the cloud.

### Backend Infrastructure & Operations
- **Docker**: Containerize the FastAPI backend, React web app, and PostgreSQL database for environment consistency.
- **NGINX or Traefik**: Open-source reverse proxies to handle load balancing, rate limiting, and SSL termination.
- **Celery**: Open-source distributed task queue (works with Redis/RabbitMQ) for handling heavy background duties, such as sending deadline reminder emails or crunching AI recommendations.

### Monitoring & Analytics
- **Prometheus + Grafana**: Open-source monitoring stack. Prometheus collects API metrics (e.g., how many people are using the `/api/recommendations` endpoint), and Grafana provides beautiful dashboards.
- **Sentry (Self-Hosted)**: Excellent for tracking errors in both the FastAPI backend and React/React Native frontends.
- **PostHog**: An open-source product analytics platform to track user interactions and feature usage (e.g., tracking which opportunities are clicked most).

---

## 3. Recommended AWS Services

For a production-grade deployment with high availability and minimal infrastructure management, AWS offers excellent managed services that perfectly complement your stack:

### Compute & Hosting
- **AWS Elastic Beanstalk or AWS App Runner**: For easily deploying the FastAPI backend without managing the underlying EC2 instances.
- **Amazon S3 + Amazon CloudFront (CDN)**: The best combination for hosting the built React (Vite) web application (`dist` folder). CloudFront ensures blazingly fast load times globally.
- **AWS Lambda**: For serverless execution of background tasks (e.g., daily deadline reminder scripts) without needing to run a dedicated Celery worker 24/7.

### Database & Storage
- **Amazon RDS for PostgreSQL**: A fully managed PostgreSQL database with automated backups, patching, and scaling. This is the direct upgrade from your local SQLite db.
- **Amazon ElastiCache for Redis**: Managed Redis for caching and session management.
- **Amazon S3**: For storing user uploads (e.g., resumes, profile pictures).

### Authentication, Security & Notifications
- **Amazon Cognito**: If you want to offload JWT token management and support social logins (Google, Apple) seamlessly across web and mobile.
- **Amazon SNS (Simple Notification Service)** & **Amazon SES (Simple Email Service)**: 
  - **SES**: For sending transactional emails (e.g., "Registration successful" or "Scholarship deadline tomorrow").
  - **SNS**: For sending SMS text messages (useful for low-bandwidth users) and mobile push notifications.
- **AWS WAF (Web Application Firewall)**: Protect your FastAPI endpoints from malicious requests, bots, and DDoS attacks.

### AI & Recommendations
- **Amazon Personalize**: A fully managed machine learning service to deliver highly customized opportunity recommendations to users based on their interactions, saving you from building complex ML models from scratch.

---

## 4. Estimated Monthly Cost (Hackathon Tier)

For a hackathon project, the primary goal is to build a functional prototype at **zero or near-zero cost**. Here is how you can leverage free tiers to keep your costs down:

### Option 1: The "Always Free" Hackathon Stack ($0/month)
This stack uses generous free tiers from alternative providers, ideal for hackathons:

- **Frontend Hosting (React Web)**: Vercel or Netlify (Free Tier) - **$0/month**
- **Backend Hosting (FastAPI)**: Render or Railway (Free Tier/Trial) - **$0/month**
- **Database (PostgreSQL)**: Supabase or Neon (Generous Free Tiers) - **$0/month**
- **Authentication**: Supabase Auth or Firebase Authentication (Free Tiers) - **$0/month**
- **Email Notifications**: Resend or SendGrid (Free Tiers: ~3,000 to 100 emails/day) - **$0/month**
- **Total Estimated Cost**: **$0/month**

### Option 2: The AWS Free Tier Stack (~$0 - $5/month)
If your hackathon requires you to use AWS, you can stick strictly to the AWS Free Tier (available for the first 12 months for new accounts):

- **Compute (FastAPI)**: Amazon EC2 (t2.micro or t3.micro) - **750 hours/month Free**
- **Database**: Amazon RDS for PostgreSQL (db.t3.micro or db.t4g.micro) - **750 hours/month Free** + 20GB DB Storage Free
- **Frontend Hosting**: Amazon S3 + CloudFront - **S3: 5GB Free**, **CloudFront: 1TB transfer out Free**
- **Authentication**: Amazon Cognito - **50,000 MAUs Free**
- **Emails/SMS**: Amazon SES (62,000 emails/month free if sent from EC2) / Amazon SNS (100 SMS messages/month free)
- **AI/Recommendations**: Avoid Amazon Personalize for a hackathon, as it does not have a comprehensive free tier and can become expensive quickly. Instead, build a simple recommendation script in Python using `scikit-learn` or basic heuristics.
- **Total Estimated Cost**: **$0/month** (Assuming you don't exceed the strict free tier limits. Keep an eye on storage and data transfer.)

**Hackathon Pro-Tip:** Always set up **AWS Budgets and Billing Alarms** on day 1 to ensure you don't accidentally spin up expensive resources and get a surprise bill!

---

## Summary Integration Path

1. **Phase 1 (Immediate)**: Dockerize the application and migrate the local SQLite database to an open-source **PostgreSQL** instance.
2. **Phase 2 (Cloud Migration)**: Deploy the FastAPI backend using **AWS App Runner** and the React frontend via **S3 + CloudFront**. Point the app to **Amazon RDS for PostgreSQL**.
3. **Phase 3 (Scale & Features)**: Integrate **Amazon SES/SNS** for reliable notifications and setup **Redis** (ElastiCache) + **Celery/Lambda** for background processing. Use **Prometheus/Grafana** for monitoring system health.
