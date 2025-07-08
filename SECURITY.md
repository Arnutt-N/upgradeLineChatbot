# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this LINE Bot project, please report it responsibly:

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to the project maintainer with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- Initial response: Within 48 hours
- Status update: Within 7 days
- Fix timeline: Depends on severity (Critical: 1-3 days, High: 1 week, Medium: 2 weeks)

## Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use strong, unique secrets for production
- Rotate credentials regularly

### LINE Bot Security
- Validate webhook signatures
- Use HTTPS in production
- Implement rate limiting
- Log security events

### Database Security
- Use parameterized queries (SQLAlchemy ORM handles this)
- Regular backups
- Encrypt sensitive data
- Limit database access

### Deployment Security
- Use container scanning
- Keep dependencies updated
- Monitor for vulnerabilities
- Use secrets management

## Known Security Considerations

1. **Webhook Validation**: Always verify LINE webhook signatures
2. **Input Sanitization**: All user inputs are sanitized
3. **Rate Limiting**: Consider implementing rate limiting for production
4. **Database**: SQLite for development, PostgreSQL for production
5. **HTTPS**: Required for LINE webhook endpoints

## Security Checklist for Deployment

- [ ] Environment variables configured
- [ ] HTTPS enabled
- [ ] Webhook signature validation enabled
- [ ] Database secured
- [ ] Logs configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented

For more information, see our [Deployment Guide](README.md#deployment).
