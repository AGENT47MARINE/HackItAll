# AWS Deployment Guide - Technical Design Document

## Overview

This design document specifies the structure, content organization, and technical artifacts for a comprehensive AWS deployment guide targeting the HackItAll FastAPI application. The guide is designed for developers with zero AWS experience and provides a complete path from account creation to production deployment with stable URLs, security best practices, and cost optimization.

### Design Goals

1. **Progressive Complexity**: Structure content to build knowledge incrementally, avoiding overwhelming beginners
2. **Multiple Learning Styles**: Support visual learners (diagrams), hands-on learners (CLI commands), and conceptual learners (explanations)
3. **Practical Focus**: Prioritize actionable steps over theoretical knowledge
4. **Safety First**: Emphasize security and cost control throughout
5. **Maintainability**: Design for easy updates as AWS services evolve

### Target Audience

- Developers with FastAPI/Python experience
- Zero to minimal AWS experience
- Comfortable with command-line interfaces
- Need production deployment for HackItAll application

### Deployment Architecture Summary

The guide will document deployment of:
- **Application Layer**: FastAPI app on AWS Elastic Beanstalk (Docker platform)
- **Database Layer**: PostgreSQL on AWS RDS
- **Caching Layer**: Redis (ElastiCache or containerized)
- **Secrets Management**: AWS Secrets Manager
- **Networking**: VPC, Security Groups, Load Balancer
- **Monitoring**: CloudWatch Logs and Metrics
- **Optional**: Custom domain via Route 53, CI/CD pipelines

## Architecture

### Document Structure Architecture

The deployment guide will be organized as a single comprehensive markdown document with the following hierarchical structure:

```
AWS Deployment Guide
├── 1. Introduction
│   ├── 1.1 What You'll Build
│   ├── 1.2 Architecture Overview (Diagram)
│   ├── 1.3 Time Estimates
│   └── 1.4 Prerequisites Checklist
├── 2. Glossary
│   └── AWS terminology with beginner-friendly definitions
├── 3. Phase 1: AWS Account and Tools Setup
│   ├── 3.1 Creating Your AWS Account
│   ├── 3.2 Installing Required Tools
│   ├── 3.3 Configuring AWS CLI
│   ├── 3.4 Setting Up IAM User
│   └── 3.5 Verification Steps
├── 4. Phase 2: Database Setup (RDS PostgreSQL)
│   ├── 4.1 Creating RDS Instance
│   ├── 4.2 Security Group Configuration
│   ├── 4.3 Database Initialization
│   ├── 4.4 Connection Testing
│   └── 4.5 Data Migration (Optional)
├── 5. Phase 3: Redis Caching Setup
│   ├── 5.1 Option A: ElastiCache Redis
│   ├── 5.2 Option B: Containerized Redis
│   └── 5.3 Connection Verification
├── 6. Phase 4: Secrets and Environment Configuration
│   ├── 6.1 AWS Secrets Manager Setup
│   ├── 6.2 Environment Variables Configuration
│   ├── 6.3 IAM Roles and Permissions
│   └── 6.4 AI Services Credentials
├── 7. Phase 5: Application Deployment (Elastic Beanstalk)
│   ├── 7.1 Creating Elastic Beanstalk Application
│   ├── 7.2 Environment Configuration
│   ├── 7.3 Docker Platform Setup
│   ├── 7.4 Deploying Application Code
│   ├── 7.5 Health Check Configuration
│   └── 7.6 Finding Your Stable URL
├── 8. Phase 6: Post-Deployment Configuration
│   ├── 8.1 SSL/TLS Certificate Setup
│   ├── 8.2 Custom Domain Configuration (Optional)
│   ├── 8.3 CORS Configuration
│   └── 8.4 Playwright Verification
├── 9. Monitoring and Logging
│   ├── 9.1 CloudWatch Logs Setup
│   ├── 9.2 Metrics and Alarms
│   ├── 9.3 Log Analysis
│   └── 9.4 Health Monitoring
├── 10. Deployment Operations
│   ├── 10.1 Deploying Updates
│   ├── 10.2 Rolling Back Deployments
│   ├── 10.3 Environment Management
│   └── 10.4 Zero-Downtime Deployments
├── 11. Security Best Practices
│   ├── 11.1 Security Group Hardening
│   ├── 11.2 Encryption Configuration
│   ├── 11.3 Credential Rotation
│   └── 11.4 Pre-Launch Security Checklist
├── 12. Cost Management
│   ├── 12.1 Cost Breakdown by Service
│   ├── 12.2 Free Tier Eligibility
│   ├── 12.3 Billing Alerts Setup
│   ├── 12.4 Cost Optimization Tips
│   └── 12.5 Development vs Production Costs
├── 13. CI/CD Pipeline Setup (Optional)
│   ├── 13.1 GitHub Actions Integration
│   ├── 13.2 AWS CodePipeline Setup
│   └── 13.3 Automated Testing Integration
├── 14. Alternative Deployment Options
│   ├── 14.1 Comparison Table
│   ├── 14.2 ECS/Fargate Overview
│   └── 14.3 EC2 Direct Deployment
├── 15. Troubleshooting Guide
│   ├── 15.1 Common Deployment Errors
│   ├── 15.2 Database Connection Issues
│   ├── 15.3 Playwright Browser Issues
│   ├── 15.4 Environment Variable Problems
│   └── 15.5 Performance Issues
├── 16. Quick Start Checklist
│   └── Pre-launch verification steps
└── 17. Additional Resources
    └── Links to AWS documentation and tools
```

### Information Architecture Principles

1. **Sequential Flow**: Each phase builds on previous phases
2. **Self-Contained Sections**: Each section can be referenced independently
3. **Consistent Formatting**: Standardized patterns for commands, warnings, and tips
4. **Progressive Disclosure**: Basic path in main content, advanced options in subsections
5. **Visual Hierarchy**: Clear heading levels, callout boxes, and code blocks

### AWS Services Architecture

The guide documents the following AWS service interactions:

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Route 53 (Optional)│
              │   Custom Domain      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Application Load    │
              │  Balancer (ALB)      │
              │  - Stable URL        │
              │  - SSL/TLS           │
              └──────────┬───────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │   Elastic Beanstalk Environment   │
         │  ┌─────────────────────────────┐  │
         │  │  EC2 Instance(s)            │  │
         │  │  - Docker Platform          │  │
         │  │  - FastAPI Container        │  │
         │  │  - (Optional) Redis Container│ │
         │  └─────────────────────────────┘  │
         └───────────┬───────────────────────┘
                     │
         ┌───────────┼───────────────────────┐
         │           │                       │
         ▼           ▼                       ▼
    ┌────────┐  ┌────────┐         ┌──────────────┐
    │  RDS   │  │ElastiCache        │   Secrets    │
    │PostgreSQL  │ Redis  │         │   Manager    │
    │        │  │(Optional)         │              │
    └────────┘  └────────┘         └──────────────┘
         │
         ▼
    ┌────────┐
    │CloudWatch
    │ Logs   │
    └────────┘
```

### Security Architecture

The guide will document the following security layers:

1. **Network Security**:
   - VPC with public/private subnets
   - Security Groups with least-privilege rules
   - Network ACLs (default configuration)

2. **Access Control**:
   - IAM users with limited permissions
   - IAM roles for service-to-service communication
   - No hardcoded credentials

3. **Data Protection**:
   - RDS encryption at rest
   - SSL/TLS for data in transit
   - Secrets Manager for sensitive data

4. **Application Security**:
   - HTTPS-only endpoints
   - CORS configuration
   - Health check endpoints

## Components and Interfaces

### Document Components

#### 1. Narrative Sections

**Purpose**: Explain concepts and provide context

**Structure**:
```markdown
### Section Title

[Beginner-friendly explanation]

**Why This Matters**: [Real-world impact]

**Key Concepts**:
- Concept 1: Definition
- Concept 2: Definition
```

#### 2. Step-by-Step Procedures

**Purpose**: Provide actionable instructions

**Structure**:
```markdown
### Task Title

**Estimated Time**: X minutes

**Prerequisites**:
- Prerequisite 1
- Prerequisite 2

**Steps**:

1. **Step Name**: Description
   
   **Via AWS Console**:
   - Sub-step 1
   - Sub-step 2
   - [Screenshot placeholder]
   
   **Via AWS CLI**:
   ```bash
   aws command --parameter VALUE
   ```
   
   **Expected Output**:
   ```
   Output example
   ```

2. **Next Step**: Description
   ...

**Verification**:
```bash
# Command to verify success
```

**Troubleshooting**:
- If X happens: Do Y
```

#### 3. Configuration Templates

**Purpose**: Provide copy-paste ready configuration files

**Types**:
- Dockerrun.aws.json (multi-container)
- .ebextensions/*.config files
- GitHub Actions workflows
- Environment variable templates
- IAM policy documents

**Structure**:
```markdown
### Configuration File: filename.ext

**Purpose**: What this file does

**Location**: Where to place it

```language
# Configuration content with comments
# PLACEHOLDER values marked clearly
```

**Customization**:
- Replace PLACEHOLDER_1 with: explanation
- Replace PLACEHOLDER_2 with: explanation
```

#### 4. Decision Trees

**Purpose**: Help users choose between options

**Structure**:
```markdown
### Choosing [Option Type]

**Decision Factors**:

| Factor | Option A | Option B |
|--------|----------|----------|
| Cost | $X/month | $Y/month |
| Complexity | Low | Medium |
| Free Tier | Yes | No |

**Choose Option A if**:
- Condition 1
- Condition 2

**Choose Option B if**:
- Condition 1
- Condition 2

**Recommendation**: For beginners, we recommend Option A because...
```

#### 5. Architecture Diagrams

**Purpose**: Visual representation of system structure

**Format**: Mermaid diagrams embedded in markdown

**Types**:
- Overall system architecture
- Network topology
- Data flow diagrams
- Deployment process flow
- CI/CD pipeline flow

#### 6. Command Reference Tables

**Purpose**: Quick reference for common operations

**Structure**:
```markdown
### Common Commands

| Task | AWS CLI Command | Notes |
|------|----------------|-------|
| Task 1 | `aws service action` | When to use |
| Task 2 | `aws service action` | When to use |
```

#### 7. Cost Estimation Tables

**Purpose**: Transparent cost information

**Structure**:
```markdown
### Cost Breakdown

| Service | Configuration | Monthly Cost | Free Tier |
|---------|--------------|--------------|-----------|
| Elastic Beanstalk | t3.micro | $0 | Platform free |
| RDS PostgreSQL | db.t3.micro | $15 | 750 hrs/month |
| ElastiCache | cache.t3.micro | $12 | No |

**Total Estimated Cost**: $X/month (after free tier)
**Development Setup**: $Y/month
**Production Setup**: $Z/month
```

#### 8. Troubleshooting Sections

**Purpose**: Help users resolve common issues

**Structure**:
```markdown
### Error: [Error Message or Symptom]

**Symptoms**:
- What you see
- Where it appears

**Causes**:
- Possible cause 1
- Possible cause 2

**Solutions**:

1. **Try This First**:
   ```bash
   command to fix
   ```
   
2. **If That Doesn't Work**:
   - Alternative solution

**Prevention**:
How to avoid this issue in the future
```

#### 9. Callout Boxes

**Purpose**: Highlight important information

**Types and Formatting**:

```markdown
> **💡 TIP**: Helpful suggestion for better results

> **⚠️ WARNING**: Important caution about potential issues

> **💰 COST ALERT**: Information about charges or cost implications

> **🔒 SECURITY**: Security best practice or consideration

> **📝 NOTE**: Additional context or clarification

> **🎯 BEGINNER FRIENDLY**: Simplified explanation for complex topics
```

### Interface Specifications

#### User Interaction Patterns

1. **Command Execution**:
   - All commands in copy-paste ready code blocks
   - Placeholders in UPPERCASE or <angle-brackets>
   - Explanation before command
   - Expected output after command

2. **AWS Console Navigation**:
   - Breadcrumb-style navigation paths
   - Example: "AWS Console > Services > Elastic Beanstalk > Environments"
   - Screenshot placeholders with descriptive alt text

3. **Verification Steps**:
   - Every major step includes verification
   - Clear success/failure indicators
   - Next steps for both outcomes

4. **Progressive Disclosure**:
   - Basic path in main content
   - "Advanced Options" in collapsible sections
   - "Learn More" links to AWS docs

## Data Models

### Configuration File Templates

#### 1. Dockerrun.aws.json (Single Container)

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "YOUR_DOCKER_IMAGE",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 80
    }
  ],
  "Logging": "/var/log/nginx"
}
```

#### 2. Dockerrun.aws.json (Multi-Container with Redis)

```json
{
  "AWSEBDockerrunVersion": 2,
  "containerDefinitions": [
    {
      "name": "fastapi-app",
      "image": "YOUR_DOCKER_IMAGE",
      "essential": true,
      "memory": 512,
      "portMappings": [
        {
          "hostPort": 80,
          "containerPort": 8000
        }
      ],
      "links": ["redis"],
      "environment": [
        {
          "name": "REDIS_URL",
          "value": "redis://redis:6379"
        }
      ]
    },
    {
      "name": "redis",
      "image": "redis:7-alpine",
      "essential": true,
      "memory": 256,
      "portMappings": [
        {
          "hostPort": 6379,
          "containerPort": 6379
        }
      ]
    }
  ]
}
```

#### 3. .ebextensions/01_environment.config

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    ENVIRONMENT: production
    LOG_LEVEL: INFO
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.micro
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
```

#### 4. .ebextensions/02_https_redirect.config

```yaml
files:
  "/etc/nginx/conf.d/https_redirect.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      server {
        listen 80;
        return 301 https://$host$request_uri;
      }
```

#### 5. Environment Variables Template

```bash
# Database Configuration
DATABASE_URL=postgresql://USER:PASSWORD@RDS_ENDPOINT:5432/DATABASE_NAME

# Redis Configuration
REDIS_URL=redis://REDIS_ENDPOINT:6379

# Application Configuration
SECRET_KEY=YOUR_SECRET_KEY_HERE
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend-domain.com

# AI Services
AI_PROVIDER=openai  # or anthropic, bedrock
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# AWS Configuration (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

#### 6. IAM Policy for Secrets Manager Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME*"
    }
  ]
}
```

#### 7. IAM Policy for Bedrock Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

#### 8. GitHub Actions Workflow

```yaml
name: Deploy to AWS Elastic Beanstalk

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Generate deployment package
      run: zip -r deploy.zip . -x '*.git*'
    
    - name: Deploy to EB
      uses: einaregilsson/beanstalk-deploy@v21
      with:
        aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        application_name: hackitall-app
        environment_name: hackitall-prod
        version_label: ${{ github.sha }}
        region: us-east-1
        deployment_package: deploy.zip
```

#### 9. Python Code for Secrets Manager Retrieval

```python
import boto3
import json
from functools import lru_cache

@lru_cache()
def get_secret(secret_name: str, region_name: str = "us-east-1") -> dict:
    """
    Retrieve secret from AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        region_name: AWS region where secret is stored
        
    Returns:
        Dictionary containing secret key-value pairs
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        raise Exception(f"Error retrieving secret: {str(e)}")
    
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# Usage example
if __name__ == "__main__":
    secrets = get_secret("hackitall/production")
    database_url = secrets.get("DATABASE_URL")
    openai_key = secrets.get("OPENAI_API_KEY")
```

### CLI Command Sequences

#### Complete Deployment Command Sequence

```bash
# 1. Initialize EB CLI in project directory
eb init -p docker -r us-east-1 hackitall-app

# 2. Create environment
eb create hackitall-prod \
  --instance-type t3.micro \
  --envvars DATABASE_URL=postgresql://...,REDIS_URL=redis://... \
  --tags Project=HackItAll,Environment=Production

# 3. Check environment status
eb status

# 4. Open application in browser
eb open

# 5. View logs
eb logs

# 6. Deploy updates
eb deploy

# 7. Rollback if needed
eb deploy --version VERSION_LABEL
```

#### RDS Creation Command

```bash
aws rds create-db-instance \
  --db-instance-identifier hackitall-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-XXXXXXXXX \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --publicly-accessible false \
  --tags Key=Project,Value=HackItAll Key=Environment,Value=Production
```

#### ElastiCache Redis Creation Command

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id hackitall-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --security-group-ids sg-XXXXXXXXX \
  --tags Key=Project,Value=HackItAll Key=Environment,Value=Production
```

#### Secrets Manager Commands

```bash
# Create secret
aws secretsmanager create-secret \
  --name hackitall/production \
  --description "Production secrets for HackItAll application" \
  --secret-string file://secrets.json

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id hackitall/production \
  --query SecretString \
  --output text

# Update secret
aws secretsmanager update-secret \
  --secret-id hackitall/production \
  --secret-string file://secrets.json

# Rotate secret
aws secretsmanager rotate-secret \
  --secret-id hackitall/production
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Since this is a documentation project rather than a software system, traditional property-based testing doesn't directly apply. However, we can define correctness properties for the documentation itself that ensure it meets its requirements.

