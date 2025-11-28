# 🚀 Quick Deploy to Railway

## Prerequisites
- GitHub account
- Railway account (free signup)

## 🔥 One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/yourusername/n8n-odoo-automation)

## Manual Deployment Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial n8n setup"
git branch -M main
git remote add origin https://github.com/yourusername/n8n-odoo-automation.git
git push -u origin main
```

### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect the Dockerfile and deploy

### 3. Configure Environment Variables
In Railway dashboard, add these variables:

**Required:**
- `N8N_BASIC_AUTH_USER`: `admin` (or your preferred username)
- `N8N_BASIC_AUTH_PASSWORD`: `your-secure-password`
- `N8N_ENCRYPTION_KEY`: Generate a 32-character secure key

**Optional:**
- `WEBHOOK_URL`: Your Railway app URL (get this after deployment)
- `N8N_HOST`: Your Railway domain
- `SMTP_HOST`: For email notifications
- `SMTP_PORT`: For email notifications
- `SMTP_USER`: For email notifications
- `SMTP_PASS`: For email notifications

### 4. Generate Secure Keys
Use this command to generate secure keys:

```bash
# Generate 32-character encryption key
openssl rand -hex 16

# Or use Node.js
node -e "console.log(require('crypto').randomBytes(16).toString('hex'))"

# Or use Python
python -c "import secrets; print(secrets.token_hex(16))"
```

### 5. Access Your n8n Instance
1. Railway will provide a URL like: `https://n8n-production-xxxx.up.railway.app`
2. Open the URL in your browser
3. Login with your configured username/password
4. Import your workflow: `n8n_bill_automation_workflow.json`

## 🔧 Configuration

### Import Your Bill Automation Workflow
1. In n8n, go to **Workflows** > **Import from File**
2. Upload `n8n_bill_automation_workflow.json`
3. Configure these credentials:
   - **Google Drive OAuth2** (for file access)
   - **OpenAI API** (for OCR processing)
   - **SMTP** (for notifications)
   - **HTTP** (for Odoo webhook)

### Set Up Google Drive Integration
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google Drive API
4. Create OAuth2 credentials
5. Add your Railway URL to authorized redirect URIs
6. Configure in n8n credentials

### Set Up OpenAI Integration
1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to n8n credentials
3. Ensure you have GPT-4 Vision access

## 📊 Monitoring

### Railway Dashboard
- View logs in real-time
- Monitor resource usage
- Set up custom domains
- Configure auto-deploy from GitHub

### n8n Monitoring
- Access execution logs in n8n interface
- Set up error notifications
- Monitor workflow performance

## 🔒 Security Best Practices

### 1. Strong Authentication
```bash
N8N_BASIC_AUTH_USER=your-admin-username
N8N_BASIC_AUTH_PASSWORD=use-a-very-strong-password-here
```

### 2. Secure Encryption
```bash
N8N_ENCRYPTION_KEY=generate-32-character-secure-key-here
```

### 3. HTTPS Only
```bash
N8N_PROTOCOL=https
N8N_SECURE_COOKIE=true
```

### 4. Environment Security
```bash
N8N_BLOCK_ENV_ACCESS_IN_NODE=true
N8N_GIT_NODE_DISABLE_BARE_REPOS=true
```

## 💡 Pro Tips

### Cost Optimization
- Railway free tier: $5/month credit
- n8n typically uses ~$2-3/month
- Monitor usage in Railway dashboard
- Consider upgrading for production workloads

### Performance
- Railway provides 512MB RAM by default
- Upgrade to 1GB+ for heavy workflows
- Use PostgreSQL for better performance (available on paid tiers)

### Backup Strategy
1. **Export workflows regularly**:
   ```bash
   # In n8n interface: Settings > Import/Export > Export All
   ```
2. **Version control your configurations**
3. **Railway provides automatic backups**

### Custom Domain
1. In Railway dashboard: Settings > Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `WEBHOOK_URL` environment variable

## 🚨 Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check Railway logs for errors
# Verify all environment variables are set
# Ensure Dockerfile is properly configured
```

**Authentication fails:**
```bash
# Verify N8N_BASIC_AUTH_USER and PASSWORD are set
# Check if variables contain special characters
# Try logging in with exact credentials
```

**Workflows not executing:**
```bash
# Check webhook URL configuration
# Verify credentials are properly set
# Test API connections manually
```

**Database issues:**
```bash
# SQLite database should auto-create
# Check file permissions in logs
# Consider upgrading to PostgreSQL
```

### Getting Help
- Railway Discord: [railway.app/discord](https://railway.app/discord)
- n8n Community: [community.n8n.io](https://community.n8n.io)
- GitHub Issues: Create issues in your repository

## 📈 Scaling

### When to Upgrade
- Workflows taking longer to execute
- Memory usage consistently high
- Need for high availability
- Multiple team members

### Upgrade Options
1. **Railway Pro**: More resources, PostgreSQL, teams
2. **Dedicated VPS**: Full control, custom configurations
3. **n8n Cloud**: Official managed service

---

🎉 **You're ready to deploy! Railway makes it super easy to host n8n for free.**

**Estimated deployment time: 5-10 minutes** ⚡