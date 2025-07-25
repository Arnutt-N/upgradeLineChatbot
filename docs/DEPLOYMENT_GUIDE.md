# 🚀 Deployment Guide - Render.com

## 📋 Prerequisites

### 1. LINE Developer Account
- Go to [LINE Developers Console](https://developers.line.biz/)
- Create a Channel (Messaging API)
- Get your **Channel Secret** and **Channel Access Token**

### 2. Telegram Bot (Optional)
- Message @BotFather on Telegram
- Create a new bot and get the **Bot Token**
- Get your **Chat ID**

### 3. GitHub Repository
- Push your code to GitHub
- Make sure all files are committed

## 🔧 Render.com Deployment Steps

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your repository

### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select branch: `main` or `master`

### Step 3: Configure Service
```
Name: line-chatbot-admin
Environment: Python 3
Region: Oregon (or closest to you)
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker
```

### Step 4: Set Environment Variables
Go to **Environment** tab and add:

#### Required Variables:
```
ENVIRONMENT = production
HOST = 0.0.0.0
PORT = 10000
RELOAD = false
DEBUG = false

LINE_CHANNEL_SECRET = your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN = your_actual_access_token
```

#### Optional Variables:
```
TELEGRAM_BOT_TOKEN = your_telegram_bot_token
TELEGRAM_CHAT_ID = your_telegram_chat_id

NOTIFICATION_QUEUE_SIZE = 100
HISTORY_RETENTION_DAYS = 90
ANALYTICS_UPDATE_INTERVAL = 300
```

### Step 5: Configure Auto-Deploy
1. Enable **Auto-Deploy** from Git
2. Set **Health Check Path**: `/health`
3. Choose **Free Plan** (for demo)

### Step 6: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Check logs for any errors

## 🌐 Post-Deployment Configuration

### 1. Update LINE Webhook URL
1. Go to LINE Developers Console
2. Find your channel → **Messaging API**
3. Set **Webhook URL**: `https://your-app-name.onrender.com/webhook`
4. Enable **Use webhook**
5. Verify webhook

### 2. Test Your Application
Visit these URLs:
- `https://your-app-name.onrender.com/` - Service info
- `https://your-app-name.onrender.com/health` - Health check
- `https://your-app-name.onrender.com/admin` - Admin interface
- `https://your-app-name.onrender.com/ui/dashboard` - Enhanced dashboard
- `https://your-app-name.onrender.com/docs` - API documentation

### 3. Test LINE Integration
1. Add your LINE bot as friend
2. Send a message
3. Check logs in Render dashboard
4. Test admin live chat

## 🔧 Troubleshooting

### Common Issues:

#### 1. Build Fails
```bash
# Check requirements.txt
# Make sure all dependencies have version numbers
# Check Render build logs
```

#### 2. App Crashes on Start
```bash
# Check environment variables are set correctly
# Verify START_COMMAND is correct
# Check application logs
```

#### 3. Database Issues
```bash
# SQLite should work automatically
# Check if migration ran successfully
# Verify disk storage is mounted
```

#### 4. LINE Webhook Fails
```bash
# Verify webhook URL is correct
# Check LINE channel secret/token
# Test /webhook endpoint manually
```

## 📊 Monitoring

### Health Checks
- Render automatically monitors `/health` endpoint
- Set up email notifications in Render dashboard
- Monitor response times and uptime

### Logs
- View real-time logs in Render dashboard
- Check for errors and performance issues
- Monitor database queries

### Performance
- Free tier limitations: 512MB RAM, sleeps after 15min inactivity
- Consider paid tier for production use
- Monitor resource usage

## 🔄 Updates and Maintenance

### Automatic Deployment
- Push to main branch triggers auto-deploy
- Check deployment status in Render dashboard
- Rollback if needed

### Database Backup
- Download database regularly from Render dashboard
- Store backups securely
- Test restore procedures

### Environment Updates
- Update environment variables as needed
- Restart service after major changes
- Test thoroughly after updates

## 📋 Deployment Checklist

### Pre-Deployment:
- [ ] LINE Developer account setup
- [ ] Bot tokens obtained
- [ ] Code pushed to GitHub
- [ ] Environment variables documented

### During Deployment:
- [ ] Render service created
- [ ] Environment variables set
- [ ] Health check configured
- [ ] Auto-deploy enabled

### Post-Deployment:
- [ ] LINE webhook URL updated
- [ ] Application URLs tested
- [ ] LINE bot functionality verified
- [ ] Admin interface accessible
- [ ] Monitoring configured

## 🎯 Success Criteria

✅ **Deployment Successful When:**
- Health check returns 200 OK
- LINE webhook receives messages
- Admin interface loads correctly
- Enhanced dashboard displays data
- No critical errors in logs

## 📞 Support

If you encounter issues:
1. Check Render documentation
2. Review application logs
3. Test locally first
4. Check environment variable configuration
5. Verify LINE API configuration

---

**🎉 Your LINE Chatbot Admin System is now live on Render.com!**
