# EC2 Auto-Launcher

**Automated EC2 instance provisioning with security best practices**

## Status
🚧 Under development

## What It Will Do

Launch secure EC2 instances with one command:
- Security groups (SSH restricted to your IP)
- IAM roles (least privilege)
- Auto-generated SSH keys
- Cost optimization
- Security hardening

## Installation

```bash
pip install -r requirements.txt
```

Setup

1. Configure AWS credentials:

```bash
aws configure
```

2. Test connection:

```bash
python src/launcher.py
```

Roadmap

• [x] Project setup
• [x] AWS connection test
• [x] Security group creation
• [x] Key pair management
• [x] Instance launch
• [ ] Security hardening
• [ ] Cost optimization features
Tech Stack

• Python 3.8+
• boto3 (AWS SDK)
• AWS EC2

Built by Max Steele | Learning AI Solutions Architecture
