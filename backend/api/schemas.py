"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SafetyLevel(str, Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    UNSAFE = "UNSAFE"

class PollutantType(str, Enum):
    PM25 = "pm25"
    PM10 = "pm10"
    NO2 = "no2"
    SO2 = "so2"
    CO = "co"
    O3 = "o3"
    CH4 = "ch4"

class MetricValue(BaseModel):
    value: float
    unit: str
    threshold: Optional[float] = None
    source: str
    timestamp: datetime
    uncertainty: Optional[Dict[str, Any]] = None

class DataTimestamp(BaseModel):
    air_quality: Optional[datetime] = None
    water_quality: Optional[datetime] = None
    land: Optional[datetime] = None
    meteorology: Optional[datetime] = None

class Verdict(BaseModel):
    level: SafetyLevel
    confidence: float = Field(..., ge=0, le=100)
    risk_score: float = Field(..., ge=0, le=100)

class PlumeDetection(BaseModel):
    detected: bool
    pollutant: Optional[str] = None
    intensity: Optional[float] = None
    source_estimate: Optional[Dict[str, Any]] = None

class LocationResponse(BaseModel):
    location: Dict[str, Any]
    timestamp: datetime
    data_timestamp: DataTimestamp
    verdict: Verdict
    metrics: Dict[str, Any]
    plumes: List[PlumeDetection]
    sources: Dict[str, Any]

class HumanReadableReason(BaseModel):
    summary: str
    reasons: List[str]
    recommendations: List[str]

class TechnicalMetric(BaseModel):
    raw_value: float
    unit: str
    threshold: Dict[str, Any]
    exceedance_factor: Optional[float] = None
    data_source: str
    measurement_timestamp: datetime
    uncertainty: Optional[Dict[str, Any]] = None
    spatial_coverage: Optional[str] = None
    spatial_resolution_km: Optional[float] = None

class AnalysisResponse(BaseModel):
    human_readable: HumanReadableReason
    technical: Dict[str, Any]
    model_info: Dict[str, Any]

class ForecastPoint(BaseModel):
    timestamp: datetime
    metrics: Dict[str, PollutantType]
    confidence: float

class ForecastResponse(BaseModel):
    location: List[float]
    forecast_type: str
    horizon_hours: int
    generated_at: datetime
    predictions: List[ForecastPoint]
    model_info: Dict[str, Any]

