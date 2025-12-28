"""
Data Fusion Service
Combines data from multiple sources (satellite, ground sensors, weather)
"""

from typing import Dict
import numpy as np

class DataFusionService:
    """Fuse data from multiple sources with weighted confidence"""
    
    def __init__(self):
        # Source weights (sum to 1.0)
        self.weights = {
            "satellite": 0.4,
            "ground_sensor": 0.5,
            "weather": 0.1
        }
    
    async def fuse_data(self, raw_data: Dict, lat: float, lng: float) -> Dict:
        """
        Fuse data from multiple sources into unified metrics
        
        Args:
            raw_data: Raw data from all sources
            lat: Latitude
            lng: Longitude
        
        Returns:
            Dict with fused metrics (air, water, land)
        """
        sources = raw_data.get("sources", {})
        
        # Fuse air quality data
        air_metrics = self._fuse_air_quality(sources)
        
        # Fuse water quality (placeholder - would process Sentinel-2)
        water_metrics = self._fuse_water_quality(sources)
        
        # Fuse land metrics (placeholder - would process Landsat/Sentinel-2)
        land_metrics = self._fuse_land_metrics(sources)
        
        return {
            "air": air_metrics,
            "water": water_metrics,
            "land": land_metrics
        }
    
    def _fuse_air_quality(self, sources: Dict) -> Dict:
        """Fuse air quality data from satellite and ground sensors"""
        metrics = {}
        
        # Extract ground sensor data (OpenAQ)
        openaq_data = sources.get("openaq", {})
        measurements = openaq_data.get("measurements", [])
        
        # Extract satellite data (Sentinel-5P)
        sentinel_data = sources.get("sentinel5p", {})
        
        # Fuse PM2.5
        pm25_values = []
        pm25_weights = []
        
        # From OpenAQ
        for meas in measurements:
            if meas.get("parameter") == "pm25" and meas.get("value") is not None:
                pm25_values.append(meas["value"])
                pm25_weights.append(self.weights["ground_sensor"])
        
        if pm25_values:
            fused_pm25 = np.average(pm25_values, weights=pm25_weights)
            metrics["pm25"] = {
                "value": float(fused_pm25),
                "unit": "μg/m³",
                "threshold": 45.0,  # WHO 24h guideline
                "source": "OpenAQ"
            }
        
        # Fuse NO2
        no2_values = []
        no2_weights = []
        
        # From OpenAQ
        for meas in measurements:
            if meas.get("parameter") == "no2" and meas.get("value") is not None:
                no2_values.append(meas["value"])
                no2_weights.append(self.weights["ground_sensor"])
        
        # From Sentinel-5P
        if "no2" in sentinel_data and sentinel_data["no2"].get("value"):
            # Convert from mol/m² to μg/m³ (simplified conversion)
            no2_mol = sentinel_data["no2"]["value"]
            no2_ug = no2_mol * 1e6 * 46.01 / 6.022e23 * 1e12  # Rough conversion
            no2_values.append(no2_ug)
            no2_weights.append(self.weights["satellite"])
        
        if no2_values:
            fused_no2 = np.average(no2_values, weights=no2_weights)
            metrics["no2"] = {
                "value": float(fused_no2),
                "unit": "μg/m³",
                "threshold": 200.0,  # WHO 24h guideline
                "source": "Fused (OpenAQ + Sentinel-5P)" if len(no2_values) > 1 else "OpenAQ" if measurements else "Sentinel-5P"
            }
        
        # Fuse SO2
        so2_values = []
        so2_weights = []
        
        # From OpenAQ
        for meas in measurements:
            if meas.get("parameter") == "so2" and meas.get("value") is not None:
                so2_values.append(meas["value"])
                so2_weights.append(self.weights["ground_sensor"])
        
        # From Sentinel-5P
        if "so2" in sentinel_data and sentinel_data["so2"].get("value"):
            so2_mol = sentinel_data["so2"]["value"]
            so2_ug = so2_mol * 1e6 * 64.07 / 6.022e23 * 1e12  # Rough conversion
            so2_values.append(so2_ug)
            so2_weights.append(self.weights["satellite"])
        
        if so2_values:
            fused_so2 = np.average(so2_values, weights=so2_weights)
            metrics["so2"] = {
                "value": float(fused_so2),
                "unit": "μg/m³",
                "threshold": 40.0,  # WHO 24h guideline
                "source": "Fused (OpenAQ + Sentinel-5P)" if len(so2_values) > 1 else "OpenAQ" if measurements else "Sentinel-5P"
            }
        
        return metrics
    
    def _fuse_water_quality(self, sources: Dict) -> Dict:
        """Fuse water quality data (placeholder - would process Sentinel-2)"""
        return {
            "quality_score": 75.0,
            "turbidity": None,
            "status": "Data not available",
            "source": "Placeholder"
        }
    
    def _fuse_land_metrics(self, sources: Dict) -> Dict:
        """Fuse land/deforestation metrics (placeholder - would process Landsat/Sentinel-2)"""
        return {
            "deforestation_risk": 25.0,
            "trend": "stable",
            "source": "Placeholder"
        }
