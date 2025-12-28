# Deployment Guide

## Production Deployment Checklist

### Backend Setup

1. **Environment Variables**
   ```env
   DEBUG=False
   DATABASE_URL=postgresql://user:password@host:5432/environmental_db
   REDIS_URL=redis://host:6379/0
   OPENAQ_API_KEY=your_key (optional)
   MAPBOX_TOKEN=your_token (optional)
   ```

2. **Database Setup**
   ```bash
   # Install PostGIS extension
   psql -d environmental_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```

3. **Google Earth Engine Authentication**
   ```bash
   earthengine authenticate
   python -c "import ee; ee.Initialize()"
   ```

4. **Run Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Environment Variables**
   ```env
   NEXT_PUBLIC_API_URL=http://your-backend-url:8000/api/v1
   ```

2. **Build & Run**
   ```bash
   npm install
   npm run build
   npm start
   ```

### Docker Deployment (Optional)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Limitations & Notes

- Earth Engine requires authentication (cannot run in pure container without credentials)
- Some data sources may have rate limits
- Real-time data may have latency (see ARCHITECTURE.md)
- ML models require training data for forecasting

