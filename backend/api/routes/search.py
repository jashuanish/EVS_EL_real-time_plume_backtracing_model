"""
Search API endpoints
Geocoding and location search
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
import httpx

router = APIRouter()

@router.get("/search")
async def search_location(q: str = Query(..., description="Search query")):
    """
    Search for locations using geocoding
    
    Uses Nominatim (OpenStreetMap) for geocoding
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use Nominatim for geocoding
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": q,
                    "format": "json",
                    "limit": 10,
                    "addressdetails": 1
                },
                headers={
                    "User-Agent": "Environmental Safety Platform"  # Required by Nominatim
                }
            )
            response.raise_for_status()
            
            results = response.json()
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "name": result.get("display_name", ""),
                    "lat": float(result.get("lat", 0)),
                    "lng": float(result.get("lon", 0)),
                    "type": result.get("type", ""),
                    "importance": result.get("importance", 0)
                })
            
            return {"results": formatted_results}
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Geocoding service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching location: {str(e)}")

