# 🥭 Mango Detection - Docker Deployment Guide

## 📋 Prerequisites

- Docker Desktop installed
- Docker Compose installed
- Git installed

## 🚀 Quick Start (Local Development)

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Using Docker Commands

**Backend:**
```bash
cd Backend
docker build -t mango-detection-backend .
docker run -d -p 8000:8000 --name mango-api mango-detection-backend
```

**Frontend:**
```bash
cd project/frontend
docker build -t mango-detection-frontend .
docker run -d -p 3000:80 --name mango-frontend mango-detection-frontend
```

## 🌐 Deploy to Production

### Option A: Render.com (Free Tier)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Docker configuration"
   git push origin main
   ```

2. **Deploy Backend:**
   - Go to [render.com](https://render.com) and sign up
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Configure:
     - **Name:** `mango-detection-api`
     - **Root Directory:** `Backend`
     - **Runtime:** `Docker`
     - **Instance Type:** `Free`
   - Click **"Create Web Service"**

3. **Update Frontend API URL:**
   - Update `.env` with your Render backend URL:
     ```
     VITE_API_URL=https://mango-detection-api.onrender.com
     ```

4. **Deploy Frontend to GitHub Pages:**
   ```bash
   cd project/frontend
   npm run build
   npm run deploy
   ```

### Option B: Railway.app

1. **Sign up at [railway.app](https://railway.app)**

2. **Deploy Backend:**
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Select `MangoDetector` repository
   - Add **"New Service"** → Select `Backend` folder
   - Railway auto-detects Dockerfile
   - Your API URL: `https://your-project.up.railway.app`

3. **Deploy Frontend:**
   - Add another service for `project/frontend`
   - Railway builds and deploys automatically

### Option C: Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name mango-detection-rg --location eastus

# Create container registry
az acr create --resource-group mango-detection-rg --name mangodetectionacr --sku Basic

# Build and push backend
az acr build --registry mangodetectionacr --image mango-backend:latest ./Backend

# Deploy container
az container create \
  --resource-group mango-detection-rg \
  --name mango-api \
  --image mangodetectionacr.azurecr.io/mango-backend:latest \
  --cpu 2 \
  --memory 4 \
  --dns-name-label mango-detection-api \
  --ports 8000
```

## 🛠️ Useful Docker Commands

```bash
# View running containers
docker ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build

# Remove all containers and images
docker-compose down --rmi all

# Access backend container shell
docker exec -it mango-detection-api bash

# Clean up unused resources
docker system prune -a
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### View Container Stats
```bash
docker stats
```

## 🔧 Troubleshooting

### Issue: Port already in use
```bash
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Change first number
```

### Issue: Container fails to start
```bash
# View detailed logs
docker logs mango-detection-api

# Check container status
docker ps -a
```

### Issue: Model file not found
```bash
# Ensure models are in Backend/models/ directory
# Check volume mapping in docker-compose.yml
```

## 📦 Project Structure

```
project/
├── Backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── app.py
│   └── models/
│       ├── best.pt
│       └── last.pt
├── project/frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── nginx.conf
│   ├── .env
│   └── package.json
├── docker-compose.yml
└── render.yaml
```

## 🌟 Production Tips

1. **Use environment variables** for configuration
2. **Enable HTTPS** in production
3. **Set up monitoring** and logging
4. **Use Docker secrets** for sensitive data
5. **Implement rate limiting** for API endpoints
6. **Add CORS policies** for production domains

## 📝 License

MIT License

## 👤 Author

LaVireak - [GitHub](https://github.com/LaVireak)

---

**Live Demo:** Coming soon!
