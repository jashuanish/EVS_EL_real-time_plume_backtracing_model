# Environmental Safety Platform

A production-grade, real-time environmental intelligence platform that assesses habitability risk using satellite, ground sensor, and meteorological data.

## ⚠️ Important: Real Data System

**This is a REAL production system using live data from public APIs:**
- OpenAQ (global ground sensors)
- Sentinel-5P TROPOMI (satellite air quality)
- ERA5 weather data (plume tracing)
- Government datasets (CPCB for India)

**NO mocked, random, or placeholder data** - All values come from real environmental monitoring sources.

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL with PostGIS (optional, for data storage)
- Redis (optional, for caching)
- Google Earth Engine account (for Sentinel-5P data)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Authenticate Google Earth Engine (if using satellite data)
earthengine authenticate

# Run backend
uvicorn main:app --reload
```

Backend API will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`

### Frontend Setup

```bash
# Install dependencies
npm install

# Set environment variable (create .env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── services/           # Data ingestion, ML pipeline, data fusion
│   ├── core/               # Configuration
│   └── main.py             # FastAPI app
├── app/                    # Next.js frontend
│   ├── page.tsx            # Main map page
│   └── analysis/           # Analysis page
├── components/             # React components
├── lib/                    # API client, utilities
└── ARCHITECTURE.md         # Detailed system architecture
```

---

## 🎯 Features

### Real-Time Environmental Assessment
- Air quality (PM2.5, NO₂, SO₂, O₃, CO)
- Water quality (turbidity, NDWI)
- Land monitoring (deforestation, NDVI)
- Gas plume detection and source tracing

### Multi-Source Data Fusion
- Combines satellite and ground sensor data
- Weighted confidence scoring
- Temporal alignment and interpolation

### ML-Powered Analysis
- Anomaly detection (Isolation Forest)
- Risk scoring (exposure + duration + uncertainty)
- Plume trajectory modeling (backward tracing)
- Time-series forecasting (LSTM/Prophet)

### User Experience
- Google Maps-style interactive map
- Human-readable explanations ("Explain Like I'm 15")
- Technical breakdown with full data provenance
- Real-time data timestamps and latency indicators

---

## 📊 API Endpoints

### `GET /api/v1/location/{lat}/{lng}`
Get environmental assessment for a location.

**Response includes:**
- Verdict (SAFE/MODERATE/UNSAFE)
- Risk score and confidence
- Air, water, land metrics
- Data sources and timestamps

### `GET /api/v1/analysis/{lat}/{lng}`
Get detailed analysis with human-readable and technical explanations.

**Response includes:**
- Human-readable summary and recommendations
- Technical breakdown with thresholds, sources, uncertainty
- Risk model details and feature importance

### `GET /api/v1/forecast/{lat}/{lng}?horizon_hours=48`
Get environmental forecast (requires historical data and trained models).

### `GET /api/v1/search?q=query`
Search for locations using geocoding.

---

## 🛰️ Data Sources

| Source | Type | Coverage | Update Frequency | Latency |
|--------|------|----------|------------------|---------|
| OpenAQ | Ground sensors | Global (3000+ stations) | Near real-time | < 1 hour |
| Sentinel-5P | Satellite | Global | Daily | ~24 hours |
| Sentinel-2 | Satellite | Global | ~5 days | ~5 days |
| ERA5 | Weather model | Global | Hourly | 1-5 days |
| CPCB | Ground sensors | India (300+ stations) | Hourly | < 1 hour |

**Special Support:** High-resolution data for India, particularly Karnataka (district/city level where available).

---

## 🔬 Technical Details

### Risk Scoring Model

```
Risk Score = 0.6 × Exposure + 0.3 × Duration + 0.1 × Uncertainty

Exposure: Based on threshold exceedances (WHO/CPCB guidelines)
Duration: Temporal persistence of high exposure
Uncertainty: Data quality, coverage, age penalty
```

### Data Fusion

Weighted averaging with confidence:
- Satellite: 40% weight
- Ground sensors: 50% weight
- Weather: 10% weight

Weights adjusted by data quality and spatial proximity.

### Plume Tracing

Backward Lagrangian trajectory model:
- Uses ERA5 wind vectors
- Traces pollution plumes backward 24-72 hours
- Identifies likely source regions with confidence ellipses

---

## ⚠️ Limitations & Ethical Considerations

See `ARCHITECTURE.md` for detailed limitations, including:
- Spatial resolution constraints
- Temporal resolution and latency
- Model uncertainty and error bounds
- Data quality and coverage gaps
- Ethical considerations (false positives/negatives)
- Regulatory compliance

**Important:** This platform provides evidence-based assessments, not legal conclusions or medical advice.

---

## 🏛️ Government / Smart City Deployment

The platform can be scaled for:
- Real-time city-wide dashboards
- Automated compliance reporting
- Emergency response integration
- Public health department APIs
- IoT sensor network integration

See `ARCHITECTURE.md` Section 9 for deployment model and infrastructure requirements.

---

## 📚 Documentation

- **ARCHITECTURE.md** - Comprehensive system architecture
- **backend/README.md** - Backend setup and API details
- **DEPLOYMENT.md** - Production deployment guide

---

## 🛠️ Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS, Leaflet
- **Backend:** FastAPI, Python 3.11+
- **ML:** PyTorch, scikit-learn, Isolation Forest, LSTM
- **Geospatial:** rasterio, geopandas, PostGIS
- **Data Sources:** Google Earth Engine, OpenAQ API, ERA5

---

## 📝 License

[Specify your license]

---

## 🙏 Attribution

- Data sources: OpenAQ, Copernicus Sentinel-5P/2, ECMWF ERA5, CPCB
- Standards: WHO Air Quality Guidelines 2021, CPCB AQI

---

**Built for environmental forensics, habitability assessment, and public health protection.**
