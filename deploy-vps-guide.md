# VPS Deployment Guide

## 1. Initial Server Setup

```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx
apt install -y nginx

# Install certbot for SSL
apt install -y certbot python3-certbot-nginx
```

## 2. Clone and Setup Application

```bash
# Clone your repo
cd /var/www
git clone https://github.com/peterdokim/news-summary-ai.git
cd news-summary-ai
git checkout vercel-deployment

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup Next.js
npm install
npm run build

# Create .env file
nano .env
# Add: OPENAI_API_KEY=your_key_here
```

## 3. Create Systemd Services

### Flask Backend Service

```bash
# Create service file
nano /etc/systemd/system/flask-backend.service
```

```ini
[Unit]
Description=Flask News Summarizer Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/news-summary-ai
Environment="PATH=/var/www/news-summary-ai/venv/bin"
EnvironmentFile=/var/www/news-summary-ai/.env
ExecStart=/var/www/news-summary-ai/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Next.js Frontend Service

```bash
nano /etc/systemd/system/nextjs-frontend.service
```

```ini
[Unit]
Description=Next.js News Summarizer Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/news-summary-ai
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
EnvironmentFile=/var/www/news-summary-ai/.env
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

### Enable and start services

```bash
systemctl daemon-reload
systemctl enable flask-backend nextjs-frontend
systemctl start flask-backend nextjs-frontend
systemctl status flask-backend nextjs-frontend
```

## 4. Configure Nginx

```bash
nano /etc/nginx/sites-available/news-summarizer
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Next.js frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Flask backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/news-summarizer /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## 5. Setup SSL Certificate

```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 6. Configure DNS

Point your domain to the VPS IP:

```
A Record:  @          →  your.server.ip
A Record:  www        →  your.server.ip
```

## 7. Firewall Setup

```bash
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
```

## 8. Deployment Updates

When you push changes:

```bash
cd /var/www/news-summary-ai
git pull origin vercel-deployment

# Update Python backend
source venv/bin/activate
pip install -r requirements.txt
systemctl restart flask-backend

# Update Next.js frontend
npm install
npm run build
systemctl restart nextjs-frontend
```

## 9. Monitoring

```bash
# Check logs
journalctl -u flask-backend -f
journalctl -u nextjs-frontend -f

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```
