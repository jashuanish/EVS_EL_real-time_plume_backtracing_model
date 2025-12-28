# Environmental Safety Platform - Backend API

Production-grade FastAPI backend for real-time environmental intelligence and habitability risk assessment.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/environmental_db
REDIS_URL=redis://localhost:6379/0

# Optional API Keys
OPENAQ_API_KEY=your_openaq_key_here
MAPBOX_TOKEN=your_mapbox_token_here

# Google Earth Engine (requires authentication)
# Run: earthengine authenticate
```

### 3. Google Earth Engine Setup (for Sentinel-5P data)

```bash
# Install Earth Engine CLI (if not already installed)
pip install earthengine-api

# Authenticate (opens browser)
earthengine authenticate

# Initialize (run once)
python -c "import ee; ee.Initialize()"
```

### 4. Run the Server

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py entry point
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### GET `/api/v1/location/{lat}/{lng}`
Get environmental assessment for a location.

**Example:**
```bash
curl http://localhost:8000/api/v1/location/12.9716/77.5946
```

### GET `/api/v1/analysis/{lat}/{lng}`
Get detailed analysis with human-readable and technical explanations.

**Example:**
```bash
curl http://localhost:8000/api/v1/analysis/12.9716/77.5946
```

### GET `/api/v1/forecast/{lat}/{lng}?horizon_hours=48`
Get environmental forecast.

**Example:**
```bash
curl http://localhost:8000/api/v1/forecast/12.9716/77.5946?horizon_hours=48
```

### GET `/api/v1/search?q=query`
Search for locations using geocoding.

**Example:**
```bash
curl "http://localhost:8000/api/v1/search?q=Bangalore"
```

## Data Sources

The backend integrates with:

1. **OpenAQ** - Global ground sensor network (no API key required)
2. **Sentinel-5P (TROPOMI)** - Satellite air quality data (via Google Earth Engine)
3. **Sentinel-2** - Water quality and land monitoring (future)
4. **ERA5** - Weather data for plume tracing (future)
5. **CPCB** - India-specific air quality (placeholder)

## Architecture

See `ARCHITECTURE.md` in the root directory for detailed system design.

## Development Notes

- All data is real-time or near-real-time from public APIs
- ML models are implemented but may require training data
- Forecasting models are placeholders - need historical data and training
- Earth Engine integration requires authentication

