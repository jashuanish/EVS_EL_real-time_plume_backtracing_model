"""
Location API endpoints
Returns environmental assessment for a given location
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime
from api.schemas import LocationResponse, SafetyLevel
from services.data_ingestion import DataIngestionService
from services.ml_pipeline import RiskScorer, AnomalyDetector
from services.data_fusion import DataFusionService
try:
    import reverse_geocoder as rg
except ImportError:
    rg = None

router = APIRouter()

# Initialize services
data_ingestion = DataIngestionService()
risk_scorer = RiskScorer()
anomaly_detector = AnomalyDetector()
data_fusion = DataFusionService()

@router.get("/location/{lat}/{lng}", response_model=LocationResponse)
async def get_location_assessment(
    lat: float,
    lng: float
):
    """
    Get environmental safety assessment for a location
    
    Returns:
        LocationResponse with verdict, metrics, and data sources
    """
    try:
        # 1. Get location name (reverse geocoding)
        location_name = await _get_location_name(lat, lng)
        
        # 2. Fetch data from all sources
        raw_data = await data_ingestion.fetch_all_sources(lat, lng)
        
        # 3. Fuse data from multiple sources
        fused_metrics = await data_fusion.fuse_data(raw_data, lat, lng)
        
        # 4. Calculate risk score
        risk_result = risk_scorer.calculate_risk_score(
            metrics=fused_metrics,
            historical_trend=None,  # TODO: Fetch from database
            data_quality=_assess_data_quality(raw_data)
        )
        
        # 5. Detect anomalies
        anomaly_result = anomaly_detector.predict(fused_metrics.get("air", {}))
        
        # 6. Check for plumes (simplified - would need actual detection logic)
        plumes = await _detect_plumes(fused_metrics)
        
        # 7. Extract data timestamps
        data_timestamps = _extract_timestamps(raw_data)
        
        # 8. Build response
        return {
            "location": {
                "lat": lat,
                "lng": lng,
                "name": location_name
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data_timestamp": data_timestamps,
            "verdict": {
                "level": SafetyLevel(risk_result["verdict"]),
                "confidence": risk_result["confidence"],
                "risk_score": risk_result["risk_score"]
            },
            "metrics": fused_metrics,
            "plumes": plumes,
            "sources": _extract_sources(raw_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing location: {str(e)}")

async def _get_location_name(lat: float, lng: float) -> str:
    """Get location name using reverse geocoding"""
    if rg is None:
        return f"Location ({lat:.4f}, {lng:.4f})"
    try:
        result = rg.search((lat, lng))
        if result:
            location = result[0]
            parts = []
            if location.get("name"):
                parts.append(location["name"])
            if location.get("admin1"):  # State/Province
                parts.append(location["admin1"])
            if location.get("cc"):  # Country code
                parts.append(location["cc"])
            return ", ".join(parts) if parts else f"Location ({lat:.4f}, {lng:.4f})"
        return f"Location ({lat:.4f}, {lng:.4f})"
    except Exception:
        return f"Location ({lat:.4f}, {lng:.4f})"

def _assess_data_quality(raw_data: dict) -> dict:
    """Assess data quality metrics"""
    sources = raw_data.get("sources", {})
    
    # Calculate coverage (how many sources provided data)
    total_sources = len(sources)
    valid_sources = sum(1 for s in sources.values() if "error" not in s)
    coverage = valid_sources / total_sources if total_sources > 0 else 0.0
    
    # Calculate data age (hours)
    timestamp_str = raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z")
    try:
        data_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        age_hours = (datetime.utcnow() - data_time.replace(tzinfo=None)).total_seconds() / 3600
    except:
        age_hours = 0
    
    return {
        "coverage": coverage,
        "age_hours": age_hours,
        "valid_sources": valid_sources,
        "total_sources": total_sources
    }

async def _detect_plumes(metrics: dict) -> list:
    """Detect pollution plumes (simplified detection logic)"""
    plumes = []
    
    air = metrics.get("air", {})
    if "so2" in air and air["so2"].get("value"):
        value = air["so2"]["value"]
        # Simple threshold-based detection
        # (Real implementation would use spatial analysis)
        if value > 50:  # Arbitrary threshold - should use proper detection
            plumes.append({
                "detected": True,
                "pollutant": "SO2",
                "intensity": value,
                "source_estimate": None  # Would be filled by plume tracer
            })
    
    return plumes if plumes else [{"detected": False}]

def _extract_timestamps(raw_data: dict) -> dict:
    """Extract timestamps from raw data sources"""
    sources = raw_data.get("sources", {})
    
    timestamps = {}
    
    # Air quality timestamp
    if "openaq" in sources and "timestamp" in sources["openaq"]:
        timestamps["air_quality"] = sources["openaq"]["timestamp"]
    elif "sentinel5p" in sources and "timestamp" in sources["sentinel5p"]:
        timestamps["air_quality"] = sources["sentinel5p"]["timestamp"]
    
    # Other timestamps would be extracted similarly
    # For now, use current time as fallback
    now = datetime.utcnow().isoformat() + "Z"
    timestamps.setdefault("air_quality", now)
    timestamps.setdefault("water_quality", now)
    timestamps.setdefault("land", now)
    timestamps.setdefault("meteorology", now)
    
    return timestamps

def _extract_sources(raw_data: dict) -> dict:
    """Extract data source information"""
    sources = raw_data.get("sources", {})
    
    source_list = []
    
    if "sentinel5p" in sources:
        source_list.append("Sentinel-5P TROPOMI")
    
    if "openaq" in sources and sources["openaq"].get("measurements"):
        source_list.append("OpenAQ")
    
    if "cpcb" in sources:
        source_list.append("CPCB (India)")
    
    return {
        "satellite": "Sentinel-5P TROPOMI" if "sentinel5p" in sources else None,
        "ground_sensors": source_list,
        "weather": "ERA5" if "weather" in sources else None
    }

def _assess_data_quality(raw_data: dict) -> dict:
    """Assess data quality metrics"""
    sources = raw_data.get("sources", {})
    
    # Calculate coverage (how many sources provided data)
    total_sources = len(sources)
    valid_sources = sum(1 for s in sources.values() if "error" not in s)
    coverage = valid_sources / total_sources if total_sources > 0 else 0.0
    
    # Calculate data age (hours)
    timestamp_str = raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z")
    try:
        data_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        age_hours = (datetime.utcnow() - data_time.replace(tzinfo=None)).total_seconds() / 3600
    except:
        age_hours = 0
    
    return {
        "coverage": coverage,
        "age_hours": age_hours,
        "valid_sources": valid_sources,
        "total_sources": total_sources
    }

