Proposed Architecture Stack
* Amazon EC2 (for hosting the backend and AI models)
* Amazon RDS (for database)
* Amazon S3 (for storage)
* Optional: AWS Lambda mapping to API Gateway
* Other: Amazon CloudFront (CDN for frontend), Docker

What's the specific GenAI model you're using?
* Meta Llama 3 (8B) or Mistral 7B. We are opting for open-weights models to ensure cost-efficiency and flexibility. During the hackathon, we may run these locally or via free-tier inference APIs (like Groq or Together AI) and eventually containerize them on AWS EC2 or deploy them via AWS SageMaker if credits permit.

What's your data strategy?
* Data Sources: User profiles (skills, education, interests), opportunity data (hackathons, scholarships scraped or provided via APIs), and user interaction history (saved/applied opportunities).
* Storage & Processing: User and structured opportunity data will be stored in Amazon RDS (PostgreSQL) for reliable relational access. Resumes and profile images will be stored in Amazon S3. The FastAPI backend running on Amazon EC2 (or App Runner) will process incoming data and format prompt context to invoke our open-source GenAI model (e.g., Llama 3) for generating personalized opportunity recommendations.

What is your "24-hour Goal"?
* Deploy the foundational cloud infrastructure: Set up the PostgreSQL database on Amazon RDS, configure the S3 bucket for assets, and deploy the core FastAPI backend to an Amazon EC2 instance. Ensure the backend can successfully connect to the database and interface with our chosen open-source GenAI model (e.g., via a free inference API like Groq) to generate the first set of personalized recommendations.
