# Environmental Safety Platform - Production Architecture

## System Overview

A real-time environmental intelligence platform that fuses satellite, ground sensor, and meteorological data to assess habitability risk at any global location with special high-resolution support for India (particularly Karnataka).

---

## 1. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (React/Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Map View   │  │ Analysis UI  │  │  Search UI   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTPS / WebSocket
┌────────────────────▼─────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Location    │  │   Analysis   │  │   Forecast   │          │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                 DATA FUSION ENGINE (Python)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Satellite   │  │   Ground     │  │  Weather     │          │
│  │  Processor   │  │   Sensors    │  │  Fusion      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│              ML PIPELINE (PyTorch / scikit-learn)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Anomaly    │  │    Plume     │  │    Risk      │          │
│  │  Detection   │  │   Tracing    │  │   Scoring    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐                                               │
│  │  Forecasting │                                               │
│  │   (LSTM/     │                                               │
│  │   Prophet)   │                                               │
│  └──────────────┘                                               │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│              DATA INGESTION LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Sentinel-5P  │  │    OpenAQ    │  │    CPCB      │          │
│  │  (TROPOMI)   │  │              │  │  (India)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Sentinel-2   │  │     ERA5     │  │    GRDC      │          │
│  │              │  │  (Weather)   │  │  (Rivers)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│              DATA STORAGE                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   PostGIS    │  │  Time-Series │  │  Cache       │          │
│  │  (Geospatial)│  │    DB        │  │  (Redis)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. DATA INGESTION PIPELINE

### 2.1 Satellite Data Sources

#### Sentinel-5P (TROPOMI) - Air Quality
- **Source**: Copernicus Open Access Hub / Google Earth Engine
- **Variables**: NO₂, SO₂, CO, CH₄, Aerosol Index, O₃
- **Spatial Resolution**: 3.5×7 km² (NO₂), 7×7 km² (others)
- **Temporal Resolution**: Daily (with ~24h latency)
- **API**: Google Earth Engine Python API (preferred) or Copernicus OData API
- **Coverage**: Global

#### Sentinel-2 - Water & Land
- **Source**: Copernicus Open Access Hub / Google Earth Engine
- **Variables**: NDWI (water), NDVI (vegetation), turbidity indices
- **Spatial Resolution**: 10-20m
- **Temporal Resolution**: ~5 days
- **Coverage**: Global

#### Landsat 8/9 - Deforestation
- **Source**: USGS EarthExplorer / Google Earth Engine
- **Variables**: NDVI, EVI, land cover change
- **Spatial Resolution**: 30m
- **Temporal Resolution**: ~16 days
- **Coverage**: Global

### 2.2 Ground Sensor Networks

#### OpenAQ (Global)
- **API**: https://api.openaq.org/v2/
- **Variables**: PM2.5, PM10, NO₂, SO₂, O₃, CO
- **Update Frequency**: Near real-time (varies by station)
- **Coverage**: Global (3000+ stations)

#### CPCB (India)
- **API**: https://app.cpcbccr.com/ccr/#/caaqm-dashboard-all/caaqm-landing
- **Variables**: AQI, PM2.5, PM10, NO₂, SO₂, CO, O₃
- **Update Frequency**: Hourly
- **Coverage**: 300+ stations across India
- **Special Support**: District-level data for Karnataka

### 2.3 Meteorological Data

#### ERA5 (ECMWF)
- **Source**: CDS API or AWS S3
- **Variables**: Wind (u/v components), temperature, pressure, humidity
- **Spatial Resolution**: 0.25° (~31km)
- **Temporal Resolution**: Hourly
- **Latency**: ~5 days for final, 1 day for near-real-time
- **Critical for**: Plume trajectory modeling

#### IMD (India Meteorological Department)
- **Source**: IMD API (if available) or web scraping with attribution
- **Variables**: Regional wind, rainfall, temperature
- **Coverage**: India-specific

### 2.4 Water Quality Data

#### GRDC (Global Runoff Data Centre)
- **Source**: GRDC web portal / API
- **Variables**: River discharge
- **Coverage**: Major rivers globally

#### Sentinel-2 Derived
- **Turbidity**: From red/blue band ratios
- **Chlorophyll-a**: From blue/green ratios
- **Coverage**: Surface water bodies globally

---

## 3. DATA PROCESSING PIPELINE

### 3.1 Data Ingestion Flow

```
External API → Raw Data Fetch → Validation → Geospatial Reprojection 
→ Temporal Alignment → Quality Flags → Storage (PostGIS/Time-Series DB)
```

### 3.2 Geospatial Processing

**Tools**: `rasterio`, `geopandas`, `xarray`

1. **Reprojection**: All data → WGS84 / Web Mercator
2. **Resampling**: Different resolutions → Common grid (e.g., 1km for fusion)
3. **Spatial Aggregation**: Satellite pixels → Location-centric summaries
4. **Temporal Interpolation**: Fill gaps using linear/spline interpolation

### 3.3 Data Fusion Strategy

**Multi-source fusion** using weighted averaging with confidence:

```
Final Value = Σ (Source_i × Weight_i × Confidence_i) / Σ (Weight_i × Confidence_i)
```

**Weights**:
- Satellite: 0.4 (spatial coverage, but lower temporal resolution)
- Ground sensors: 0.5 (accuracy, but limited spatial coverage)
- Weather model: 0.1 (contextual, not direct measurement)

**Confidence**:
- Based on data age, sensor quality, spatial distance from target

---

## 4. ML PIPELINE

### 4.1 Anomaly Detection

**Method**: Isolation Forest + Local Outlier Factor (LOF)

**Features**:
- Pollution levels vs historical baseline (30-day rolling window)
- Spatial neighbors comparison
- Temporal patterns (hourly, daily, seasonal)

**Output**:
- Anomaly score (0-1)
- Contribution of each feature

### 4.2 Plume Tracing (Backward Trajectory)

**Method**: Lagrangian particle dispersion model (simplified)

**Algorithm**:
1. Start at detection point (high SO₂/NO₂)
2. Use ERA5 wind vectors (u, v components)
3. Trace backward in time (24-72 hours)
4. Identify likely source regions
5. Calculate source probability cone

**Output**:
- Source coordinates (lat/lng)
- Confidence region (ellipse)
- Probable source type (industrial, urban, natural)

### 4.3 Risk Scoring Model

**Multi-factor Risk Score**:

```
Risk = f(Exposure, Duration, Sensitivity, Uncertainty)

Components:
1. Exposure Score (0-100):
   - Air: Max(PM2.5/WHO_limit, NO₂/WHO_limit, SO₂/WHO_limit) × 100
   - Water: (1 - Quality_Score/100) × 100
   - Land: Deforestation_Risk
   
2. Duration Score:
   - Temporal persistence of high exposure
   - Recent trend (improving vs worsening)
   
3. Population Sensitivity:
   - Age distribution (elderly, children)
   - Pre-existing conditions (if available)
   
4. Uncertainty Penalty:
   - Reduces confidence for sparse data
   - Increases risk conservatively
```

**Final Risk Categories**:
- **SAFE** (0-33): Below thresholds, low confidence uncertainty
- **MODERATE** (34-66): Near thresholds or high uncertainty
- **UNSAFE** (67-100): Exceeds thresholds consistently

**Confidence** (0-100%):
- Based on data quality, coverage, temporal consistency

### 4.4 Time-Series Forecasting

#### Short-term (Hours to Days)
**Method**: LSTM (Long Short-Term Memory) neural network

**Features**:
- Historical pollution levels (last 30 days)
- Weather forecasts (wind, temperature, pressure)
- Day-of-week, hour-of-day (temporal patterns)

**Output**:
- Point forecast
- Uncertainty bounds (using dropout-based Monte Carlo)

#### Long-term (Weeks to Months)
**Method**: Prophet (Facebook) or ARIMA + seasonal decomposition

**Features**:
- Multi-year historical trends
- Seasonal patterns
- Known events (fire seasons, monsoon, etc.)

**Output**:
- Trend forecast
- Seasonal components
- Prediction intervals

---

## 5. API DESIGN

### 5.1 Endpoints

#### GET `/api/v1/location/{lat}/{lng}`
Returns current environmental assessment for a location.

**Response**:
```json
{
  "location": {
    "lat": 12.9716,
    "lng": 77.5946,
    "name": "Bangalore, Karnataka, India"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "data_timestamp": {
    "air_quality": "2024-01-15T09:00:00Z",
    "water_quality": "2024-01-14T12:00:00Z",
    "land": "2024-01-13T00:00:00Z",
    "meteorology": "2024-01-15T10:00:00Z"
  },
  "verdict": {
    "level": "UNSAFE",
    "confidence": 87.5,
    "risk_score": 72.3
  },
  "metrics": {
    "air": {
      "pm25": {"value": 85.2, "unit": "μg/m³", "threshold": 15, "source": "CPCB"},
      "no2": {"value": 48.3, "unit": "μg/m³", "threshold": 25, "source": "Sentinel-5P"},
      "so2": {"value": 12.1, "unit": "μg/m³", "threshold": 40, "source": "Sentinel-5P"}
    },
    "water": {
      "turbidity": {"value": 8.5, "unit": "NTU", "threshold": 5.0, "source": "Sentinel-2"},
      "quality_score": 65.0
    },
    "land": {
      "deforestation_risk": 35.0,
      "trend": "worsening"
    }
  },
  "plumes": [
    {
      "detected": true,
      "pollutant": "SO2",
      "intensity": 45.2,
      "source_estimate": {
        "lat": 12.9850,
        "lng": 77.6200,
        "confidence_radius_km": 5.2,
        "probable_type": "industrial"
      }
    }
  ],
  "sources": {
    "satellite": "Sentinel-5P L2 product",
    "ground_sensors": ["CPCB_STATION_123", "OpenAQ_456"],
    "weather": "ERA5 reanalysis"
  }
}
```

#### GET `/api/v1/analysis/{lat}/{lng}`
Detailed analysis with human-readable and technical explanations.

**Response**:
```json
{
  "human_readable": {
    "summary": "This location is UNSAFE to inhabit.",
    "reasons": [
      "PM2.5 levels (85.2 μg/m³) exceed WHO annual limit (15 μg/m³) by 5.7×",
      "NO₂ levels (48.3 μg/m³) exceed WHO guideline (25 μg/m³) by 1.9×",
      "Upwind SO₂ plume detected from industrial cluster 5km northeast",
      "Water turbidity (8.5 NTU) exceeds safe limit (5.0 NTU) by 70%"
    ],
    "recommendations": [
      "Avoid outdoor activities, especially during peak hours",
      "Use air purifiers indoors",
      "Monitor water before consumption"
    ]
  },
  "technical": {
    "air_quality": {
      "pm25": {
        "raw_value": 85.2,
        "unit": "μg/m³",
        "threshold": {"source": "WHO", "value": 15, "standard": "WHO AQG 2021"},
        "exceedance_factor": 5.68,
        "data_source": "CPCB Station KA-BLR-001",
        "sensor_id": "CPCB_STATION_123",
        "measurement_timestamp": "2024-01-15T09:00:00Z",
        "quality_flag": "validated",
        "spatial_coverage": "point",
        "uncertainty": {"type": "95% CI", "lower": 80.1, "upper": 90.3}
      },
      "no2": {
        "raw_value": 48.3,
        "unit": "μg/m³",
        "threshold": {"source": "WHO", "value": 25, "standard": "WHO AQG 2021"},
        "exceedance_factor": 1.93,
        "data_source": "Sentinel-5P TROPOMI L2",
        "product_id": "S5P_OFFL_L2__NO2____20240115T093045",
        "measurement_timestamp": "2024-01-15T09:30:45Z",
        "spatial_resolution_km": 3.5,
        "processing_level": "L2",
        "uncertainty": {"type": "standard_error", "value": 2.1}
      }
    },
    "plume_analysis": {
      "detection_timestamp": "2024-01-15T09:30:00Z",
      "pollutant": "SO2",
      "trajectory_model": "Lagrangian backward",
      "wind_source": "ERA5 hourly",
      "source_estimate": {
        "coordinates": [12.9850, 77.6200],
        "confidence_ellipse": {
          "semi_major_km": 5.2,
          "semi_minor_km": 3.1,
          "angle_deg": 45.0
        },
        "temporal_range_hours": [12, 48],
        "probability": 0.78
      },
      "source_type_classification": {
        "industrial": 0.85,
        "urban": 0.10,
        "natural": 0.05
      }
    },
    "risk_model": {
      "exposure_score": 72.3,
      "duration_score": 65.0,
      "sensitivity_score": 50.0,
      "uncertainty_penalty": 5.0,
      "final_risk_score": 72.3,
      "model_version": "v1.2.0",
      "feature_importance": {
        "pm25": 0.35,
        "no2": 0.25,
        "plume_detection": 0.20,
        "temporal_trend": 0.15,
        "water_quality": 0.05
      }
    }
  }
}
```

#### GET `/api/v1/forecast/{lat}/{lng}`
Time-series forecast for location.

**Response**:
```json
{
  "location": [12.9716, 77.5946],
  "forecast_type": "short_term",
  "horizon_hours": 48,
  "generated_at": "2024-01-15T10:30:00Z",
  "predictions": [
    {
      "timestamp": "2024-01-15T11:00:00Z",
      "pm25": {"mean": 82.1, "lower": 75.3, "upper": 89.0, "confidence": 0.90},
      "no2": {"mean": 46.8, "lower": 42.1, "upper": 51.5, "confidence": 0.88}
    }
  ],
  "model_info": {
    "type": "LSTM",
    "training_data_range": "2023-01-01 to 2024-01-14",
    "rmse": 5.2,
    "mae": 3.8
  }
}
```

#### GET `/api/v1/search?q={query}`
Geocoding search (using Nominatim or Google Geocoding API).

---

## 6. FRONTEND UI FLOW

### 6.1 Home Page

1. **Initialization**:
   - Request geolocation permission
   - If granted → center map on user location
   - If denied → center on default (Bangalore/Karnataka)

2. **Map Rendering**:
   - Use Mapbox GL JS or Leaflet with custom tile layers
   - Render pollution heatmaps as overlays
   - Show real-time sensor markers (OpenAQ, CPCB)

3. **Layer Toggles**:
   - Air Pollution (NO₂, SO₂, PM2.5 heatmaps)
   - Water Quality (turbidity, NDWI)
   - Land (deforestation, NDVI change)
   - Gas Plumes (animated overlay)

4. **Time Slider**:
   - Past: Historical data (last 30 days)
   - Present: Latest available
   - Future: Forecast (if available)

5. **Click Interaction**:
   - On map click → Fetch `/api/v1/location/{lat}/{lng}`
   - Display verdict badge in right panel
   - Show "View Detailed Analysis" button

### 6.2 Analysis Page

**Two-Mode Toggle**:
- Human-Readable Mode (default)
- Technical Mode

**Content**:
- Verdict with confidence
- Reasons (bullets in human mode, tables in technical mode)
- Data provenance (every claim linked to source)
- Timestamps (with latency indicators)
- Charts (time series, threshold crossings)
- Plume visualization (if detected)

---

## 7. ERROR HANDLING & LATENCY

### 7.1 Data Unavailability

**Scenarios**:
1. **No satellite data** (clouds, sensor downtime)
   - Fallback to ground sensors only
   - Reduce confidence score
   - Show "Limited data available" warning

2. **No ground sensors nearby** (>50km)
   - Use satellite-only
   - Higher uncertainty bounds
   - Explicit message: "No nearby ground sensors"

3. **Stale data** (>7 days old)
   - Show "Last updated: X days ago"
   - Disable real-time features
   - Recommend checking back later

### 7.2 API Failures

- **Retry logic**: Exponential backoff (3 attempts)
- **Graceful degradation**: Use cached data if fresh (<24h old)
- **User feedback**: "Some data sources temporarily unavailable"

### 7.3 Latency Indicators

Every data point shows:
- **Last updated timestamp**
- **Age** (e.g., "2 hours ago", "5 days ago")
- **Color coding**: Green (<1 day), Yellow (1-7 days), Red (>7 days)

---

## 8. LIMITATIONS & ETHICAL NOTES

### 8.1 Technical Limitations

1. **Spatial Resolution**: Satellite data limited to 3.5-30km grids
   - Cannot detect hyperlocal pollution (street-level)
   - Micro-environments may vary significantly

2. **Temporal Resolution**: Daily satellite passes, hourly sensors
   - Short-term spikes may be missed
   - Forecasting uncertainty increases with horizon

3. **Data Quality**: 
   - Satellite retrievals fail in cloudy conditions
   - Ground sensors may have calibration drift
   - Cross-validation required but not always possible

4. **Model Uncertainty**:
   - Risk scores are estimates, not certainties
   - Plume tracing has inherent uncertainty (wind model errors)
   - Forecasting accuracy degrades over time

5. **Coverage Gaps**:
   - Rural areas may lack ground sensors
   - Some regions have sparse satellite coverage
   - Water quality data limited to surface water

### 8.2 Ethical Considerations

1. **False Negatives**: Classifying unsafe areas as safe → harm to users
   - **Mitigation**: Conservative risk scoring (err on side of caution)
   - Clear confidence intervals

2. **False Positives**: Over-alerting → unnecessary anxiety, property value impacts
   - **Mitigation**: Show uncertainty, provide context
   - Encourage verification with local authorities

3. **Data Privacy**: User location tracking
   - **Policy**: No server-side location logging (only for API requests)
   - Client-side geolocation opt-in only

4. **Attribution & Responsibility**:
   - Cannot attribute pollution to specific companies without additional investigation
   - Platform provides evidence, not legal conclusions

5. **Accessibility**:
   - Ensure data is accessible to non-technical users (human-readable mode)
   - Provide multiple languages (future enhancement)

### 8.3 Regulatory Compliance

1. **Data Usage**: Respect API terms of service (Sentinel, OpenAQ, CPCB)
2. **Attribution**: Credit all data sources
3. **No Medical Claims**: Platform is informational, not medical advice
4. **Disclaimers**: Clearly state limitations and uncertainties

---

## 9. SCALABILITY TO GOVERNMENT / SMART CITIES

### 9.1 Enhanced Features for Government Deployment

1. **Real-time Dashboards**:
   - City-wide pollution monitoring
   - Alert system for threshold breaches
   - Historical compliance tracking

2. **API for Integration**:
   - Smart city platforms (IoT sensor networks)
   - Emergency response systems
   - Public health departments

3. **Reporting & Analytics**:
   - Automated compliance reports
   - Trend analysis (monthly/quarterly)
   - Source attribution for enforcement

4. **High-Resolution Data**:
   - Integration with city-specific sensor networks
   - Drone/UAV data integration
   - Traffic flow data (for emissions modeling)

### 9.2 Infrastructure Requirements

- **Backend**: Horizontal scaling (Kubernetes)
- **Database**: PostGIS cluster, time-series DB (TimescaleDB)
- **Caching**: Redis for frequent queries
- **Compute**: ML inference on GPU clusters (for real-time forecasting)
- **Storage**: Object storage (S3/GCS) for historical satellite data

### 9.3 Deployment Model

- **Cloud-native**: AWS/GCP/Azure
- **Containerized**: Docker containers
- **CI/CD**: Automated testing and deployment
- **Monitoring**: Prometheus + Grafana for system health
- **Alerting**: PagerDuty for critical failures

---

## 10. TECH STACK JUSTIFICATION

### Frontend: Next.js + React + Mapbox GL JS

**Why**:
- Next.js: SSR for fast initial load, SEO-friendly
- React: Component-based, large ecosystem
- Mapbox GL JS: High-performance WebGL rendering, custom styling, 3D support

**Alternatives considered**: Leaflet (simpler, but less performant for large datasets)

### Backend: FastAPI (Python)

**Why**:
- Fast: ASGI server, async support
- Type hints: Better code quality, IDE support
- Auto documentation: OpenAPI/Swagger
- Python ecosystem: Easy integration with ML libraries

### ML: PyTorch + scikit-learn

**Why**:
- PyTorch: LSTM/neural networks for forecasting
- scikit-learn: Anomaly detection (Isolation Forest), preprocessing
- xarray: Multi-dimensional arrays (satellite data)
- geopandas: Geospatial data manipulation

### Geospatial: rasterio + geopandas + PostGIS

**Why**:
- rasterio: Efficient satellite raster processing
- geopandas: Vector data (points, polygons)
- PostGIS: Spatial queries, indexing (faster than MongoDB/MySQL)

### Storage: PostGIS + TimescaleDB + Redis

**Why**:
- PostGIS: Geospatial data storage and queries
- TimescaleDB: Time-series optimization (hypertables)
- Redis: Caching, session management

---

## NEXT STEPS: IMPLEMENTATION

This document serves as the blueprint. Implementation will proceed in phases:

1. **Phase 1**: Backend API structure + data ingestion (OpenAQ, Sentinel via Earth Engine)
2. **Phase 2**: ML pipeline (anomaly detection, risk scoring)
3. **Phase 3**: Frontend integration with real data
4. **Phase 4**: Plume tracing + forecasting
5. **Phase 5**: Production hardening (error handling, caching, scaling)

