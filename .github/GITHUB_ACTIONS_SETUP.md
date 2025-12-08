# GitHub Actions Setup for Auto-Deployment

This guide shows you how to set up automatic deployment to your EC2 instance whenever you push to the `main` branch.

## How It Works

```
1. You push code to GitHub
   ↓
2. GitHub Actions triggers
   ↓
3. Connects to your EC2 via SSH
   ↓
4. Pulls latest code
   ↓
5. Rebuilds Docker container
   ↓
6. Restarts service
```

## Prerequisites

- EC2 instance with SSH access
- GitHub repository (already created)
- SSH key pair for EC2 access

## Setup Instructions

### Step 1: Get Your EC2 SSH Key

You already have this from when you set up EC2. It's a `.pem` file.

```bash
# View your private key
cat ~/.ssh/your-ec2-key.pem
```

Copy the entire contents (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`).

### Step 2: Add GitHub Secrets

Go to your GitHub repository:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**

Add these 3 secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `EC2_SSH_PRIVATE_KEY` | Your entire `.pem` file contents | `-----BEGIN RSA PRIVATE KEY-----\nMIIE...` |
| `EC2_HOST` | Your EC2 public IP or hostname | `54.123.45.67` or `ec2-54-123-45-67.compute.amazonaws.com` |
| `EC2_USER` | SSH username | `ec2-user` (Amazon Linux) or `ubuntu` (Ubuntu) |

### Step 3: Initial Setup on EC2

SSH into your EC2 instance and do the initial setup:

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip

# Clone repository
cd ~
git clone https://github.com/dropflyai/TradeFly-Backend.git
cd TradeFly-Backend

# Set up environment variables
cp .env.example .env
nano .env  # Add your API keys

# Do first deployment manually
./deploy.sh
```

### Step 4: Test Auto-Deployment

Now every time you push to `main`, it will auto-deploy!

Test it:
```bash
# Make a small change
echo "# Auto-deploy test" >> README.md
git add README.md
git commit -m "Test auto-deployment"
git push origin main
```

Watch it deploy:
1. Go to GitHub repository → **Actions** tab
2. You'll see the workflow running
3. Click it to watch real-time logs

### Step 5: Manual Deployment (Optional)

You can also trigger deployment manually:
1. Go to **Actions** tab
2. Click **Deploy to AWS EC2** workflow
3. Click **Run workflow**

## Troubleshooting

### "Permission denied (publickey)"

**Problem:** GitHub Actions can't SSH into your EC2.

**Fix:**
- Verify `EC2_SSH_PRIVATE_KEY` secret is the complete private key
- Verify `EC2_USER` is correct (`ec2-user` for Amazon Linux, `ubuntu` for Ubuntu)
- Check EC2 security group allows SSH (port 22) from GitHub Actions IPs

### "Directory not found"

**Problem:** First deployment hasn't been run.

**Fix:** SSH into EC2 and clone the repo manually (see Step 3).

### "Docker command not found"

**Problem:** Docker not installed on EC2.

**Fix:**
```bash
# Amazon Linux 2
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -aG docker ec2-user

# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
```

Log out and log back in for group changes to take effect.

### "Container failed to start"

**Problem:** Missing environment variables or wrong configuration.

**Fix:** SSH into EC2 and check:
```bash
cd ~/TradeFly-Backend
cat .env  # Verify all required vars are set
docker-compose logs
```

## Security Best Practices

✅ **DO:**
- Keep your `.pem` file secure
- Use GitHub Secrets (never commit keys to repo)
- Restrict EC2 Security Group to your IP for SSH
- Use a dedicated deploy key (optional, advanced)

❌ **DON'T:**
- Commit `.pem` files to git
- Share your EC2 private key
- Leave port 22 open to the world (0.0.0.0/0)

## Advanced: Deploy Key (Optional)

Instead of using your main EC2 key, create a deploy-specific key:

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f github_deploy_key

# Copy public key to EC2
ssh-copy-id -i github_deploy_key.pub ec2-user@your-ec2-ip

# Use github_deploy_key (private) in GitHub secret instead
```

## Monitoring Deployments

### View deployment status
- GitHub Actions tab shows all deployments
- Green checkmark = success
- Red X = failed (click to see logs)

### Check running service on EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
docker ps | grep tradefly
docker-compose logs -f
```

## What Gets Auto-Deployed?

Every push to `main` branch deploys:
- Code changes
- Dependency updates (requirements.txt)
- Configuration changes
- Docker changes

**NOT auto-deployed:**
- Environment variables (.env) - you must update manually on EC2
- EC2 system configuration

## Next Steps

1. Set up the 3 GitHub secrets
2. Do initial manual deploy on EC2
3. Push code to test auto-deployment
4. Celebrate! 🎉

Your backend will now auto-deploy on every commit to `main`.
