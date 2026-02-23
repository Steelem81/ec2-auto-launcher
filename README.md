# EC2 Auto-Launcher

**Automated EC2 instance provisioning with security-first design**

One command to launch production-ready, hardened AWS EC2 instances with proper security groups, SSH key management, and resource cleanup.

---

## Problem

Manual EC2 setup through AWS Console is:
- ⏱️ **Slow:** 15-30 minutes per instance
- ❌ **Error-prone:** Easy to misconfigure security (SSH open to 0.0.0.0/0)
- 💸 **Costly:** Wrong instance types, forgotten resources
- 📝 **Not repeatable:** "How did I configure that server 3 months ago?"

## Solution

EC2 Auto-Launcher automates secure instance provisioning in **under 2 minutes** with:

- ✅ Security groups auto-configured (SSH restricted to your IP only)
- ✅ SSH key pairs generated and stored securely (chmod 0400)
- ✅ Idempotent operations (reuses existing resources)
- ✅ Resource cleanup command (no orphaned resources)
- ✅ Tagged for cost tracking and organization

---

## Features

### Security-First Design

- **Dynamic IP whitelisting:** Automatically restricts SSH to your current IP
- **Secure key storage:** Private keys saved with proper permissions (0400)
- **IMDSv2 support:** Protection against SSRF attacks on instance metadata
- **Least-privilege IAM:** Only necessary permissions granted

### Resource Management

- **Idempotent operations:** Check before create - safe to run multiple times
- **Cleanup mode:** Delete test resources with `--cleanup` flag
- **Resource tagging:** Auto-tags instances for cost tracking

### Developer Experience

- **One-command launch:** No clicking through AWS Console
- **CLI interface:** Simple, intuitive commands
- **Clear error messages:** Know exactly what went wrong
- **Configurable:** Easy to customize instance types, AMIs, regions

---

## Installation

### Prerequisites

- Python 3.8+
- AWS account with EC2 permissions
- AWS CLI configured

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ec2-auto-launcher.git
cd ec2-auto-launcher

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region, Output format
```
---

## Usage

### Launch an Instance

```bash
python src/launcher.py
```

Output:

```bash
==================================================
EC2 Auto-Launcher
==================================================
EC2 Launcher initialized (Region: us-east-1)
AWS connection successful!
Your public IP: 123.45.67.89
Using existing security group: sg-0abc123def456
Key pair created: keys/auto-launcher-key.pem
Launching instance...
Instance launched: i-0123456789abcdef
Waiting for instance to start...
Instance running at: 54.123.45.67

==================================================
SUCCESS!
Instance ID: i-0123456789abcdef
Public IP: 54.123.45.67
SSH Command: ssh -i keys/auto-launcher-key.pem ec2-user@54.123.45.67
==================================================

```
### SSH into Your Instance

```bash
ssh -i keys/auto-launcher-key.pem ec2-user@54.123.45.67
```

### Cleanup Resources

```bash
python src/launcher.py --cleanup
```

Deletes:
• Security group
• Key pair (AWS + local .pem file)

Note: Terminate instances manually via AWS Console or:

```bash 
aws ec2 terminate-instances --instance-ids i-0123456789abcdef
```

## Configuration

Edit .env to customize:

```bash
# AWS Configuration
AWS_REGION=us-east-1

# Instance Settings
DEFAULT_INSTANCE_TYPE=t2.micro  # Free tier eligible
DEFAULT_AMI=ami-0c55b159cbfafe1f0  # Amazon Linux 2 (region-specific)

# Resource Names
KEY_PAIR_NAME=auto-launcher-key
SECURITY_GROUP_NAME=auto-launcher-sg
```


Architecture

```bash
┌─────────────────────────────────────────────────────┐
│                 EC2 Auto-Launcher                   │

Carl, [2/22/2026 8:24 AM]
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ Security │   │   Key    │   │   EC2    │
  │  Group   │   │   Pair   │   │ Instance │
  └──────────┘   └──────────┘   └──────────┘
        │               │               │
        │ SSH: Your IP  │ .pem saved    │ Tagged
        │ only (port 22)│ chmod 0400    │ Auto-configured
        └───────────────┴───────────────┘

```
---

Security Considerations

Implemented
• SSH access restricted to your IP (no 0.0.0.0/0!)
• Private keys stored securely (read-only by owner)
• Keys never committed to git (.gitignore configured)
• IMDSv2 enabled (protects against SSRF)
• Resource tagging (track what's deployed)

Best Practices
• Rotate keys regularly: Delete old keys, generate new ones
• Update IP when it changes: Re-run launcher or update SG manually
• Terminate unused instances: Avoid surprise AWS bills
• Use IAM roles: For production, attach roles instead of keys

Tech Stack
• Python 3.8+
• boto3: AWS SDK for Python
• click: CLI framework
• python-dotenv: Environment variable management
• requests: HTTP library for IP detection

---

## What I Learned

### AWS Fundamentals
• EC2 instance lifecycle (pending → running → stopping → terminated)
• Security groups as virtual firewalls
• Key pair management and SSH access
• IAM permissions for EC2 operations
• Region-specific AMI IDs

### Engineering Patterns
• Idempotent operations: Check-before-create pattern
• Resource lifecycle management: Create, use, cleanup
• CLI tool design: Flags, defaults, error handling
• Security-first development: Least privilege, defense in depth

### Debugging Skills
• Variable shadowing bugs (hardcoded values overwriting correct ones)
• SSH connection troubleshooting (security groups, IP changes, permissions)
• AWS error message interpretation
• Systematic debugging methodology

## Roadmap

Planned Features
• [ ] Multiple instance profiles (web-server, database, etc.)
• [ ] Auto-terminate after X hours (cost control)
• [ ] CloudWatch monitoring setup
• [ ] Multiple region support
• [ ] Instance user data (auto-install packages)
• [ ] Elastic IP allocation
• [ ] Cost estimation before launch

Stretch Goals
• [ ] Web UI for non-technical users
• [ ] Terraform integration
• [ ] Auto-scaling group support
• [ ] Load balancer configuration

## Contributing
This is a learning project, but suggestions welcome! Open an issue if you find bugs or have ideas.

## License
MIT License - feel free to use for your own projects!

Author
Max Steele
Aspiring AI Solutions Architect | Security-First Development

Built as part of my journey to become an AI Solutions Architect.
Learning AWS, Python automation, and security best practices through hands-on projects.
