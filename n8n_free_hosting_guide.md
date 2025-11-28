# 🚀 n8n Free Hosting Guide - Deploy Your Automation Platform

## 🎯 Best Free Hosting Options for n8n

### 1. 🥇 **Railway** (RECOMMENDED)
**Free Tier**: $5 credit monthly, 512MB RAM, 1GB disk, always-on
**Perfect for n8n with persistent storage**

### 2. 🥈 **Render** 
**Free Tier**: 512MB RAM, always-on, PostgreSQL included
**Great Docker support**

### 3. 🥉 **Fly.io**
**Free Tier**: 3 shared VMs, 160GB bandwidth/month
**Excellent for global deployment**

### 4. 💡 **Oracle Cloud Always Free**
**Free Tier**: 1-4 ARM CPUs, 6-24GB RAM, 200GB storage
**Most powerful option but requires setup**

---

## 🚀 Railway Deployment (RECOMMENDED)

### Step 1: Prepare Your Files

Create a `Dockerfile` in your project:

```dockerfile
FROM node:18-alpine

# Install n8n globally
RUN npm install -g n8n

# Set working directory
WORKDIR /data

# Create necessary directories
RUN mkdir -p /data/.n8n

# Set environment variables
ENV N8N_USER_FOLDER=/data/.n8n
ENV DB_TYPE=sqlite
ENV DB_SQLITE_DATABASE=/data/database.sqlite
ENV N8N_BASIC_AUTH_ACTIVE=true
ENV N8N_BASIC_AUTH_USER=admin
ENV N8N_BASIC_AUTH_PASSWORD=your-secure-password
ENV WEBHOOK_URL=https://your-app.railway.app

# Expose port
EXPOSE 5678

# Start n8n
CMD ["n8n", "start"]
```

Create a `railway.toml` file:

```toml
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "always"

[[services]]
name = "n8n"

[services.variables]
N8N_PORT = "5678"
N8N_PROTOCOL = "https"
N8N_HOST = "0.0.0.0"
GENERIC_TIMEZONE = "UTC"
```

### Step 2: Deploy to Railway

1. **Sign up** at [railway.app](https://railway.app) with GitHub
2. **Connect GitHub repo** with your n8n files
3. **Add environment variables**:
   ```
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=your-secure-password
   N8N_ENCRYPTION_KEY=your-32-character-key
   WEBHOOK_URL=https://your-app.railway.app
   ```
4. **Deploy** - Railway auto-deploys from your repo
5. **Get your URL** - Railway provides a public URL

### Step 3: Import Your Workflow

1. Access your Railway n8n URL
2. Login with your credentials
3. Import `n8n_bill_automation_workflow.json`
4. Configure credentials (Google Drive, OpenAI, etc.)

---

## 🐳 Render Deployment

### Step 1: Create render.yaml

```yaml
services:
  - type: web
    name: n8n-automation
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: N8N_BASIC_AUTH_ACTIVE
        value: true
      - key: N8N_BASIC_AUTH_USER
        value: admin
      - key: N8N_BASIC_AUTH_PASSWORD
        generateValue: true
      - key: N8N_ENCRYPTION_KEY
        generateValue: true
      - key: DB_TYPE
        value: postgresdb
      - key: DB_POSTGRESDB_HOST
        fromDatabase:
          name: n8n-db
          property: host
      - key: DB_POSTGRESDB_DATABASE
        fromDatabase:
          name: n8n-db
          property: database
      - key: DB_POSTGRESDB_USER
        fromDatabase:
          name: n8n-db
          property: user
      - key: DB_POSTGRESDB_PASSWORD
        fromDatabase:
          name: n8n-db
          property: password

databases:
  - name: n8n-db
    databaseName: n8n
```

### Step 2: Deploy

1. **Connect GitHub** to [render.com](https://render.com)
2. **Select repository** with your n8n files
3. **Configure service** - Render reads render.yaml
4. **Deploy** - Auto-deployment with PostgreSQL database

---

## ✈️ Fly.io Deployment

### Step 1: Install Fly CLI

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
fly auth login
```

### Step 2: Create fly.toml

```toml
app = "your-n8n-app"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  N8N_PORT = "8080"
  N8N_PROTOCOL = "https"
  N8N_HOST = "0.0.0.0"

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[mounts]
  destination = "/data"
  source = "n8n_data"
```

### Step 3: Deploy

```bash
# Create volume for persistent storage
fly volumes create n8n_data --size 1 --region iad

# Deploy app
fly deploy

# Set secrets
fly secrets set N8N_BASIC_AUTH_PASSWORD=your-password
fly secrets set N8N_ENCRYPTION_KEY=your-32-char-key
```

---

## 🔧 Docker Compose for Self-Hosting

If you prefer self-hosting on a VPS:

```yaml
version: '3.8'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "80:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-password
      - N8N_HOST=your-domain.com
      - N8N_PROTOCOL=https
      - N8N_PORT=5678
      - WEBHOOK_URL=https://your-domain.com/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:13
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

---

## 🔐 Security Configuration

### Essential Environment Variables

```bash
# Authentication
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=your-username
N8N_BASIC_AUTH_PASSWORD=your-secure-password

# Encryption (32 characters)
N8N_ENCRYPTION_KEY=your-very-secure-32-character-key

# Security
N8N_BLOCK_ENV_ACCESS_IN_NODE=true
N8N_SECURE_COOKIE=true

# HTTPS (for production)
N8N_PROTOCOL=https
N8N_HOST=your-domain.com
```

---

## 📊 Platform Comparison

| Platform | RAM | Storage | Database | Uptime | Ease |
|----------|-----|---------|----------|---------|------|
| Railway | 512MB | 1GB | SQLite | 100% | ⭐⭐⭐⭐⭐ |
| Render | 512MB | SSD | PostgreSQL | 100% | ⭐⭐⭐⭐ |
| Fly.io | 256MB | 3GB | SQLite | 100% | ⭐⭐⭐ |
| Oracle | 24GB | 200GB | Any | 100% | ⭐⭐ |

---

## 🚀 Quick Start - Railway (5 Minutes)

1. **Fork this repo** to your GitHub
2. **Sign up** at [railway.app](https://railway.app)
3. **Import project** from GitHub
4. **Add environment variables**:
   - `N8N_BASIC_AUTH_PASSWORD`: your-password
   - `N8N_ENCRYPTION_KEY`: generate-32-chars
5. **Deploy** - Get your URL in 2-3 minutes!

---

## 🔄 Migration from Local to Cloud

### Export Your Workflows
```bash
# From your local n8n
n8n export:workflow --all --output=./workflows.json
```

### Import to Cloud n8n
1. Access your hosted n8n instance
2. Go to **Settings > Import/Export**
3. Upload your `workflows.json` file
4. Reconfigure credentials for cloud environment

---

## 💡 Pro Tips

### 1. **Always Use HTTPS** in Production
Set `N8N_PROTOCOL=https` and `N8N_SECURE_COOKIE=true`

### 2. **Backup Your Data**
Most platforms provide automatic backups, but export workflows regularly

### 3. **Monitor Usage**
Keep track of your free tier limits:
- Railway: $5/month credit
- Render: 750 hours/month
- Fly.io: 160GB bandwidth

### 4. **Environment Management**
- Use different instances for development/production
- Keep sensitive credentials in environment variables
- Never commit credentials to git

### 5. **Performance Optimization**
```bash
# Optimize for production
N8N_LOG_LEVEL=warn
N8N_METRICS=true
DB_POSTGRESDB_POOL_SIZE=5
```

---

## 🚨 Important Notes

⚠️ **Free Tier Limitations**:
- Railway: $5 credit/month (usually enough for n8n)
- Render: Goes to sleep after 15min inactivity
- Fly.io: 3 apps maximum on free tier

✅ **Best for Production**: Railway or paid tiers for mission-critical workflows

🔄 **Automatic Updates**: Most platforms support auto-deployment from git

📱 **Mobile Access**: All solutions provide responsive web interface

---

## 🆘 Troubleshooting

### Common Issues:

1. **App won't start**: Check environment variables
2. **Database errors**: Verify connection strings
3. **Authentication fails**: Confirm AUTH variables
4. **Webhooks not working**: Update WEBHOOK_URL
5. **Workflows disappear**: Check persistent storage

### Debug Commands:
```bash
# Check logs
fly logs -a your-app  # Fly.io
railway logs          # Railway

# Connect to instance
fly ssh console       # Fly.io
railway shell         # Railway
```

---

## 📞 Support Resources

- **n8n Docs**: [docs.n8n.io](https://docs.n8n.io)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Community**: [community.n8n.io](https://community.n8n.io)

---

**Ready to deploy? Railway is your best bet for hassle-free n8n hosting! 🚀**