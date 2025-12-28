"""
Data Ingestion Service
Fetches real data from various sources: OpenAQ, Sentinel-5P, etc.
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from core.config import settings

class OpenAQService:
    """OpenAQ API client for global ground sensor data"""
    
    BASE_URL = "https://api.openaq.org/v2"
    
    async def get_latest_measurements(
        self,
        lat: float,
        lng: float,
        radius_km: float = 50.0,
        parameters: List[str] = ["pm25", "pm10", "no2", "so2", "o3", "co"]
    ) -> Dict:
        """
        Get latest measurements from OpenAQ stations near a location
        
        Args:
            lat: Latitude
            lng: Longitude
            radius_km: Search radius in kilometers
            parameters: List of pollutants to fetch
        
        Returns:
            Dict with measurements data
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # OpenAQ v2 API - locations endpoint
                params = {
                    "coordinates": f"{lat},{lng}",
                    "radius": int(radius_km * 1000),  # Convert to meters
                    "limit": 100,
                    "order_by": "distance"
                }
                
                response = await client.get(f"{self.BASE_URL}/locations", params=params)
                response.raise_for_status()
                
                locations_data = response.json()
                
                # Get measurements for each location
                measurements = []
                for location in locations_data.get("results", [])[:10]:  # Top 10 closest
                    location_id = location.get("id")
                    if not location_id:
                        continue
                    
                    # Fetch latest measurements
                    for param in parameters:
                        try:
                            meas_response = await client.get(
                                f"{self.BASE_URL}/locations/{location_id}/latest",
                                params={"parameter": param}
                            )
                            if meas_response.status_code == 200:
                                data = meas_response.json()
                                measurements.extend(data.get("results", []))
                        except Exception as e:
                            print(f"Error fetching {param} for location {location_id}: {e}")
                            continue
                
                return {
                    "source": "OpenAQ",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "measurements": measurements,
                    "locations_count": len(locations_data.get("results", []))
                }
                
            except httpx.HTTPError as e:
                print(f"OpenAQ API error: {e}")
                return {
                    "source": "OpenAQ",
                    "error": str(e),
                    "measurements": []
                }
            except Exception as e:
                print(f"Unexpected error in OpenAQ service: {e}")
                return {
                    "source": "OpenAQ",
                    "error": str(e),
                    "measurements": []
                }

class Sentinel5PService:
    """
    Sentinel-5P (TROPOMI) data service
    Uses Google Earth Engine API for satellite data access
    """
    
    def __init__(self):
        self.ee = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Earth Engine (requires credentials)"""
        try:
            import ee
            if not self.initialized:
                # Initialize with credentials if available
                try:
                    ee.Initialize()
                except Exception:
                    # If not initialized, user needs to authenticate
                    print("Warning: Earth Engine not authenticated. Run 'earthengine authenticate'")
                    return False
                self.ee = ee
                self.initialized = True
            return True
        except ImportError:
            print("Warning: earthengine-api not installed")
            return False
    
    async def get_air_quality(
        self,
        lat: float,
        lng: float,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        buffer_km: float = 10.0
    ) -> Dict:
        """
        Get Sentinel-5P air quality data for a location
        
        Args:
            lat: Latitude
            lng: Longitude
            buffer_km: Buffer radius around point (km)
            date_start: Start date (default: 7 days ago)
            date_end: End date (default: today)
        
        Returns:
            Dict with NO2, SO2, CO, CH4, Aerosol Index data
        """
        if not self.initialize():
            return {
                "source": "Sentinel-5P",
                "error": "Earth Engine not initialized",
                "data": {}
            }
        
        try:
            if date_end is None:
                date_end = datetime.utcnow()
            if date_start is None:
                date_start = date_end - timedelta(days=7)
            
            point = self.ee.Geometry.Point([lng, lat])
            region = point.buffer(buffer_km * 1000)  # Convert km to meters
            
            # Get NO2 data
            no2_collection = (
                self.ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2')
                .filterDate(date_start.strftime('%Y-%m-%d'), date_end.strftime('%Y-%m-%d'))
                .filterBounds(region)
                .select('NO2_column_number_density')
            )
            
            # Get SO2 data
            so2_collection = (
                self.ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_SO2')
                .filterDate(date_start.strftime('%Y-%m-%d'), date_end.strftime('%Y-%m-%d'))
                .filterBounds(region)
                .select('SO2_column_number_density')
            )
            
            # Calculate mean values
            no2_mean = no2_collection.mean().reduceRegion(
                reducer=self.ee.Reducer.mean(),
                geometry=region,
                scale=3500  # 3.5km resolution
            ).getInfo()
            
            so2_mean = so2_collection.mean().reduceRegion(
                reducer=self.ee.Reducer.mean(),
                geometry=region,
                scale=7000  # 7km resolution
            ).getInfo()
            
            return {
                "source": "Sentinel-5P TROPOMI",
                "timestamp": date_end.isoformat() + "Z",
                "data_start": date_start.isoformat() + "Z",
                "data_end": date_end.isoformat() + "Z",
                "location": {"lat": lat, "lng": lng},
                "no2": {
                    "value": no2_mean.get("NO2_column_number_density", None),
                    "unit": "mol/m²",
                    "spatial_resolution_km": 3.5
                },
                "so2": {
                    "value": so2_mean.get("SO2_column_number_density", None),
                    "unit": "mol/m²",
                    "spatial_resolution_km": 7.0
                },
                "product": "OFFL L3"
            }
            
        except Exception as e:
            print(f"Sentinel-5P processing error: {e}")
            return {
                "source": "Sentinel-5P",
                "error": str(e),
                "data": {}
            }

class CPCBService:
    """
    Central Pollution Control Board (India) data service
    Note: CPCB API may require authentication or web scraping
    """
    
    BASE_URL = "https://app.cpcbccr.com"
    
    async def get_station_data(
        self,
        lat: float,
        lng: float,
        state: Optional[str] = "Karnataka"
    ) -> Dict:
        """
        Get CPCB station data (India-specific)
        Note: This is a placeholder - actual implementation may require
        web scraping or official API access
        """
        # TODO: Implement actual CPCB API integration
        # This may require:
        # - Web scraping from CPCB dashboard
        # - Official API access (if available)
        # - Alternative: Use OpenAQ data for India stations
        
        return {
            "source": "CPCB",
            "note": "CPCB integration requires implementation",
            "fallback": "Using OpenAQ data for India stations",
            "data": {}
        }

class WeatherService:
    """Weather data service (ERA5 or alternative)"""
    
    async def get_wind_data(
        self,
        lat: float,
        lng: float,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Get wind vector data for plume tracing
        For now, returns placeholder structure
        TODO: Integrate with ERA5 CDS API or alternative
        """
        # Placeholder - actual implementation would fetch from ERA5/CDS
        return {
            "source": "ERA5",
            "note": "ERA5 integration requires CDS API access",
            "wind_u": None,  # u-component (m/s)
            "wind_v": None,  # v-component (m/s)
            "timestamp": (timestamp or datetime.utcnow()).isoformat() + "Z"
        }

class DataIngestionService:
    """Main data ingestion service that coordinates all sources"""
    
    def __init__(self):
        self.openaq = OpenAQService()
        self.sentinel5p = Sentinel5PService()
        self.cpcb = CPCBService()
        self.weather = WeatherService()
    
    async def fetch_all_sources(
        self,
        lat: float,
        lng: float,
        include_satellite: bool = True,
        include_ground: bool = True,
        include_weather: bool = True
    ) -> Dict:
        """
        Fetch data from all available sources for a location
        
        Returns:
            Dict with data from all sources
        """
        tasks = []
        
        if include_ground:
            tasks.append(("openaq", self.openaq.get_latest_measurements(lat, lng)))
        
        if include_satellite:
            tasks.append(("sentinel5p", self.sentinel5p.get_air_quality(lat, lng)))
        
        if include_weather:
            tasks.append(("weather", self.weather.get_wind_data(lat, lng)))
        
        # Fetch data concurrently
        results = {}
        for source_name, coro in tasks:
            try:
                results[source_name] = await coro
            except Exception as e:
                results[source_name] = {"error": str(e), "source": source_name}
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "location": {"lat": lat, "lng": lng},
            "sources": results
        }

