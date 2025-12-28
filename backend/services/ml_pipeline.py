"""
ML Pipeline: Anomaly Detection, Risk Scoring, Forecasting
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """Detect anomalies in pollution data using Isolation Forest"""
    
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.fitted = False
    
    def fit(self, historical_data: pd.DataFrame):
        """Fit the anomaly detection model on historical data"""
        if len(historical_data) < 10:
            self.fitted = False
            return
        
        # Prepare features: pollution values and temporal features
        features = self._extract_features(historical_data)
        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled)
        self.fitted = True
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for anomaly detection"""
        features_list = []
        
        # Pollution metrics
        for col in ['pm25', 'pm10', 'no2', 'so2', 'o3']:
            if col in df.columns:
                features_list.append(df[col].values)
        
        # Temporal features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            features_list.append(df['hour'].values / 24.0)
            features_list.append(df['day_of_week'].values / 7.0)
        
        if not features_list:
            return np.array([]).reshape(len(df), 0)
        
        return np.column_stack(features_list)
    
    def predict(self, current_data: Dict) -> Dict:
        """
        Predict if current data point is anomalous
        
        Returns:
            Dict with anomaly_score, is_anomaly, and feature contributions
        """
        if not self.fitted:
            return {
                "anomaly_score": 0.0,
                "is_anomaly": False,
                "confidence": 0.0,
                "note": "Model not fitted - insufficient historical data"
            }
        
        # Prepare current data as DataFrame
        df = pd.DataFrame([current_data])
        features = self._extract_features(df)
        
        if features.shape[1] == 0:
            return {
                "anomaly_score": 0.0,
                "is_anomaly": False,
                "confidence": 0.0,
                "note": "No features available"
            }
        
        features_scaled = self.scaler.transform(features)
        anomaly_score = self.model.score_samples(features_scaled)[0]
        is_anomaly = self.model.predict(features_scaled)[0] == -1
        
        return {
            "anomaly_score": float(anomaly_score),
            "is_anomaly": bool(is_anomaly),
            "confidence": abs(anomaly_score),
            "threshold": -0.5  # Typical threshold for Isolation Forest
        }

class RiskScorer:
    """
    Multi-factor risk scoring model
    Combines exposure, duration, sensitivity, and uncertainty
    """
    
    # WHO Air Quality Guidelines (2021)
    WHO_THRESHOLDS = {
        "pm25_annual": 15.0,  # μg/m³
        "pm25_24h": 45.0,    # μg/m³
        "pm10_annual": 45.0,  # μg/m³
        "pm10_24h": 45.0,    # μg/m³
        "no2_annual": 25.0,   # μg/m³
        "no2_24h": 200.0,    # μg/m³
        "so2_24h": 40.0,     # μg/m³
        "o3_8h": 100.0,      # μg/m³
    }
    
    # India-specific thresholds (CPCB)
    CPCB_THRESHOLDS = {
        "pm25_24h": 60.0,    # μg/m³
        "pm10_24h": 100.0,   # μg/m³
        "no2_24h": 80.0,     # μg/m³
        "so2_24h": 80.0,     # μg/m³
        "o3_8h": 180.0,      # μg/m³
    }
    
    def calculate_risk_score(
        self,
        metrics: Dict,
        historical_trend: Optional[List[Dict]] = None,
        data_quality: Dict = None
    ) -> Dict:
        """
        Calculate comprehensive risk score
        
        Args:
            metrics: Current pollution metrics
            historical_trend: Historical data for duration scoring
            data_quality: Data quality indicators (coverage, age, etc.)
        
        Returns:
            Dict with risk_score, exposure_score, duration_score, confidence, verdict
        """
        if data_quality is None:
            data_quality = {"coverage": 1.0, "age_hours": 0}
        
        # 1. Exposure Score (0-100)
        exposure_score = self._calculate_exposure_score(metrics)
        
        # 2. Duration Score (0-100)
        duration_score = self._calculate_duration_score(historical_trend)
        
        # 3. Uncertainty Penalty
        uncertainty_penalty = self._calculate_uncertainty_penalty(data_quality)
        
        # 4. Combined Risk Score
        # Weighted combination: 60% exposure, 30% duration, 10% uncertainty
        risk_score = (
            0.6 * exposure_score +
            0.3 * duration_score +
            0.1 * uncertainty_penalty
        )
        
        # Ensure score is between 0-100
        risk_score = max(0, min(100, risk_score))
        
        # 5. Determine verdict
        if risk_score >= 67:
            verdict = "UNSAFE"
        elif risk_score >= 34:
            verdict = "MODERATE"
        else:
            verdict = "SAFE"
        
        # 6. Calculate confidence (based on data quality)
        confidence = self._calculate_confidence(data_quality, metrics)
        
        return {
            "risk_score": round(risk_score, 1),
            "exposure_score": round(exposure_score, 1),
            "duration_score": round(duration_score, 1),
            "uncertainty_penalty": round(uncertainty_penalty, 1),
            "verdict": verdict,
            "confidence": round(confidence, 1),
            "model_version": "1.0.0"
        }
    
    def _calculate_exposure_score(self, metrics: Dict) -> float:
        """Calculate exposure score based on threshold exceedances"""
        max_exceedance = 0.0
        
        # Air quality metrics
        air = metrics.get("air", {})
        
        # PM2.5
        if "pm25" in air and air["pm25"].get("value") is not None:
            value = air["pm25"]["value"]
            threshold = self.WHO_THRESHOLDS["pm25_24h"]
            exceedance = value / threshold if threshold > 0 else 0
            max_exceedance = max(max_exceedance, exceedance)
        
        # NO2
        if "no2" in air and air["no2"].get("value") is not None:
            value = air["no2"]["value"]
            threshold = self.WHO_THRESHOLDS["no2_24h"]
            exceedance = value / threshold if threshold > 0 else 0
            max_exceedance = max(max_exceedance, exceedance)
        
        # SO2
        if "so2" in air and air["so2"].get("value") is not None:
            value = air["so2"]["value"]
            threshold = self.WHO_THRESHOLDS["so2_24h"]
            exceedance = value / threshold if threshold > 0 else 0
            max_exceedance = max(max_exceedance, exceedance)
        
        # Water quality
        water = metrics.get("water", {})
        if "quality_score" in water:
            score = water["quality_score"]
            # Lower score = higher risk
            water_risk = (100 - score) / 100.0
            max_exceedance = max(max_exceedance, water_risk)
        
        # Convert exceedance factor to score (0-100)
        # exceedance of 1.0 = threshold = score of 50
        # exceedance of 2.0 = 2x threshold = score of 100
        exposure_score = min(100, max_exceedance * 50)
        
        return exposure_score
    
    def _calculate_duration_score(self, historical_trend: Optional[List[Dict]]) -> float:
        """Calculate duration score based on persistence of high exposure"""
        if not historical_trend or len(historical_trend) < 7:
            return 50.0  # Default moderate if no history
        
        # Count days with high exposure in last 30 days
        high_exposure_days = 0
        total_days = min(30, len(historical_trend))
        
        for day_data in historical_trend[-total_days:]:
            # Check if any metric exceeds thresholds
            air = day_data.get("air", {})
            for pollutant, data in air.items():
                if isinstance(data, dict) and "value" in data:
                    value = data["value"]
                    threshold_key = f"{pollutant}_24h"
                    if threshold_key in self.WHO_THRESHOLDS:
                        threshold = self.WHO_THRESHOLDS[threshold_key]
                        if value > threshold:
                            high_exposure_days += 1
                            break
        
        # Score: percentage of days with high exposure
        duration_score = (high_exposure_days / total_days) * 100
        
        return duration_score
    
    def _calculate_uncertainty_penalty(self, data_quality: Dict) -> float:
        """Calculate uncertainty penalty (higher = more uncertainty = higher risk)"""
        penalty = 0.0
        
        # Data age penalty
        age_hours = data_quality.get("age_hours", 0)
        if age_hours > 24:
            penalty += min(20, (age_hours - 24) / 24 * 20)
        
        # Coverage penalty
        coverage = data_quality.get("coverage", 1.0)
        if coverage < 0.5:
            penalty += (1 - coverage) * 30
        
        return min(100, penalty)
    
    def _calculate_confidence(self, data_quality: Dict, metrics: Dict) -> float:
        """Calculate confidence score (0-100)"""
        confidence = 100.0
        
        # Reduce confidence for old data
        age_hours = data_quality.get("age_hours", 0)
        if age_hours > 24:
            confidence -= min(30, (age_hours - 24) / 24 * 30)
        
        # Reduce confidence for sparse data
        coverage = data_quality.get("coverage", 1.0)
        confidence *= coverage
        
        # Reduce confidence if missing critical metrics
        air = metrics.get("air", {})
        if not air or len(air) < 2:
            confidence *= 0.7
        
        return max(0, min(100, confidence))

class PlumeTracer:
    """
    Simplified backward trajectory model for plume source detection
    Uses wind vectors to trace pollution plumes backward in time
    """
    
    async def trace_plume(
        self,
        detection_lat: float,
        detection_lng: float,
        pollutant: str,
        intensity: float,
        wind_data: Dict,
        hours_back: int = 48
    ) -> Dict:
        """
        Trace plume backward to identify likely source
        
        Args:
            detection_lat: Detection point latitude
            detection_lng: Detection point longitude
            pollutant: Pollutant type (SO2, NO2, etc.)
            intensity: Detection intensity
            wind_data: Wind vector data (u, v components)
            hours_back: How many hours to trace back
        
        Returns:
            Dict with source estimate and confidence region
        """
        # Simplified implementation
        # Full implementation would:
        # 1. Get hourly wind vectors for the time period
        # 2. Trace backward using Lagrangian particle model
        # 3. Account for turbulence and dispersion
        # 4. Identify source regions with high probability
        
        # Placeholder: Return detection point as source estimate
        # (In production, this would run actual trajectory model)
        
        return {
            "source_estimate": {
                "lat": detection_lat,
                "lng": detection_lng,
                "confidence_radius_km": 10.0,
                "probability": 0.5
            },
            "trajectory_model": "Lagrangian backward (simplified)",
            "note": "Full plume tracing requires ERA5 wind data integration",
            "hours_traced": hours_back
        }

