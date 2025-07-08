# Deployment Security Checklist

## Pre-deployment Security Checks

### 🔍 1. Secret Scanning
```bash
# Run security scanner
python check_secrets.py

# Check git status
git status

# Ensure .env is not tracked
git ls-files | grep -E "\.(env|secret|key)$"
```

### 🔐 2. Environment Variables (Fly.io)
```bash
# Set required secrets
fly secrets set LINE_CHANNEL_SECRET="your_actual_secret"
fly secrets set LINE_CHANNEL_ACCESS_TOKEN="your_actual_token"
fly secrets set TELEGRAM_BOT_TOKEN="your_bot_token"
fly secrets set TELEGRAM_CHAT_ID="your_chat_id"
fly secrets set ENVIRONMENT="production"
fly secrets set DEBUG="false"

# Verify secrets are set
fly secrets list
```

### 🛡️ 3. Production Configuration
- [ ] HOST=0.0.0.0
- [ ] HTTPS enabled
- [ ] Webhook signature validation active
- [ ] Database path secured (/app/data/)
- [ ] Debug mode disabled
- [ ] Logs configured

### 🔒 4. Security Headers (Add to main.py if needed)
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add security middleware
if settings.is_production:
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.fly.dev"])
```

### 🚨 5. Final Checks
- [ ] No .env file in git
- [ ] No hardcoded secrets in code
- [ ] Database files ignored
- [ ] Backup files ignored
- [ ] Security scanner passes

## Post-deployment Verification

### ✅ 1. Test Endpoints
- [ ] https://your-app.fly.dev/health
- [ ] https://your-app.fly.dev/admin
- [ ] LINE webhook functionality

### ✅ 2. Monitor Logs
```bash
fly logs --app your-app-name
```

### ✅ 3. Security Monitoring
- [ ] Check for unusual traffic
- [ ] Monitor error logs
- [ ] Verify webhook signatures are validated

## Emergency Response

If secrets are compromised:
1. Immediately rotate all credentials
2. Update environment variables
3. Redeploy application
4. Monitor for unauthorized access
5. Review access logs

## Contact

For security issues, please refer to SECURITY.md
