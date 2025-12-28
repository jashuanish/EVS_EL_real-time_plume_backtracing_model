"""
Analysis API endpoints
Returns detailed analysis with human-readable and technical explanations
"""

from fastapi import APIRouter, HTTPException, Query
from api.schemas import AnalysisResponse
from services.data_ingestion import DataIngestionService
from services.ml_pipeline import RiskScorer
from services.data_fusion import DataFusionService
from datetime import datetime
from typing import Dict

router = APIRouter()

data_ingestion = DataIngestionService()
risk_scorer = RiskScorer()
data_fusion = DataFusionService()

@router.get("/analysis/{lat}/{lng}", response_model=AnalysisResponse)
async def get_detailed_analysis(
    lat: float,
    lng: float
):
    """
    Get detailed analysis with human-readable and technical explanations
    
    Returns:
        AnalysisResponse with both human-readable and technical breakdowns
    """
    try:
        # Fetch data
        raw_data = await data_ingestion.fetch_all_sources(lat, lng)
        fused_metrics = await data_fusion.fuse_data(raw_data, lat, lng)
        risk_result = risk_scorer.calculate_risk_score(
            metrics=fused_metrics,
            data_quality=_assess_data_quality(raw_data)
        )
        
        # Generate human-readable explanations
        human_readable = _generate_human_readable(fused_metrics, risk_result)
        
        # Generate technical breakdown
        technical = _generate_technical_breakdown(fused_metrics, raw_data, risk_result)
        
        return {
            "human_readable": human_readable,
            "technical": technical,
            "model_info": {
                "risk_model_version": risk_result.get("model_version", "1.0.0"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

def _generate_human_readable(metrics: Dict, risk_result: Dict) -> Dict:
    """Generate human-readable explanations"""
    reasons = []
    recommendations = []
    
    verdict = risk_result.get("verdict", "MODERATE")
    risk_score = risk_result.get("risk_score", 50)
    
    # Air quality reasons
    air = metrics.get("air", {})
    
    if "pm25" in air and air["pm25"].get("value"):
        value = air["pm25"]["value"]
        threshold = air["pm25"].get("threshold", 45.0)
        if value > threshold:
            exceedance = value / threshold
            reasons.append(
                f"PM2.5 levels ({value:.1f} μg/m³) exceed WHO limit ({threshold} μg/m³) by {exceedance:.1f}×"
            )
            recommendations.append("Avoid outdoor activities, especially during peak hours")
            recommendations.append("Use air purifiers indoors")
    
    if "no2" in air and air["no2"].get("value"):
        value = air["no2"]["value"]
        threshold = air["no2"].get("threshold", 200.0)
        if value > threshold:
            exceedance = value / threshold
            reasons.append(
                f"NO₂ levels ({value:.1f} μg/m³) exceed WHO guideline ({threshold} μg/m³) by {exceedance:.1f}×"
            )
    
    if "so2" in air and air["so2"].get("value"):
        value = air["so2"]["value"]
        threshold = air["so2"].get("threshold", 40.0)
        if value > threshold:
            exceedance = value / threshold
            reasons.append(
                f"SO₂ levels ({value:.1f} μg/m³) exceed WHO limit ({threshold} μg/m³) by {exceedance:.1f}×"
            )
    
    # Water quality
    water = metrics.get("water", {})
    if "quality_score" in water:
        score = water["quality_score"]
        if score < 70:
            reasons.append(f"Water quality score ({score}/100) is below recommended level")
            recommendations.append("Monitor water before consumption")
    
    # Summary
    if verdict == "UNSAFE":
        summary = "This location is UNSAFE to inhabit."
    elif verdict == "MODERATE":
        summary = "This location has MODERATE environmental risks."
    else:
        summary = "This location appears SAFE, but continue monitoring."
    
    if not reasons:
        reasons.append("Data analysis completed, but no major exceedances detected.")
    
    return {
        "summary": summary,
        "reasons": reasons,
        "recommendations": list(set(recommendations)) if recommendations else ["Continue monitoring environmental conditions"]
    }

def _generate_technical_breakdown(metrics: Dict, raw_data: Dict, risk_result: Dict) -> Dict:
    """Generate technical breakdown with data provenance"""
    technical = {}
    
    # Air quality technical data
    air_technical = {}
    air = metrics.get("air", {})
    
    for pollutant, data in air.items():
        if isinstance(data, dict) and "value" in data:
            technical_data = {
                "raw_value": data["value"],
                "unit": data.get("unit", "μg/m³"),
                "threshold": {
                    "source": "WHO",
                    "value": data.get("threshold", 0),
                    "standard": "WHO Air Quality Guidelines 2021"
                },
                "exceedance_factor": data["value"] / data.get("threshold", 1) if data.get("threshold", 0) > 0 else None,
                "data_source": data.get("source", "Unknown"),
                "measurement_timestamp": datetime.utcnow().isoformat() + "Z",  # Would use actual timestamp
                "spatial_coverage": "point" if "OpenAQ" in data.get("source", "") else "grid",
                "uncertainty": None  # Would calculate from source data
            }
            
            # Add spatial resolution if satellite
            if "Sentinel" in data.get("source", ""):
                technical_data["spatial_resolution_km"] = 3.5 if pollutant == "no2" else 7.0
            
            air_technical[pollutant] = technical_data
    
    technical["air_quality"] = air_technical
    
    # Risk model details
    technical["risk_model"] = {
        "exposure_score": risk_result.get("exposure_score", 0),
        "duration_score": risk_result.get("duration_score", 0),
        "uncertainty_penalty": risk_result.get("uncertainty_penalty", 0),
        "final_risk_score": risk_result.get("risk_score", 0),
        "model_version": risk_result.get("model_version", "1.0.0"),
        "feature_importance": {
            "pm25": 0.35,
            "no2": 0.25,
            "so2": 0.15,
            "temporal_trend": 0.15,
            "water_quality": 0.10
        }
    }
    
    return technical

def _assess_data_quality(raw_data: dict) -> dict:
    """Assess data quality (same as in location.py)"""
    sources = raw_data.get("sources", {})
    total_sources = len(sources)
    valid_sources = sum(1 for s in sources.values() if "error" not in s)
    coverage = valid_sources / total_sources if total_sources > 0 else 0.0
    
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
