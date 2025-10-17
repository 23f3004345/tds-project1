# Deployment Guide

## Cloud Deployment Options

### Option 1: Deploy on Railway

1. **Create Railway Account**: https://railway.app

2. **Deploy Student API**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   railway init
   
   # Add environment variables
   railway variables set GITHUB_TOKEN=your_token
   railway variables set OPENAI_API_KEY=your_key
   railway variables set STUDENT_SECRET=your_secret
   
   # Deploy
   railway up
   ```

3. **Get your public URL** from Railway dashboard

### Option 2: Deploy on Render

1. **Create account**: https://render.com

2. **New Web Service**:
   - Connect your GitHub repo
   - Build command: `pip install -r requirements.txt && playwright install chromium`
   - Start command: `python student_api.py`

3. **Add Environment Variables** in Render dashboard

### Option 3: Deploy on Heroku

1. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

2. **Add Procfile**:
   ```
   web: python student_api.py
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 4: Deploy on Your Own Server

Using systemd on Linux:

1. **Create service file** `/etc/systemd/system/student-api.service`:
   ```ini
   [Unit]
   Description=Student API Service
   After=network.target

   [Service]
   Type=simple
   User=youruser
   WorkingDirectory=/path/to/project
   Environment="PATH=/path/to/project/venv/bin"
   ExecStart=/path/to/project/venv/bin/python student_api.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start**:
   ```bash
   sudo systemctl enable student-api
   sudo systemctl start student-api
   ```

## Database Setup for Production

### PostgreSQL (Recommended)

1. **Install PostgreSQL** or use a hosted service (ElephantSQL, Supabase, etc.)

2. **Update .env**:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

3. **Initialize**:
   ```bash
   python init_db.py
   ```

## Security Considerations

1. **Never commit .env file** - It's in .gitignore
2. **Use strong secrets** - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **Rotate GitHub tokens** regularly
4. **Use HTTPS** in production
5. **Rate limit** your API endpoints
6. **Monitor costs** for LLM API usage

## Monitoring

Add logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
```

## Scaling

For high volume:
- Use Redis for caching
- Add task queue (Celery/RQ) for async processing
- Use CDN for GitHub Pages
- Implement connection pooling for database

