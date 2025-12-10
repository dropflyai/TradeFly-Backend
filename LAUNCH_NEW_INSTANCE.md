# Launch New EC2 Instance for TradeFly

## Step 1: Go to AWS EC2 Console

1. Go to https://console.aws.amazon.com/ec2/
2. Click **"Launch Instance"**

---

## Step 2: Configure Instance

### Name and Tags
- **Name:** `TradeFly-Production`

### Application and OS Images (AMI)
- **AMI:** Ubuntu Server 24.04 LTS (or 22.04 LTS)
- **Architecture:** 64-bit (x86)

### Instance Type
- **Type:** `t3.small` ($15/month - good starting point)
- Or `t3.medium` ($30/month - if you need more power)

### Key Pair
- **Select:** `Botthentic n8n` (same as your existing instance)
- This lets you SSH with the same key

### Network Settings
Click **"Edit"** and configure:

- **VPC:** (select the same VPC as your n8n instance)
- **Subnet:** `subnet-0862376a7dfb9c0b8` (same as n8n)
- **Auto-assign Public IP:** Enable
- **Firewall (Security Groups):** Create new security group
  - **Name:** `TradeFly-Production-SG`
  - **Description:** Security group for TradeFly API server

**Inbound Rules:**
| Type  | Protocol | Port Range | Source    | Description          |
|-------|----------|------------|-----------|----------------------|
| SSH   | TCP      | 22         | 0.0.0.0/0 | SSH access           |
| HTTP  | TCP      | 80         | 0.0.0.0/0 | HTTP traffic         |
| HTTPS | TCP      | 443        | 0.0.0.0/0 | HTTPS traffic (SSL)  |

### Configure Storage
- **Size:** 20 GB gp3
- **Type:** General Purpose SSD (gp3)

### Advanced Details
Scroll down to **IAM instance profile:**
- **Select:** `TradeFly-EC2-SSM-Profile`
- This allows me to deploy code via SSM (same as your n8n instance)

---

## Step 3: Launch

1. Click **"Launch Instance"**
2. Wait for instance to start (1-2 minutes)
3. Click on the instance ID
4. **Copy the Public IP address** and send it to me

---

## After Launch: What I'll Do

Once you give me the new instance ID and IP, I will:

1. Install Python 3.12 and all dependencies
2. Deploy TradeFly backend code
3. Set up systemd service (auto-restart)
4. Install and configure Nginx
5. Get SSL certificate for api.tradeflyai.com
6. Test all endpoints

---

## Cost Comparison

**Option 1: t3.small**
- 2 vCPU, 2GB RAM
- $15/month
- Good for moderate traffic

**Option 2: t3.medium**
- 2 vCPU, 4GB RAM
- $30/month
- Better for heavy market scans

**Recommendation:** Start with t3.small, upgrade later if needed.

---

## After You Launch

Send me:
1. **Instance ID** (e.g., i-0abc123def456)
2. **Public IP address** (e.g., 1.2.3.4)

Then I'll handle the rest!
